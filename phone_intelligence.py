import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
import json
from datetime import datetime
import logging
from config import Config
import random

class PhoneIntelligence:
    """Core phone number intelligence and analysis engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_phone_number(self, phone_input):
        """
        Comprehensive phone number analysis
        
        Args:
            phone_input (str): Phone number in any format
            
        Returns:
            dict: Analysis results
        """
        try:
            # Parse and validate phone number
            parsed_number = self._parse_phone_number(phone_input)
            if not parsed_number:
                return {'error': 'Invalid phone number format'}
            
            # Basic information extraction
            basic_info = self._extract_basic_info(parsed_number)
            
            # Carrier information
            carrier_info = self._get_carrier_info(parsed_number)
            
            # Security analysis
            security_analysis = self._perform_security_analysis(parsed_number, phone_input)
            
            # OSINT enrichment
            osint_data = self._perform_osint_enrichment(parsed_number, phone_input)
            
            # Technical details
            technical_details = self._extract_technical_details(parsed_number)
            
            # Network intelligence
            network_intelligence = self._get_network_intelligence(parsed_number, phone_input)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(security_analysis, osint_data)
            
            # Compile results
            results = {
                'timestamp': datetime.now().isoformat(),
                'input_number': phone_input,
                'risk_score': risk_score,
                **basic_info,
                'carrier_info': carrier_info,
                'security_analysis': security_analysis,
                'osint_data': osint_data,
                'technical_details': technical_details,
                'network_intelligence': network_intelligence
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Analysis error: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _parse_phone_number(self, phone_input):
        """Parse and validate phone number"""
        try:
            # Try parsing with different region hints
            regions_to_try = ['US', 'GB', 'CA', 'AU', None]
            
            for region in regions_to_try:
                try:
                    parsed = phonenumbers.parse(phone_input, region)
                    if phonenumbers.is_valid_number(parsed):
                        return parsed
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Phone parsing error: {str(e)}")
            return None
    
    def _extract_basic_info(self, parsed_number):
        """Extract basic geographic and carrier information"""
        try:
            country = geocoder.description_for_number(parsed_number, "en")
            region = geocoder.description_for_number(parsed_number, "en")
            carrier_name = carrier.name_for_number(parsed_number, "en")
            
            # Get timezone information
            timezones = timezone.time_zones_for_number(parsed_number)
            timezone_str = list(timezones)[0] if timezones else "Unknown"
            
            # Determine line type
            number_type = phonenumbers.number_type(parsed_number)
            line_type = self._get_line_type_description(number_type)
            
            return {
                'country': country or "Unknown",
                'region': region or "Unknown",
                'carrier': carrier_name or "Unknown",
                'line_type': line_type,
                'timezone': timezone_str,
                'country_code': parsed_number.country_code
            }
            
        except Exception as e:
            self.logger.error(f"Basic info extraction error: {str(e)}")
            return {}
    
    def _get_line_type_description(self, number_type):
        """Convert number type enum to human-readable description"""
        type_map = {
            phonenumbers.PhoneNumberType.MOBILE: "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE: "Landline",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
            phonenumbers.PhoneNumberType.VOIP: "VoIP",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            phonenumbers.PhoneNumberType.PAGER: "Pager",
            phonenumbers.PhoneNumberType.UAN: "Universal Access Number",
            phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail"
        }
        return type_map.get(number_type, "Unknown")
    
    def _get_carrier_info(self, parsed_number):
        """Get detailed carrier information"""
        try:
            carrier_name = carrier.name_for_number(parsed_number, "en")
            number_type = phonenumbers.number_type(parsed_number)
            
            carrier_info = {
                'name': carrier_name or "Unknown",
                'type': self._get_line_type_description(number_type),
                'country': geocoder.description_for_number(parsed_number, "en"),
                'mobile_country_code': str(parsed_number.country_code),
                'mobile_network_code': "Unknown"  # Would need additional API for MNC
            }
            
            # Try to get additional carrier info from Numverify API
            if Config.NUMVERIFY_API_KEY:
                numverify_data = self._query_numverify_api(parsed_number)
                if numverify_data:
                    carrier_info.update(numverify_data)
            
            return carrier_info
            
        except Exception as e:
            self.logger.error(f"Carrier info error: {str(e)}")
            return {}
    
    def _perform_security_analysis(self, parsed_number, phone_input):
        """Perform security-related analysis"""
        try:
            analysis = {
                'is_spam_risk': False,
                'is_voip': False,
                'reputation_score': 50,  # Default neutral score
                'risk_indicators': []
            }
            
            # Check if it's a VoIP number
            number_type = phonenumbers.number_type(parsed_number)
            if number_type == phonenumbers.PhoneNumberType.VOIP:
                analysis['is_voip'] = True
                analysis['risk_indicators'].append("VoIP number")
            
            # Try Twilio Lookup API for additional security data
            if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
                twilio_data = self._query_twilio_lookup(parsed_number)
                if twilio_data:
                    analysis.update(twilio_data)
            
            # Check against known spam databases (placeholder)
            spam_check = self._check_spam_databases(phone_input)
            if spam_check:
                analysis['is_spam_risk'] = True
                analysis['risk_indicators'].append("Found in spam database")
                analysis['reputation_score'] = max(0, analysis['reputation_score'] - 30)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Security analysis error: {str(e)}")
            return {}
    
    def _perform_osint_enrichment(self, parsed_number, phone_input):
        """Perform OSINT data enrichment"""
        try:
            osint_data = {
                'breach_data': [],
                'social_media_presence': {},
                'additional_intel': {},
                'network_intelligence': self._get_network_intelligence(parsed_number, phone_input),
                'digital_footprint': self._get_digital_footprint(phone_input),
                'associated_emails': self._find_associated_emails(phone_input),
                'websites': self._find_associated_websites(phone_input),
                'social_accounts': self._find_social_media_accounts(phone_input)
            }
            
            # Check HaveIBeenPwned for associated breaches
            if Config.HIBP_API_KEY:
                breach_data = self._check_hibp_breaches(phone_input)
                if breach_data:
                    osint_data['breach_data'] = breach_data
            
            # Placeholder for social media lookup
            # In a real implementation, you would integrate with appropriate APIs
            social_data = self._check_social_media_presence(phone_input)
            if social_data:
                osint_data['social_media_presence'] = social_data
            
            return osint_data
            
        except Exception as e:
            self.logger.error(f"OSINT enrichment error: {str(e)}")
            return {}
    
    def _extract_technical_details(self, parsed_number):
        """Extract technical phone number details"""
        try:
            return {
                'international_format': phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                ),
                'national_format': phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
                ),
                'e164_format': phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.E164
                ),
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number,
                'number_type': self._get_line_type_description(
                    phonenumbers.number_type(parsed_number)
                )
            }
            
        except Exception as e:
            self.logger.error(f"Technical details error: {str(e)}")
            return {}
    
    def _calculate_risk_score(self, security_analysis, osint_data):
        """Calculate overall risk score (0-100)"""
        try:
            base_score = 20  # Base risk score
            
            # Add risk based on security indicators
            if security_analysis.get('is_spam_risk'):
                base_score += 40
            
            if security_analysis.get('is_voip'):
                base_score += 20
            
            # Add risk based on breach data
            if osint_data.get('breach_data'):
                base_score += 30
            
            # Adjust based on reputation score
            reputation = security_analysis.get('reputation_score', 50)
            if reputation < 30:
                base_score += 20
            elif reputation > 70:
                base_score = max(0, base_score - 10)
            
            return min(100, base_score)
            
        except Exception as e:
            self.logger.error(f"Risk calculation error: {str(e)}")
            return 50
    
    def _query_numverify_api(self, parsed_number):
        """Query Numverify API for additional carrier information"""
        try:
            if not Config.NUMVERIFY_API_KEY:
                return None
            
            phone_str = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
            
            url = f"http://apilayer.net/api/validate"
            params = {
                'access_key': Config.NUMVERIFY_API_KEY,
                'number': phone_str,
                'country_code': '',
                'format': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    return {
                        'carrier': data.get('carrier', 'Unknown'),
                        'line_type': data.get('line_type', 'Unknown'),
                        'location': data.get('location', 'Unknown')
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Numverify API error: {str(e)}")
            return None
    
    def _query_twilio_lookup(self, parsed_number):
        """Query Twilio Lookup API for security information"""
        try:
            if not (Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN):
                return None
            
            # Placeholder for Twilio Lookup API integration
            # In a real implementation, you would use the Twilio SDK
            return {
                'reputation_score': 60,  # Placeholder
                'spam_risk': False
            }
            
        except Exception as e:
            self.logger.error(f"Twilio lookup error: {str(e)}")
            return None
    
    def _check_spam_databases(self, phone_input):
        """Check phone number against spam databases"""
        try:
            # Placeholder for spam database checks
            # In a real implementation, you would integrate with spam databases
            return False
            
        except Exception as e:
            self.logger.error(f"Spam check error: {str(e)}")
            return False
    
    def _check_hibp_breaches(self, phone_input):
        """Check HaveIBeenPwned for associated breaches"""
        try:
            if not Config.HIBP_API_KEY:
                return []
            
            # Placeholder for HIBP API integration
            # Note: HIBP doesn't directly support phone number lookups
            # This would require finding associated email addresses first
            return []
            
        except Exception as e:
            self.logger.error(f"HIBP check error: {str(e)}")
            return []
    
    def _check_social_media_presence(self, phone_input):
        """Check for social media presence (placeholder)"""
        try:
            # Placeholder for social media lookup
            # In a real implementation, you would need to comply with
            # each platform's terms of service and API usage policies
            return {}
            
        except Exception as e:
            self.logger.error(f"Social media check error: {str(e)}")
            return {}
    
    def _get_network_intelligence(self, parsed_number, phone_input):
        """Gather network intelligence and attempt real IP detection"""
        try:
            network_data = {
                'carrier_network_info': {},
                'potential_ip_ranges': [],
                'network_status': 'Offline',  # Default to offline
                'online_indicators': [],
                'network_security': {},
                'real_time_ip': None,  # Added real-time IP field
                'connection_status': 'Unknown',  # Added connection status
                'last_seen': None  # Added last seen timestamp
            }
            
            # Get carrier network information
            carrier_network = self._get_carrier_network_info(parsed_number)
            if carrier_network:
                network_data['carrier_network_info'] = carrier_network
            
            # Attempt to find associated IP ranges for the carrier
            ip_ranges = self._get_carrier_ip_ranges(parsed_number)
            if ip_ranges:
                network_data['potential_ip_ranges'] = ip_ranges
            
            online_status = self._detect_online_status(phone_input, parsed_number)
            if online_status:
                network_data.update(online_status)
            
            # Network security assessment
            network_security = self._assess_network_security(parsed_number)
            if network_security:
                network_data['network_security'] = network_security
            
            return network_data
            
        except Exception as e:
            self.logger.error(f"Network intelligence error: {str(e)}")
            return {}
    

    def _detect_online_status(self, phone_input, parsed_number):
        """Enhanced online status detection with real-time monitoring capabilities"""
        try:
            online_status = {
                'network_status': 'Unknown',
                'connection_status': 'Unknown',
                'last_seen': None,
                'online_indicators': [],
                'real_time_ip': None,
                'connection_quality': 'Unknown',
                'device_activity': {},
                'network_changes': []
            }
            
            
            # Method 1: Check messaging app status (WhatsApp, Telegram, etc.)
            messaging_status = self._check_messaging_app_status(phone_input)
            if messaging_status:
                online_status.update(messaging_status)
            
            # Method 2: Social media activity detection
            social_activity = self._check_recent_social_activity(phone_input)
            if social_activity:
                online_status['device_activity']['social_media'] = social_activity
                if social_activity.get('recent_activity'):
                    online_status['network_status'] = 'Recently Online'
                    online_status['last_seen'] = social_activity.get('last_activity_time')
            
            # Method 3: Network carrier status (if available)
            carrier_status = self._check_carrier_network_status(parsed_number)
            if carrier_status:
                online_status.update(carrier_status)
            
            # Method 4: VoIP service detection
            voip_status = self._check_voip_services(phone_input)
            if voip_status:
                online_status['device_activity']['voip'] = voip_status
                if voip_status.get('active'):
                    online_status['online_indicators'].append('VoIP service active')
            
            # Method 5: Business listing activity
            business_activity = self._check_business_activity(phone_input)
            if business_activity:
                online_status['device_activity']['business'] = business_activity
            
            # Method 6: Real-time network probing (ethical methods only)
            network_probe = self._perform_network_probe(parsed_number)
            if network_probe:
                online_status.update(network_probe)
            
            # Determine overall status based on collected data
            online_status['network_status'] = self._determine_overall_status(online_status)
            
            # Add timestamp
            online_status['check_timestamp'] = datetime.now().isoformat()
            
            return online_status
            
        except Exception as e:
            self.logger.error(f"Online status detection error: {str(e)}")
            return {
                'network_status': 'Error',
                'connection_status': 'Unknown',
                'error': str(e)
            }
    
    def _check_messaging_app_status(self, phone_input):
        """Check messaging app online status"""
        try:
            messaging_status = {
                'whatsapp': self._check_whatsapp_status(phone_input),
                'telegram': self._check_telegram_status(phone_input),
                'signal': self._check_signal_status(phone_input),
                'viber': self._check_viber_status(phone_input)
            }
            
            # Determine if any messaging app shows online status
            online_apps = []
            for app, status in messaging_status.items():
                if status and status.get('online'):
                    online_apps.append(app)
            
            if online_apps:
                return {
                    'connection_status': 'Online via messaging',
                    'online_indicators': [f'{app} active' for app in online_apps],
                    'messaging_apps': messaging_status
                }
            
            return {'messaging_apps': messaging_status}
            
        except Exception as e:
            self.logger.error(f"Messaging app status error: {str(e)}")
            return {}
    
    def _check_whatsapp_status(self, phone_input):
        """Check WhatsApp online status (ethical methods only)"""
        try:
            # This would use WhatsApp Business API or public business profiles
            # Note: Personal WhatsApp status checking would violate privacy
            return {
                'registered': False,  # Placeholder
                'business_account': False,
                'last_seen': None,
                'online': False
            }
        except:
            return {}
    
    def _check_telegram_status(self, phone_input):
        """Check Telegram status for public profiles"""
        try:
            # Only check public Telegram profiles/channels
            return {
                'public_profile': False,
                'username': None,
                'last_seen': None,
                'online': False
            }
        except:
            return {}
    
    def _check_signal_status(self, phone_input):
        """Check Signal status (very limited due to privacy focus)"""
        try:
            # Signal prioritizes privacy, very limited public information
            return {
                'registered': False,
                'online': False
            }
        except:
            return {}
    
    def _check_viber_status(self, phone_input):
        """Check Viber public account status"""
        try:
            # Check for Viber public accounts/business profiles
            return {
                'public_account': False,
                'business_profile': False,
                'online': False
            }
        except:
            return {}
    
    def _check_recent_social_activity(self, phone_input):
        """Check for recent social media activity"""
        try:
            # This would check public social media posts/activity
            # Only public information that's already accessible
            
            activity_data = {
                'recent_activity': False,
                'last_activity_time': None,
                'platforms_active': [],
                'activity_score': 0
            }
            
            # Check various platforms for recent public activity
            platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok']
            
            for platform in platforms:
                platform_activity = self._check_platform_activity(phone_input, platform)
                if platform_activity and platform_activity.get('recent'):
                    activity_data['platforms_active'].append(platform)
                    activity_data['recent_activity'] = True
                    activity_data['activity_score'] += 1
                    
                    # Update last activity time if more recent
                    if platform_activity.get('timestamp'):
                        if not activity_data['last_activity_time'] or platform_activity['timestamp'] > activity_data['last_activity_time']:
                            activity_data['last_activity_time'] = platform_activity['timestamp']
            
            return activity_data
            
        except Exception as e:
            self.logger.error(f"Social activity check error: {str(e)}")
            return {}
    
    def _check_platform_activity(self, phone_input, platform):
        """Check activity on a specific platform"""
        try:
            # This would use platform APIs to check for recent public activity
            # Placeholder implementation
            return {
                'recent': False,
                'timestamp': None,
                'activity_type': None
            }
        except:
            return {}
    
    def _check_carrier_network_status(self, parsed_number):
        """Check carrier network status"""
        try:
            carrier_name = carrier.name_for_number(parsed_number, "en")
            
            # This would integrate with carrier APIs (where available)
            # Most carriers don't provide real-time status for privacy reasons
            
            return {
                'carrier_status': 'Unknown',
                'network_available': True,  # Assume network is available
                'roaming_status': 'Unknown'
            }
            
        except Exception as e:
            self.logger.error(f"Carrier status check error: {str(e)}")
            return {}
    
    def _check_voip_services(self, phone_input):
        """Check VoIP service activity"""
        try:
            voip_data = {
                'skype': self._check_skype_status(phone_input),
                'google_voice': self._check_google_voice_status(phone_input),
                'discord': self._check_discord_voice_status(phone_input),
                'zoom': self._check_zoom_status(phone_input),
                'active': False
            }
            
            # Check if any VoIP service is active
            for service, status in voip_data.items():
                if service != 'active' and status and status.get('online'):
                    voip_data['active'] = True
                    break
            
            return voip_data
            
        except Exception as e:
            self.logger.error(f"VoIP services check error: {str(e)}")
            return {}
    
    def _check_skype_status(self, phone_input):
        """Check Skype status"""
        try:
            # Check for public Skype profiles
            return {'online': False, 'username': None}
        except:
            return {}
    
    def _check_google_voice_status(self, phone_input):
        """Check Google Voice status"""
        try:
            # Limited public information available
            return {'active': False}
        except:
            return {}
    
    def _check_discord_voice_status(self, phone_input):
        """Check Discord voice activity"""
        try:
            # Check for public Discord servers/activity
            return {'online': False, 'servers': []}
        except:
            return {}
    
    def _check_zoom_status(self, phone_input):
        """Check Zoom meeting activity"""
        try:
            # Check for public Zoom webinars/meetings
            return {'in_meeting': False, 'public_meetings': []}
        except:
            return {}
    
    def _check_business_activity(self, phone_input):
        """Check business-related activity"""
        try:
            business_data = {
                'google_my_business': self._check_google_business(phone_input),
                'yelp_activity': self._check_yelp_activity(phone_input),
                'website_activity': self._check_website_activity(phone_input),
                'recent_reviews': self._check_recent_reviews(phone_input)
            }
            
            return business_data
            
        except Exception as e:
            self.logger.error(f"Business activity check error: {str(e)}")
            return {}
    
    def _check_google_business(self, phone_input):
        """Check Google My Business activity"""
        try:
            # Check for Google My Business listings and recent updates
            return {'listed': False, 'recent_updates': False}
        except:
            return {}
    
    def _check_yelp_activity(self, phone_input):
        """Check Yelp business activity"""
        try:
            # Check for Yelp business profiles and recent activity
            return {'business_profile': False, 'recent_activity': False}
        except:
            return {}
    
    def _check_website_activity(self, phone_input):
        """Check website activity for businesses"""
        try:
            # Check if business websites are active/updated
            return {'websites_found': [], 'recent_updates': False}
        except:
            return {}
    
    def _check_recent_reviews(self, phone_input):
        """Check for recent business reviews"""
        try:
            # Check various review platforms for recent reviews
            return {'recent_reviews': False, 'platforms': []}
        except:
            return {}
    
    def _perform_network_probe(self, parsed_number):
        """Perform ethical network probing"""
        try:
            # Only use ethical, legal methods for network detection
            probe_data = {
                'ping_response': False,
                'port_scan_results': {},
                'network_latency': None,
                'connection_quality': 'Unknown'
            }
            
            # Note: Actual network probing should only be done with proper authorization
            # This is a placeholder for demonstration
            
            return probe_data
            
        except Exception as e:
            self.logger.error(f"Network probe error: {str(e)}")
            return {}
    
    def _determine_overall_status(self, status_data):
        """Determine overall online status from collected data"""
        try:
            online_indicators = status_data.get('online_indicators', [])
            
            if len(online_indicators) >= 2:
                return 'Online'
            elif len(online_indicators) == 1:
                return 'Recently Online'
            elif status_data.get('messaging_apps'):
                # Check if any messaging app shows activity
                for app_data in status_data['messaging_apps'].values():
                    if app_data and app_data.get('online'):
                        return 'Online via messaging'
            
            return 'Offline'
            
        except:
            return 'Unknown'

    def _check_social_media_activity(self, phone_input):
        """Check for social media activity associated with phone number"""
        try:
            # This would check publicly available social media profiles
            # that are linked to phone numbers (with proper permissions)
            
            # Placeholder implementation for demonstration
            # In reality, this would use legitimate social media APIs
            
            return False  # No social media activity detected
            
        except Exception as e:
            self.logger.error(f"Social media activity check error: {str(e)}")
            return False

    
    def _check_carrier_public_status(self, carrier_name, country_code):
        """Check carrier public status APIs"""
        # Placeholder implementation
        return None
    
    def _get_carrier_network_info(self, parsed_number):
        """Get detailed carrier network information"""
        try:
            carrier_name = carrier.name_for_number(parsed_number, "en")
            country = geocoder.description_for_number(parsed_number, "en")
            number_type = phonenumbers.number_type(parsed_number)
            
            network_info = {
                'carrier_name': carrier_name or "Unknown",
                'network_type': self._get_line_type_description(number_type),
                'country': country or "Unknown",
                'mcc': str(parsed_number.country_code),  # Mobile Country Code
                'mnc': "Unknown",  # Mobile Network Code - would need additional API
                'network_technology': self._detect_network_technology(parsed_number),
                'roaming_partners': self._get_roaming_partners(carrier_name),
                'network_coverage': self._get_network_coverage(carrier_name, country)
            }
            
            return network_info
            
        except Exception as e:
            self.logger.error(f"Carrier network info error: {str(e)}")
            return {}
    
    def _get_carrier_ip_ranges(self, parsed_number):
        """Get potential IP ranges for the carrier"""
        try:
            carrier_name = carrier.name_for_number(parsed_number, "en")
            country = geocoder.description_for_number(parsed_number, "en")
            
            # This would use public IP allocation databases
            ip_ranges = []
            
            # Example IP ranges for major carriers (publicly available information)
            carrier_ip_map = {
                'Verizon': ['74.192.0.0/10', '108.160.0.0/11'],
                'AT&T': ['12.0.0.0/8', '135.0.0.0/8'],
                'T-Mobile': ['208.54.0.0/16', '66.94.0.0/16'],
                'Sprint': ['72.52.0.0/15', '173.199.0.0/16']
            }
            
            if carrier_name in carrier_ip_map:
                ip_ranges = carrier_ip_map[carrier_name]
            else:
                # Generic mobile carrier ranges by country
                country_ranges = self._get_country_mobile_ranges(country)
                if country_ranges:
                    ip_ranges = country_ranges
            
            return ip_ranges
            
        except Exception as e:
            self.logger.error(f"Carrier IP ranges error: {str(e)}")
            return []
    
    def _assess_network_security(self, parsed_number):
        """Assess network security characteristics"""
        try:
            security_assessment = {
                'encryption_support': 'Unknown',
                'network_security_level': 'Standard',
                'vulnerability_indicators': [],
                'security_score': 50,  # Default neutral score
                'security_features': []
            }
            
            number_type = phonenumbers.number_type(parsed_number)
            carrier_name = carrier.name_for_number(parsed_number, "en")
            
            # Assess based on line type
            if number_type == phonenumbers.PhoneNumberType.VOIP:
                security_assessment['vulnerability_indicators'].append('VoIP - potential for spoofing')
                security_assessment['security_score'] -= 10
            elif number_type == phonenumbers.PhoneNumberType.MOBILE:
                security_assessment['security_features'].append('Mobile network encryption')
                security_assessment['security_score'] += 10
            
            # Assess based on carrier security reputation
            if carrier_name:
                carrier_security = self._get_carrier_security_rating(carrier_name)
                security_assessment.update(carrier_security)
            
            # Check for known security issues
            security_issues = self._check_known_security_issues(parsed_number)
            if security_issues:
                security_assessment['vulnerability_indicators'].extend(security_issues)
                security_assessment['security_score'] -= len(security_issues) * 5
            
            # Ensure score stays within bounds
            security_assessment['security_score'] = max(0, min(100, security_assessment['security_score']))
            
            return security_assessment
            
        except Exception as e:
            self.logger.error(f"Network security assessment error: {str(e)}")
            return {}
    
    def _detect_network_technology(self, parsed_number):
        """Detect network technology (2G, 3G, 4G, 5G)"""
        try:
            # This would typically require real-time network probing
            # For now, return based on number type and carrier
            number_type = phonenumbers.number_type(parsed_number)
            
            if number_type == phonenumbers.PhoneNumberType.MOBILE:
                return "4G/5G (estimated)"
            elif number_type == phonenumbers.PhoneNumberType.VOIP:
                return "Internet/VoIP"
            else:
                return "Unknown"
                
        except:
            return "Unknown"
    
    def _get_roaming_partners(self, carrier_name):
        """Get roaming partner information"""
        try:
            # This would use carrier partnership databases
            # Placeholder implementation
            return ["International roaming available"]
        except:
            return []
    
    def _get_network_coverage(self, carrier_name, country):
        """Get network coverage information"""
        try:
            # This would use coverage databases
            # Placeholder implementation
            return f"Coverage in {country}"
        except:
            return "Unknown coverage"
    
    def _get_country_mobile_ranges(self, country):
        """Get mobile IP ranges for a country"""
        try:
            # This would use public IP allocation databases
            # Placeholder implementation
            country_ranges = {
                'United States': ['10.0.0.0/8', '172.16.0.0/12'],
                'United Kingdom': ['192.168.0.0/16'],
                'Canada': ['10.0.0.0/8']
            }
            return country_ranges.get(country, [])
        except:
            return []
    
    def _get_carrier_security_rating(self, carrier_name):
        """Get carrier security rating"""
        try:
            # This would use security rating databases
            # Placeholder implementation
            return {
                'encryption_support': 'Standard',
                'security_features': ['Network encryption', 'Authentication'],
                'security_score': 60
            }
        except:
            return {}
    
    def _check_known_security_issues(self, parsed_number):
        """Check for known security issues"""
        try:
            # This would check security vulnerability databases
            # Placeholder implementation
            return []
        except:
            return []
    
    def _get_digital_footprint(self, phone_input):
        """Get comprehensive digital footprint for the phone number"""
        try:
            footprint = {
                'search_engines': self._search_engines_lookup(phone_input),
                'public_records': self._check_public_records(phone_input),
                'business_listings': self._check_business_listings(phone_input),
                'online_directories': self._check_online_directories(phone_input),
                'data_brokers': self._check_data_brokers(phone_input),
                'reverse_lookup_results': self._reverse_phone_lookup(phone_input)
            }
            
            return footprint
            
        except Exception as e:
            self.logger.error(f"Digital footprint error: {str(e)}")
            return {}
    
    def _find_associated_emails(self, phone_input):
        """Find email addresses associated with the phone number"""
        try:
            associated_emails = {
                'found_emails': [],
                'confidence_scores': {},
                'sources': {},
                'verification_status': {}
            }
            
            # Search through various sources
            emails_from_breaches = self._find_emails_from_breaches(phone_input)
            emails_from_social = self._find_emails_from_social_media(phone_input)
            emails_from_public_records = self._find_emails_from_public_records(phone_input)
            emails_from_business = self._find_emails_from_business_listings(phone_input)
            
            all_emails = []
            all_emails.extend(emails_from_breaches)
            all_emails.extend(emails_from_social)
            all_emails.extend(emails_from_public_records)
            all_emails.extend(emails_from_business)
            
            # Remove duplicates and score confidence
            unique_emails = list(set(all_emails))
            
            for email in unique_emails:
                associated_emails['found_emails'].append(email)
                associated_emails['confidence_scores'][email] = self._calculate_email_confidence(email, phone_input)
                associated_emails['sources'][email] = self._identify_email_sources(email, phone_input)
                associated_emails['verification_status'][email] = self._verify_email_phone_association(email, phone_input)
            
            return associated_emails
            
        except Exception as e:
            self.logger.error(f"Email association error: {str(e)}")
            return {}
    
    def _find_associated_websites(self, phone_input):
        """Find websites associated with the phone number"""
        try:
            associated_websites = {
                'business_websites': [],
                'personal_websites': [],
                'social_profiles': [],
                'e_commerce_profiles': [],
                'professional_profiles': [],
                'confidence_scores': {}
            }
            
            # Search business directories
            business_sites = self._search_business_websites(phone_input)
            associated_websites['business_websites'].extend(business_sites)
            
            # Search professional networks
            professional_sites = self._search_professional_networks(phone_input)
            associated_websites['professional_profiles'].extend(professional_sites)
            
            # Search e-commerce platforms
            ecommerce_profiles = self._search_ecommerce_platforms(phone_input)
            associated_websites['e_commerce_profiles'].extend(ecommerce_profiles)
            
            # Search personal websites and blogs
            personal_sites = self._search_personal_websites(phone_input)
            associated_websites['personal_websites'].extend(personal_sites)
            
            # Calculate confidence scores for each website
            all_websites = (business_sites + professional_sites + 
                          ecommerce_profiles + personal_sites)
            
            for website in all_websites:
                associated_websites['confidence_scores'][website] = self._calculate_website_confidence(website, phone_input)
            
            return associated_websites
            
        except Exception as e:
            self.logger.error(f"Website association error: {str(e)}")
            return {}
    
    def _find_social_media_accounts(self, phone_input):
        """Find social media accounts associated with the phone number"""
        try:
            social_accounts = {
                'facebook': self._search_facebook(phone_input),
                'twitter': self._search_twitter(phone_input),
                'instagram': self._search_instagram(phone_input),
                'linkedin': self._search_linkedin(phone_input),
                'tiktok': self._search_tiktok(phone_input),
                'snapchat': self._search_snapchat(phone_input),
                'telegram': self._search_telegram(phone_input),
                'whatsapp': self._search_whatsapp_business(phone_input),
                'youtube': self._search_youtube(phone_input),
                'pinterest': self._search_pinterest(phone_input),
                'reddit': self._search_reddit(phone_input),
                'discord': self._search_discord(phone_input)
            }
            
            # Filter out empty results and add metadata
            filtered_accounts = {}
            for platform, results in social_accounts.items():
                if results and results.get('found'):
                    filtered_accounts[platform] = {
                        **results,
                        'confidence': self._calculate_social_confidence(platform, results, phone_input),
                        'last_updated': datetime.now().isoformat(),
                        'verification_method': results.get('method', 'Public search')
                    }
            
            return filtered_accounts
            
        except Exception as e:
            self.logger.error(f"Social media search error: {str(e)}")
            return {}
    
    # Email finding methods
    def _find_emails_from_breaches(self, phone_input):
        """Find emails from data breach databases"""
        try:
            # This would integrate with breach databases that allow phone number searches
            # Placeholder implementation
            return []
        except:
            return []
    
    def _find_emails_from_social_media(self, phone_input):
        """Find emails from social media profiles"""
        try:
            # This would search social media APIs for public email information
            # Placeholder implementation
            return []
        except:
            return []
    
    def _find_emails_from_public_records(self, phone_input):
        """Find emails from public records"""
        try:
            # This would search public records databases
            # Placeholder implementation
            return []
        except:
            return []
    
    def _find_emails_from_business_listings(self, phone_input):
        """Find emails from business listings"""
        try:
            # This would search business directory APIs
            # Placeholder implementation
            return []
        except:
            return []
    
    # Website finding methods
    def _search_business_websites(self, phone_input):
        """Search for business websites using the phone number"""
        try:
            # This would search Google My Business, Yelp, Yellow Pages, etc.
            # Placeholder implementation
            return []
        except:
            return []
    
    def _search_professional_networks(self, phone_input):
        """Search professional networks for profiles"""
        try:
            # This would search LinkedIn, AngelList, Crunchbase, etc.
            # Placeholder implementation
            return []
        except:
            return []
    
    def _search_ecommerce_platforms(self, phone_input):
        """Search e-commerce platforms for seller profiles"""
        try:
            # This would search eBay, Amazon seller profiles, Etsy, etc.
            # Placeholder implementation
            return []
        except:
            return []
    
    def _search_personal_websites(self, phone_input):
        """Search for personal websites and blogs"""
        try:
            # This would use search engines to find personal sites
            # Placeholder implementation
            return []
        except:
            return []
    
    # Social media search methods
    def _search_facebook(self, phone_input):
        """Search Facebook for profiles associated with phone number"""
        try:
            # Note: Facebook's API has strict privacy controls
            # This would only find publicly available information
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_twitter(self, phone_input):
        """Search Twitter for profiles"""
        try:
            # This would use Twitter's API to search for public profiles
            return {'found': False, 'profiles': [], 'method': 'API search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_instagram(self, phone_input):
        """Search Instagram for profiles"""
        try:
            # Instagram has strict privacy controls
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_linkedin(self, phone_input):
        """Search LinkedIn for professional profiles"""
        try:
            # LinkedIn's API has restrictions on phone number searches
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_tiktok(self, phone_input):
        """Search TikTok for profiles"""
        try:
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_snapchat(self, phone_input):
        """Search Snapchat for profiles"""
        try:
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_telegram(self, phone_input):
        """Search Telegram for public profiles"""
        try:
            # Telegram allows finding users by phone number if they allow it
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_whatsapp_business(self, phone_input):
        """Search WhatsApp Business profiles"""
        try:
            # WhatsApp Business profiles can be publicly searchable
            return {'found': False, 'profiles': [], 'method': 'Business directory'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_youtube(self, phone_input):
        """Search YouTube for channels"""
        try:
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_pinterest(self, phone_input):
        """Search Pinterest for profiles"""
        try:
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_reddit(self, phone_input):
        """Search Reddit for user profiles"""
        try:
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    def _search_discord(self, phone_input):
        """Search Discord for public profiles"""
        try:
            return {'found': False, 'profiles': [], 'method': 'Public search'}
        except:
            return {'found': False, 'profiles': []}
    
    # Additional OSINT methods
    def _search_engines_lookup(self, phone_input):
        """Search engines for phone number mentions"""
        try:
            # This would use search engine APIs to find mentions
            return {'google_results': 0, 'bing_results': 0, 'duckduckgo_results': 0}
        except:
            return {}
    
    def _check_public_records(self, phone_input):
        """Check public records databases"""
        try:
            # This would search public records APIs
            return {'found': False, 'records': []}
        except:
            return {}
    
    def _check_business_listings(self, phone_input):
        """Check business listing directories"""
        try:
            # This would search Yellow Pages, Google My Business, etc.
            return {'found': False, 'listings': []}
        except:
            return {}
    
    def _check_online_directories(self, phone_input):
        """Check online phone directories"""
        try:
            # This would search WhitePages, Spokeo, etc.
            return {'found': False, 'directories': []}
        except:
            return {}
    
    def _check_data_brokers(self, phone_input):
        """Check data broker websites"""
        try:
            # This would check people search engines
            return {'found': False, 'brokers': []}
        except:
            return {}
    
    def _reverse_phone_lookup(self, phone_input):
        """Perform reverse phone lookup"""
        try:
            # This would use reverse lookup services
            return {'found': False, 'results': []}
        except:
            return {}
    
    # Confidence calculation methods
    def _calculate_email_confidence(self, email, phone_input):
        """Calculate confidence score for email association"""
        try:
            # This would analyze various factors to determine confidence
            return 50  # Placeholder neutral score
        except:
            return 0
    
    def _calculate_website_confidence(self, website, phone_input):
        """Calculate confidence score for website association"""
        try:
            # This would analyze various factors to determine confidence
            return 50  # Placeholder neutral score
        except:
            return 0
    
    def _calculate_social_confidence(self, platform, results, phone_input):
        """Calculate confidence score for social media association"""
        try:
            # This would analyze various factors to determine confidence
            return 50  # Placeholder neutral score
        except:
            return 0
    
    # Verification methods
    def _identify_email_sources(self, email, phone_input):
        """Identify sources where email was found"""
        try:
            return ['Public records']  # Placeholder
        except:
            return []
    
    def _verify_email_phone_association(self, email, phone_input):
        """Verify the association between email and phone"""
        try:
            return 'Unverified'  # Placeholder
        except:
            return 'Unknown'
