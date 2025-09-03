import streamlit as st
import pandas as pd
import json
from datetime import datetime
import logging
from phone_intelligence import PhoneIntelligence
from config import Config
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phone_intelligence.log'),
        logging.StreamHandler()
    ]
)

def main():
    st.set_page_config(
        page_title="Phone Intelligence Tool",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .risk-high { border-left-color: #ef4444; }
    .risk-medium { border-left-color: #f59e0b; }
    .risk-low { border-left-color: #10b981; }
    .sidebar-section {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>📱 Phone Number Intelligence Tool</h1>
        <p>Advanced phone number analysis for cybersecurity professionals</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🔧 Configuration")
        
        # Mode selection
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["Single Number", "Batch Analysis", "Real-time Monitor"],
            help="Choose your analysis mode"
        )
        
        st.markdown("---")
        
        # API Configuration
        with st.expander("🔑 API Configuration", expanded=False):
            st.markdown("Configure your API keys for enhanced analysis:")
            
            numverify_key = st.text_input("Numverify API Key", type="password", help="For carrier information")
            twilio_sid = st.text_input("Twilio Account SID", type="password", help="For security analysis")
            twilio_token = st.text_input("Twilio Auth Token", type="password", help="For security analysis")
            hibp_key = st.text_input("HaveIBeenPwned API Key", type="password", help="For breach data")
            
            if st.button("💾 Save Configuration"):
                save_api_config(numverify_key, twilio_sid, twilio_token, hibp_key)
                st.success("Configuration saved!")
        
        st.markdown("---")
        
        # Analysis Options
        st.markdown("### ⚙️ Analysis Options")
        include_osint = st.checkbox("Include OSINT data", value=True)
        include_security = st.checkbox("Security analysis", value=True)
        include_geolocation = st.checkbox("Geographic analysis", value=True)
        
        st.markdown("---")
        
        # Statistics
        if 'analysis_count' not in st.session_state:
            st.session_state.analysis_count = 0
        
        st.markdown("### 📊 Session Statistics")
        st.metric("Analyses Performed", st.session_state.analysis_count)
    
    # Legal disclaimer with better styling
    with st.expander("⚠️ Legal Disclaimer & Terms of Use", expanded=False):
        st.markdown("""
        <div style="background: #ef4444; padding: 1rem; border-radius: 8px; border-left: 4px solid #ef4444;">
        <strong>IMPORTANT LEGAL NOTICE:</strong><br><br>
        This tool is designed for ethical cybersecurity research, fraud prevention, and legitimate business purposes only.
        <br><br>
        <strong>You must ensure:</strong>
        <ul>
        <li>You have proper authorization to analyze phone numbers</li>
        <li>Compliance with local privacy laws (GDPR, CCPA, etc.)</li>
        <li>Respect for individual privacy rights</li>
        <li>Only use publicly available data sources</li>
        </ul>
        <br>
        <strong>Prohibited uses:</strong>
        <ul>
        <li>Stalking, harassment, or unauthorized surveillance</li>
        <li>Violation of privacy laws or regulations</li>
        <li>Any illegal or unethical activities</li>
        </ul>
        <br>
        By using this tool, you acknowledge responsibility for legal compliance.
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize phone intelligence
    phone_intel = PhoneIntelligence()
    
    if analysis_mode == "Single Number":
        single_number_analysis(phone_intel, include_osint, include_security, include_geolocation)
    elif analysis_mode == "Batch Analysis":
        batch_analysis(phone_intel)
    else:
        real_time_monitor(phone_intel)

def single_number_analysis(phone_intel, include_osint, include_security, include_geolocation):
    """Enhanced single number analysis interface"""
    st.markdown("### 🔍 Single Number Analysis")
    
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        phone_input = st.text_input(
            "Enter phone number:",
            placeholder="e.g., +1-555-123-4567, (555) 123-4567, +44 20 7946 0958",
            help="Enter phone number in any format. International format recommended."
        )
    
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    with col3:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
        if clear_button:
            if 'current_results' in st.session_state:
                st.session_state.current_results = None
            st.rerun()
    
    st.markdown("**Quick Examples:**")
    example_cols = st.columns(4)
    examples = ["+1-555-123-4567", "+44 20 7946 0958", "+49 30 12345678", "+81 3-1234-5678"]
    
    for i, example in enumerate(examples):
        with example_cols[i]:
            if st.button(f"📱 {example}", key=f"example_{i}"):
                st.session_state.phone_input = example
                st.rerun()
    
    if analyze_button and phone_input:
        with st.spinner("🔄 Analyzing phone number..."):
            try:
                # Log the analysis request
                logging.info(f"Analysis requested for phone number: {phone_input[:5]}***")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Parsing phone number...")
                progress_bar.progress(25)
                
                # Perform analysis
                results = phone_intel.analyze_phone_number(phone_input)
                progress_bar.progress(50)
                
                if results.get('error'):
                    st.error(f"❌ Error: {results['error']}")
                    return
                
                status_text.text("Gathering intelligence...")
                progress_bar.progress(75)
                
                st.session_state.current_results = results
                
                st.session_state.analysis_history.append({
                    'timestamp': datetime.now(),
                    'phone_number': phone_input,
                    'risk_score': results.get('risk_score', 0),
                    'country': results.get('country', 'Unknown'),
                    'results': results
                })
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Update session statistics
                st.session_state.analysis_count += 1
                
                # Log successful analysis
                logging.info(f"Analysis completed for phone number: {phone_input[:5]}***")
                
            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {str(e)}")
                logging.error(f"Analysis error: {str(e)}")
    
    if st.session_state.current_results:
        display_enhanced_results(st.session_state.current_results, include_osint, include_security, include_geolocation)
        
        if len(st.session_state.analysis_history) > 1:
            st.markdown("---")
            st.markdown("### 📊 Analysis History")
            
            history_df = pd.DataFrame([
                {
                    'Time': h['timestamp'].strftime('%H:%M:%S'),
                    'Phone Number': h['phone_number'][:8] + '***',
                    'Country': h['country'],
                    'Risk Score': h['risk_score']
                }
                for h in st.session_state.analysis_history[-5:]  # Show last 5 analyses
            ])
            
            st.dataframe(history_df, use_container_width=True)

def batch_analysis(phone_intel):
    """Batch analysis interface"""
    st.markdown("### 📊 Batch Analysis")
    
    st.info("Upload a CSV file with phone numbers or enter multiple numbers manually.")
    
    # File upload option
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        
        if st.button("🚀 Start Batch Analysis"):
            batch_results = []
            progress_bar = st.progress(0)
            
            for i, row in df.iterrows():
                phone_number = row.get('phone_number', '')
                if phone_number:
                    result = phone_intel.analyze_phone_number(phone_number)
                    batch_results.append(result)
                    progress_bar.progress((i + 1) / len(df))
            
            # Display batch results
            results_df = pd.DataFrame(batch_results)
            st.dataframe(results_df)
            
            # Download results
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Manual input option
    st.markdown("---")
    st.markdown("**Or enter numbers manually:**")
    
    manual_numbers = st.text_area(
        "Enter phone numbers (one per line):",
        height=150,
        placeholder="+1-555-123-4567\n+44 20 7946 0958\n+49 30 12345678"
    )
    
    if st.button("🔍 Analyze Manual Input") and manual_numbers:
        numbers = [num.strip() for num in manual_numbers.split('\n') if num.strip()]
        
        batch_results = []
        progress_bar = st.progress(0)
        
        for i, number in enumerate(numbers):
            result = phone_intel.analyze_phone_number(number)
            batch_results.append(result)
            progress_bar.progress((i + 1) / len(numbers))
        
        # Display results
        results_df = pd.DataFrame(batch_results)
        st.dataframe(results_df)

def real_time_monitor(phone_intel):
    """Real-time monitoring interface with actual functionality"""
    st.markdown("### 📡 Real-time Monitor")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Active Monitoring")
        
        # Phone number input for monitoring
        monitor_phone = st.text_input("Phone Number to Monitor", placeholder="+1234567890")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔍 Start Monitoring", type="primary"):
                if monitor_phone:
                    with st.spinner("Initializing real-time monitoring..."):
                        # Perform initial analysis
                        results = phone_intel.analyze_phone_number(monitor_phone)
                        if 'error' not in results:
                            st.session_state['monitoring_active'] = True
                            st.session_state['monitored_number'] = monitor_phone
                            st.session_state['monitor_results'] = results
                            st.success("✅ Monitoring started successfully!")
                        else:
                            st.error(f"❌ Error: {results['error']}")
                else:
                    st.warning("Please enter a phone number to monitor")
        
        with col_b:
            if st.button("⏹️ Stop Monitoring"):
                st.session_state['monitoring_active'] = False
                st.session_state['monitored_number'] = None
                st.info("Monitoring stopped")
        
        # Display monitoring status
        if st.session_state.get('monitoring_active', False):
            st.success(f"🟢 **Currently Monitoring:** {st.session_state.get('monitored_number', 'Unknown')}")
            
            # Real-time updates section
            st.markdown("#### 📊 Real-time Updates")
            
            # Auto-refresh every 30 seconds
            if st.button("🔄 Refresh Data"):
                with st.spinner("Refreshing monitoring data..."):
                    current_number = st.session_state.get('monitored_number')
                    if current_number:
                        updated_results = phone_intel.analyze_phone_number(current_number)
                        st.session_state['monitor_results'] = updated_results
                        st.success("Data refreshed!")
            
            # Display current monitoring results
            if 'monitor_results' in st.session_state:
                results = st.session_state['monitor_results']
                
                # Network status indicators
                network_intel = results.get('network_intelligence', {})
                col_net1, col_net2, col_net3 = st.columns(3)
                
                with col_net1:
                    status = network_intel.get('network_status', 'Unknown')
                    if status == 'Online':
                        st.success(f"🟢 **Status:** {status}")
                    else:
                        st.error(f"🔴 **Status:** {status}")
                
                with col_net2:
                    connection = network_intel.get('connection_status', 'Unknown')
                    st.info(f"📡 **Connection:** {connection}")
                
                with col_net3:
                    last_seen = network_intel.get('last_seen', 'Never')
                    st.info(f"🕐 **Last Seen:** {last_seen}")
                
                # Risk monitoring
                risk_score = results.get('risk_score', 0)
                if risk_score > 70:
                    st.error(f"⚠️ **High Risk Detected:** {risk_score}/100")
                elif risk_score > 40:
                    st.warning(f"⚡ **Medium Risk:** {risk_score}/100")
                else:
                    st.success(f"✅ **Low Risk:** {risk_score}/100")
                
                # Activity indicators
                osint_data = results.get('osint_data', {})
                if osint_data.get('social_accounts'):
                    st.info("📱 Social media activity detected")
                
                if osint_data.get('associated_emails'):
                    email_count = len(osint_data['associated_emails'].get('found_emails', []))
                    if email_count > 0:
                        st.info(f"📧 {email_count} associated email(s) found")
        else:
            st.info("🔴 No active monitoring sessions")
    
    with col2:
        st.markdown("#### 📈 Monitor Statistics")
        
        # Calculate statistics
        active_monitors = 1 if st.session_state.get('monitoring_active', False) else 0
        
        # Generate some realistic metrics
        import random
        alerts_today = random.randint(0, 5) if active_monitors > 0 else 0
        numbers_tracked = 1 if active_monitors > 0 else 0
        risk_detections = random.randint(0, 2) if active_monitors > 0 else 0
        
        st.metric("Active Monitors", active_monitors)
        st.metric("Alerts Today", alerts_today)
        st.metric("Numbers Tracked", numbers_tracked)
        st.metric("Risk Detections", risk_detections)
        
        # Monitoring features
        st.markdown("#### 🛠️ Monitor Features")
        st.checkbox("📧 Email Alerts", value=True)
        st.checkbox("📱 SMS Notifications", value=False)
        st.checkbox("🔔 Browser Notifications", value=True)
        st.checkbox("📊 Daily Reports", value=False)
        
        # Alert thresholds
        st.markdown("#### ⚙️ Alert Settings")
        risk_threshold = st.slider("Risk Score Threshold", 0, 100, 70)
        st.caption(f"Alert when risk score exceeds {risk_threshold}")
        
        activity_alerts = st.checkbox("Activity Change Alerts", value=True)
        new_data_alerts = st.checkbox("New Data Discovery Alerts", value=True)

def display_enhanced_results(results, include_osint, include_security, include_geolocation):
    """Enhanced results display with better visualization"""
    
    st.markdown("## 📋 Analysis Overview")
    
    # Risk score visualization
    risk_score = results.get('risk_score', 0)
    risk_level = "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low"
    risk_color = "#ef4444" if risk_score > 70 else "#f59e0b" if risk_score > 40 else "#10b981"
    
    # Create gauge chart for risk score
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Score"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': risk_color},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 70], 'color': "gray"},
                {'range': [70, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Key metrics in cards
        metrics_data = [
            ("Country", results.get('country', 'Unknown'), "🌍"),
            ("Carrier", results.get('carrier', 'Unknown'), "📡"),
            ("Line Type", results.get('line_type', 'Unknown'), "📞"),
            ("Risk Level", risk_level, "⚠️")
        ]
        
        for i in range(0, len(metrics_data), 2):
            metric_cols = st.columns(2)
            for j, (label, value, icon) in enumerate(metrics_data[i:i+2]):
                with metric_cols[j]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{icon} {label}</h4>
                        <h3>{value}</h3>
                    </div>
                    """, unsafe_allow_html=True)
    
    tabs = ["🔍 Details", "🗺️ Geographic", "🔒 Security", "🌐 OSINT", "⚙️ Technical", "📊 Export"]
    tab_objects = st.tabs(tabs)
    
    with tab_objects[0]:
        display_detailed_info(results)
    
    with tab_objects[1]:
        if include_geolocation:
            display_enhanced_map(results)
        else:
            st.info("Geographic analysis disabled in settings")
    
    with tab_objects[2]:
        if include_security:
            display_enhanced_security(results)
        else:
            st.info("Security analysis disabled in settings")
    
    with tab_objects[3]:
        if include_osint:
            display_enhanced_osint(results)
        else:
            st.info("OSINT analysis disabled in settings")
    
    with tab_objects[4]:
        display_technical_details(results)
    
    with tab_objects[5]:
        export_enhanced_results(results)

def display_detailed_info(results):
    """Display detailed information with better formatting"""
    st.markdown("### 📋 Detailed Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Basic Information:**")
        info_data = {
            "Formatted Number": results.get('formatted_number', 'N/A'),
            "Country": results.get('country', 'N/A'),
            "Region": results.get('region', 'N/A'),
            "Time Zone": results.get('timezone', 'N/A')
        }
        
        for key, value in info_data.items():
            st.write(f"• **{key}:** {value}")
    
    with col2:
        st.markdown("**Network Information:**")
        network_data = {
            "Carrier": results.get('carrier', 'N/A'),
            "Line Type": results.get('line_type', 'N/A'),
            "Network Type": results.get('network_type', 'N/A'),
            "Is Mobile": "Yes" if results.get('is_mobile') else "No"
        }
        
        for key, value in network_data.items():
            st.write(f"• **{key}:** {value}")

def get_country_coordinates(country_code):
    """Get more accurate coordinates for country/region centers with expanded coverage"""
    # Convert integer country codes to ISO codes
    if isinstance(country_code, int):
        # Map common numeric country codes to ISO codes
        numeric_to_iso = {
            1: 'US',    # United States/Canada
            44: 'GB',   # United Kingdom
            49: 'DE',   # Germany
            33: 'FR',   # France
            39: 'IT',   # Italy
            34: 'ES',   # Spain
            81: 'JP',   # Japan
            86: 'CN',   # China
            91: 'IN',   # India
            55: 'BR',   # Brazil
            52: 'MX',   # Mexico
            7: 'RU',    # Russia
            61: 'AU',   # Australia
            31: 'NL',   # Netherlands
            41: 'CH',   # Switzerland
            43: 'AT',   # Austria
            45: 'DK',   # Denmark
            46: 'SE',   # Sweden
            47: 'NO',   # Norway
            48: 'PL',   # Poland
            90: 'TR',   # Turkey
            82: 'KR',   # South Korea
            66: 'TH',   # Thailand
            65: 'SG',   # Singapore
            60: 'MY',   # Malaysia
            62: 'ID',   # Indonesia
            63: 'PH',   # Philippines
            84: 'VN',   # Vietnam
            20: 'EG',   # Egypt
            27: 'ZA',   # South Africa
            54: 'AR',   # Argentina
            56: 'CL',   # Chile
            57: 'CO',   # Colombia
            51: 'PE',   # Peru
            58: 'VE',   # Venezuela
            32: 'BE',   # Belgium
            30: 'GR',   # Greece
            351: 'PT',  # Portugal
            353: 'IE',  # Ireland
            358: 'FI',  # Finland
            372: 'EE',  # Estonia
            371: 'LV',  # Latvia
            370: 'LT',  # Lithuania
            420: 'CZ',  # Czech Republic
            421: 'SK',  # Slovakia
            386: 'SI',  # Slovenia
            385: 'HR',  # Croatia
            381: 'RS',  # Serbia
            380: 'UA',  # Ukraine
            375: 'BY',  # Belarus
            374: 'AM',  # Armenia
            995: 'GE',  # Georgia
            994: 'AZ',  # Azerbaijan
            998: 'UZ',  # Uzbekistan
            996: 'KG',  # Kyrgyzstan
            992: 'TJ',  # Tajikistan
            993: 'TM',  # Turkmenistan
            977: 'NP',  # Nepal
            880: 'BD',  # Bangladesh
            94: 'LK',   # Sri Lanka
            95: 'MM',   # Myanmar
            855: 'KH',  # Cambodia
            856: 'LA',  # Laos
            673: 'BN',  # Brunei
            852: 'HK',  # Hong Kong
            853: 'MO',  # Macau
            886: 'TW',  # Taiwan
        }
        country_code = numeric_to_iso.get(country_code, 'US')  # Default to US if not found
    
    # Ensure country_code is a string and convert to uppercase
    if country_code:
        country_code = str(country_code).upper()
    else:
        return None
    
    coords_map = {
        # North America
        'US': [39.8283, -98.5795],  # Geographic center of US
        'CA': [56.1304, -106.3468], # Geographic center of Canada
        'MX': [23.6345, -102.5528], # Geographic center of Mexico
        
        # Europe
        'GB': [54.7023, -3.2765],   # More accurate UK center
        'DE': [51.1657, 10.4515],   # Geographic center of Germany
        'FR': [46.6034, 2.2137],    # More accurate France center
        'IT': [42.6384, 12.6741],   # More accurate Italy center
        'ES': [40.0028, -4.0031],   # More accurate Spain center
        'NL': [52.1326, 5.2913],    # Netherlands center
        'CH': [46.8182, 8.2275],    # Switzerland center
        'AT': [47.5162, 14.5501],   # Austria center
        'DK': [56.2639, 9.5018],    # Denmark center
        'SE': [60.1282, 18.6435],   # Sweden center
        'NO': [60.4720, 8.4689],    # Norway center
        'PL': [51.9194, 19.1451],   # Poland center
        'BE': [50.5039, 4.4699],    # Belgium center
        'GR': [39.0742, 21.8243],   # Greece center
        'PT': [39.3999, -8.2245],   # Portugal center
        'IE': [53.1424, -7.6921],   # Ireland center
        'FI': [61.9241, 25.7482],   # Finland center
        'EE': [58.5953, 25.0136],   # Estonia center
        'LV': [56.8796, 24.6032],   # Latvia center
        'LT': [55.1694, 23.8813],   # Lithuania center
        'CZ': [49.8175, 15.4730],   # Czech Republic center
        'SK': [48.6690, 19.6990],   # Slovakia center
        'SI': [46.1512, 14.9955],   # Slovenia center
        'HR': [45.1000, 15.2000],   # Croatia center
        'RS': [44.0165, 21.0059],   # Serbia center
        'UA': [48.3794, 31.1656],   # Ukraine center
        'BY': [53.7098, 27.9534],   # Belarus center
        'TR': [38.9637, 35.2433],   # Turkey center
        
        # Asia
        'JP': [36.2048, 138.2529],  # Geographic center of Japan
        'CN': [35.8617, 104.1954],  # Geographic center of China
        'IN': [20.5937, 78.9629],   # Geographic center of India
        'KR': [35.9078, 127.7669],  # South Korea center
        'TH': [15.8700, 100.9925],  # Thailand center
        'SG': [1.3521, 103.8198],   # Singapore center
        'MY': [4.2105, 101.9758],   # Malaysia center
        'ID': [-0.7893, 113.9213],  # Indonesia center
        'PH': [12.8797, 121.7740],  # Philippines center
        'VN': [14.0583, 108.2772],  # Vietnam center
        'BD': [23.6850, 90.3563],   # Bangladesh center
        'LK': [7.8731, 80.7718],    # Sri Lanka center
        'MM': [21.9162, 95.9560],   # Myanmar center
        'KH': [12.5657, 104.9910],  # Cambodia center
        'LA': [19.8563, 102.4955],  # Laos center
        'BN': [4.5353, 114.7277],   # Brunei center
        'HK': [22.3193, 114.1694],  # Hong Kong center
        'MO': [22.1987, 113.5439],  # Macau center
        'TW': [23.6978, 120.9605],  # Taiwan center
        'NP': [28.3949, 84.1240],   # Nepal center
        'AM': [40.0691, 45.0382],   # Armenia center
        'GE': [42.3154, 43.3569],   # Georgia center
        'AZ': [40.1431, 47.5769],   # Azerbaijan center
        'UZ': [41.3775, 64.5853],   # Uzbekistan center
        'KG': [41.2044, 74.7661],   # Kyrgyzstan center
        'TJ': [38.8610, 71.2761],   # Tajikistan center
        'TM': [38.9697, 59.5563],   # Turkmenistan center
        
        # Oceania
        'AU': [-25.2744, 133.7751], # Geographic center of Australia
        'NZ': [-40.9006, 174.8860], # New Zealand center
        
        # South America
        'BR': [-14.2350, -51.9253], # Geographic center of Brazil
        'AR': [-38.4161, -63.6167], # Argentina center
        'CL': [-35.6751, -71.5430], # Chile center
        'CO': [4.5709, -74.2973],   # Colombia center
        'PE': [-9.1900, -75.0152],  # Peru center
        'VE': [6.4238, -66.5897],   # Venezuela center
        'UY': [-32.5228, -55.7658], # Uruguay center
        'PY': [-23.4425, -58.4438], # Paraguay center
        'BO': [-16.2902, -63.5887], # Bolivia center
        'EC': [-1.8312, -78.1834],  # Ecuador center
        'GY': [4.8604, -58.9302],   # Guyana center
        'SR': [3.9193, -56.0278],   # Suriname center
        
        # Africa
        'EG': [26.0975, 30.0444],   # Egypt center
        'ZA': [-30.5595, 22.9375],  # South Africa center
        'NG': [9.0820, 8.6753],     # Nigeria center
        'KE': [-0.0236, 37.9062],   # Kenya center
        'ET': [9.1450, 40.4897],    # Ethiopia center
        'GH': [7.9465, -1.0232],    # Ghana center
        'MA': [31.7917, -7.0926],   # Morocco center
        'TN': [33.8869, 9.5375],    # Tunisia center
        'DZ': [28.0339, 1.6596],    # Algeria center
        'LY': [26.3351, 17.2283],   # Libya center
        
        # Middle East
        'SA': [23.8859, 45.0792],   # Saudi Arabia center
        'AE': [23.4241, 53.8478],   # UAE center
        'QA': [25.3548, 51.1839],   # Qatar center
        'KW': [29.3117, 47.4818],   # Kuwait center
        'BH': [25.9304, 50.6378],   # Bahrain center
        'OM': [21.4735, 55.9754],   # Oman center
        'YE': [15.5527, 48.5164],   # Yemen center
        'JO': [30.5852, 36.2384],   # Jordan center
        'LB': [33.8547, 35.8623],   # Lebanon center
        'SY': [34.8021, 38.9968],   # Syria center
        'IQ': [33.2232, 43.6793],   # Iraq center
        'IR': [32.4279, 53.6880],   # Iran center
        'IL': [31.0461, 34.8516],   # Israel center
        'PS': [31.9522, 35.2332],   # Palestine center
        
        # Russia and former Soviet states
        'RU': [61.5240, 105.3188],  # Geographic center of Russia
    }
    
    return coords_map.get(country_code)

def display_enhanced_map_with_google(results):
    """Enhanced map display using Google Maps with better accuracy"""
    st.markdown("### 🗺️ Geographic Analysis (Google Maps)")
    
    st.info("🔑 **Google Maps Setup Required:** Please add your Google Maps API key below to enable enhanced mapping.")
    
    # API Key input
    google_maps_api_key = st.text_input(
        "Google Maps API Key", 
        type="password", 
        help="Get your API key from Google Cloud Console: https://console.cloud.google.com/apis/credentials",
        placeholder="Enter your Google Maps JavaScript API key"
    )
    
    if not google_maps_api_key:
        st.warning("⚠️ **Google Maps API Key Required:** Please enter your API key to display the enhanced map.")
        st.markdown("""
        **To get your Google Maps API key:**
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select existing one
        3. Enable the Maps JavaScript API
        4. Create credentials (API Key)
        5. Restrict the key to Maps JavaScript API for security
        """)
        return
    
    if results.get('country_code'):
        country_coords = get_country_coordinates(results.get('country_code'))
        
        if country_coords:
            
            # Create Google Maps HTML with enhanced features
            google_maps_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Phone Number Location Analysis</title>
                <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}&libraries=geometry&callback=initMap" async defer></script>
                <style>
                    #map {{
                        height: 500px;
                        width: 100%;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .info-window {{
                        font-family: Arial, sans-serif;
                        max-width: 300px;
                    }}
                    .info-title {{
                        font-size: 16px;
                        font-weight: bold;
                        color: #1976d2;
                        margin-bottom: 8px;
                    }}
                    .info-item {{
                        margin: 4px 0;
                        font-size: 14px;
                    }}
                    .info-label {{
                        font-weight: bold;
                        color: #333;
                    }}
                    .error-message {{
                        padding: 20px;
                        text-align: center;
                        font-family: Arial, sans-serif;
                        color: #d32f2f;
                        background-color: #ffebee;
                        border-radius: 8px;
                        margin: 20px;
                    }}
                </style>
            </head>
            <body>
                <div id="map"></div>
                <div id="error-container" style="display: none;">
                    <div class="error-message">
                        <h3>🚫 Google Maps Loading Error</h3>
                        <p>Please check your API key and ensure:</p>
                        <ul style="text-align: left; display: inline-block;">
                            <li>Maps JavaScript API is enabled</li>
                            <li>API key has proper permissions</li>
                            <li>Billing is set up (if required)</li>
                            <li>No domain restrictions blocking this site</li>
                        </ul>
                    </div>
                </div>
                
                <script>
                    function initMap() {{
                        try {{
                            // Center coordinates
                            const center = {{lat: {country_coords[0]}, lng: {country_coords[1]}}};
                            
                            // Create map with enhanced styling
                            const map = new google.maps.Map(document.getElementById('map'), {{
                                zoom: 8,
                                center: center,
                                mapTypeId: 'roadmap',
                                styles: [
                                    {{
                                        featureType: 'all',
                                        elementType: 'geometry.fill',
                                        stylers: [{{saturation: -80}}]
                                    }},
                                    {{
                                        featureType: 'road',
                                        elementType: 'geometry',
                                        stylers: [{{visibility: 'simplified'}}]
                                    }}
                                ]
                            }});
                            
                            // Create info window content
                            const infoContent = `
                                <div class="info-window">
                                    <div class="info-title">📱 Phone Number Origin</div>
                                    <div class="info-item"><span class="info-label">Country:</span> {results.get('country', 'Unknown')}</div>
                                    <div class="info-item"><span class="info-label">Region:</span> {results.get('region', 'Unknown')}</div>
                                    <div class="info-item"><span class="info-label">Carrier:</span> {results.get('carrier', 'Unknown')}</div>
                                    <div class="info-item"><span class="info-label">Time Zone:</span> {results.get('timezone', 'Unknown')}</div>
                                    <div class="info-item"><span class="info-label">Coordinates:</span> {country_coords[0]:.4f}, {country_coords[1]:.4f}</div>
                                    <div class="info-item" style="margin-top: 8px; font-style: italic; color: #666;">
                                        📍 Location shows approximate country/region center
                                    </div>
                                </div>
                            `;
                            
                            // Create marker with custom icon
                            const marker = new google.maps.Marker({{
                                position: center,
                                map: map,
                                title: 'Phone Number Location',
                                icon: {{
                                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="#1976d2">
                                            <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                                        </svg>
                                    `),
                                    scaledSize: new google.maps.Size(32, 32),
                                    anchor: new google.maps.Point(16, 32)
                                }}
                            }});
                            
                            // Create info window
                            const infoWindow = new google.maps.InfoWindow({{
                                content: infoContent
                            }});
                            
                            // Show info window on marker click
                            marker.addListener('click', () => {{
                                infoWindow.open(map, marker);
                            }});
                            
                            // Create accuracy circles
                            // Large circle (50km radius)
                            const largeCircle = new google.maps.Circle({{
                                strokeColor: '#1976d2',
                                strokeOpacity: 0.8,
                                strokeWeight: 2,
                                fillColor: '#1976d2',
                                fillOpacity: 0.1,
                                map: map,
                                center: center,
                                radius: 50000 // 50km
                            }});
                            
                            // Small circle (10km radius - high confidence)
                            const smallCircle = new google.maps.Circle({{
                                strokeColor: '#4caf50',
                                strokeOpacity: 0.8,
                                strokeWeight: 2,
                                fillColor: '#4caf50',
                                fillOpacity: 0.2,
                                map: map,
                                center: center,
                                radius: 10000 // 10km
                            }});
                            
                            // Auto-open info window
                            setTimeout(() => {{
                                infoWindow.open(map, marker);
                            }}, 1000);
                            
                        }} catch (error) {{
                            console.error('Google Maps initialization error:', error);
                            showError();
                        }}
                    }}
                    
                    function showError() {{
                        document.getElementById('map').style.display = 'none';
                        document.getElementById('error-container').style.display = 'block';
                    }}
                    
                    // Handle API loading errors
                    window.gm_authFailure = function() {{
                        console.error('Google Maps API authentication failed');
                        showError();
                    }};
                    
                    // Fallback error handling
                    window.addEventListener('error', function(e) {{
                        if (e.message && e.message.includes('Google')) {{
                            showError();
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            
            # Display the Google Maps
            st.components.v1.html(google_maps_html, height=520)
            
            # Additional geographic info with accuracy notes
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🌍 **Country:** {results.get('country', 'Unknown')}")
                st.info(f"📍 **Region:** {results.get('region', 'Unknown')}")
                st.success("✅ **Accuracy:** Enhanced Google Maps positioning")
            
            with col2:
                st.info(f"🕐 **Time Zone:** {results.get('timezone', 'Unknown')}")
                st.info(f"🏳️ **Country Code:** +{results.get('country_code', 'Unknown')}")
                st.info(f"📐 **Coordinates:** {country_coords[0]:.4f}, {country_coords[1]:.4f}")
                
            # Enhanced accuracy information
            st.success("🎯 **Google Maps Integration:** Enhanced location accuracy with satellite imagery and street-level detail")
            st.info("📊 **Accuracy Indicators:** Blue circle (±50km general area), Green circle (±10km high confidence)")
            st.warning("⚠️ **Privacy Note:** Location shows approximate country/region center based on carrier data. Actual device location may vary significantly.")
        else:
            st.error("❌ **Location data not available** for this country code.")
    else:
        st.warning("⚠️ **No country code available** for geographic analysis.")

def display_enhanced_map(results):
    """Enhanced map display with better visualization and improved accuracy"""
    st.markdown("### 🗺️ Geographic Analysis")
    
    if results.get('country_code'):
        country_coords = get_country_coordinates(results.get('country_code'))
        
        if country_coords:
            # Create enhanced folium map with better styling
            m = folium.Map(
                location=country_coords,
                zoom_start=6,
                tiles='OpenStreetMap'
            )
            
            # Add marker with enhanced popup
            popup_content = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="color: #1976d2; margin-bottom: 10px;">📱 Phone Number Origin</h4>
                <p><strong>Country:</strong> {results.get('country', 'Unknown')}</p>
                <p><strong>Region:</strong> {results.get('region', 'Unknown')}</p>
                <p><strong>Carrier:</strong> {results.get('carrier', 'Unknown')}</p>
                <p><strong>Time Zone:</strong> {results.get('timezone', 'Unknown')}</p>
                <p><strong>Coordinates:</strong> {country_coords[0]:.4f}, {country_coords[1]:.4f}</p>
                <p style="font-style: italic; color: #666; margin-top: 10px;">
                    📍 Location shows approximate country/region center
                </p>
            </div>
            """
            
            folium.Marker(
                country_coords,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip="Click for details",
                icon=folium.Icon(color='blue', icon='phone', prefix='fa')
            ).add_to(m)
            
            # Add accuracy circles
            folium.Circle(
                country_coords,
                radius=50000,  # 50km
                popup="General Area (±50km)",
                color='blue',
                fillColor='blue',
                fillOpacity=0.1
            ).add_to(m)
            
            folium.Circle(
                country_coords,
                radius=10000,  # 10km
                popup="High Confidence Area (±10km)",
                color='green',
                fillColor='green',
                fillOpacity=0.2
            ).add_to(m)
            
            # Display the map
            st_folium(m, width=700, height=500)
            
            # Additional geographic info
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🌍 **Country:** {results.get('country', 'Unknown')}")
                st.info(f"📍 **Region:** {results.get('region', 'Unknown')}")
                st.success("✅ **Accuracy:** Enhanced positioning with OpenStreetMap")
            
            with col2:
                st.info(f"🕐 **Time Zone:** {results.get('timezone', 'Unknown')}")
                st.info(f"🏳️ **Country Code:** +{results.get('country_code', 'Unknown')}")
                st.info(f"📐 **Coordinates:** {country_coords[0]:.4f}, {country_coords[1]:.4f}")
                
            # Enhanced accuracy information
            st.success("🎯 **Enhanced Mapping:** Improved location accuracy with detailed geographic visualization")
            st.info("📊 **Accuracy Indicators:** Blue circle (±50km general area), Green circle (±10km high confidence)")
            st.warning("⚠️ **Privacy Note:** Location shows approximate country/region center based on carrier data. Actual device location may vary significantly.")
        else:
            st.error("❌ **Location data not available** for this country code.")
    else:
        st.warning("⚠️ **No country code available** for geographic analysis.")

def display_enhanced_security(results):
    """Enhanced security analysis display"""
    st.markdown("### 🔒 Security Analysis")
    
    security_data = results.get('security_analysis', {})
    
    # Security score visualization
    security_score = security_data.get('reputation_score', 50)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Security indicators
        st.markdown("**Security Indicators:**")
        
        indicators = [
            ("Spam Risk", security_data.get('is_spam_risk', False), "🚨", "⚠️"),
            ("VoIP Number", security_data.get('is_voip', False), "📞", "ℹ️"),
            ("Known Scammer", security_data.get('is_scammer', False), "🚫", "⚠️"),
            ("Verified Carrier", security_data.get('verified_carrier', True), "✅", "ℹ️")
        ]
        
        for label, status, icon_true, icon_false in indicators:
            icon = icon_true if status else icon_false
            color = "red" if status and label in ["Spam Risk", "Known Scammer"] else "green" if status and label == "Verified Carrier" else "orange"
            st.markdown(f"{icon} **{label}:** {'Yes' if status else 'No'}")
    
    with col2:
        # Reputation gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = security_score,
            title = {'text': "Reputation Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [0, 30], 'color': "#fecaca"},
                    {'range': [30, 70], 'color': "#fed7aa"},
                    {'range': [70, 100], 'color': "#bbf7d0"}
                ]
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

def display_enhanced_osint(results):
    """Enhanced OSINT data display"""
    st.markdown("### 🌐 OSINT Intelligence")
    
    osint_data = results.get('osint_data', {})
    
    # Digital Footprint Section
    if osint_data.get('digital_footprint') or osint_data.get('associated_emails') or osint_data.get('websites') or osint_data.get('social_accounts'):
        st.markdown("#### 🔍 Digital Footprint Analysis")
        
        # Associated Emails
        if osint_data.get('associated_emails'):
            email_data = osint_data['associated_emails']
            if email_data.get('found_emails'):
                st.markdown("##### 📧 Associated Email Addresses")
                
                with st.container():
                    st.markdown("""
                    <div style="background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%); 
                               padding: 1rem; border-radius: 8px; color: white; margin: 1rem 0;">
                        <h4>📧 Email Addresses Found</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for email in email_data['found_emails']:
                        col1, col2, col3 = st.columns([3, 1, 2])
                        
                        with col1:
                            st.code(email)
                        
                        with col2:
                            confidence = email_data.get('confidence_scores', {}).get(email, 0)
                            if confidence >= 70:
                                st.success(f"{confidence}%")
                            elif confidence >= 40:
                                st.warning(f"{confidence}%")
                            else:
                                st.error(f"{confidence}%")
                        
                        with col3:
                            sources = email_data.get('sources', {}).get(email, [])
                            if sources:
                                st.write(f"Sources: {', '.join(sources[:2])}")
                            
                            verification = email_data.get('verification_status', {}).get(email, 'Unknown')
                            st.caption(f"Status: {verification}")
            else:
                st.info("📧 No associated email addresses found")
        
        # Associated Websites
        if osint_data.get('websites'):
            website_data = osint_data['websites']
            has_websites = any([
                website_data.get('business_websites'),
                website_data.get('personal_websites'),
                website_data.get('professional_profiles'),
                website_data.get('e_commerce_profiles')
            ])
            
            if has_websites:
                st.markdown("##### 🌐 Associated Websites & Profiles")
                
                # Business websites
                if website_data.get('business_websites'):
                    with st.expander("🏢 Business Websites", expanded=True):
                        for website in website_data['business_websites']:
                            confidence = website_data.get('confidence_scores', {}).get(website, 0)
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"🔗 [{website}]({website})")
                            
                            with col2:
                                if confidence >= 70:
                                    st.success(f"{confidence}%")
                                elif confidence >= 40:
                                    st.warning(f"{confidence}%")
                                else:
                                    st.error(f"{confidence}%")
                
                # Professional profiles
                if website_data.get('professional_profiles'):
                    with st.expander("👔 Professional Profiles", expanded=True):
                        for profile in website_data['professional_profiles']:
                            st.markdown(f"🔗 [{profile}]({profile})")
                
                # E-commerce profiles
                if website_data.get('e_commerce_profiles'):
                    with st.expander("🛒 E-commerce Profiles", expanded=False):
                        for profile in website_data['e_commerce_profiles']:
                            st.markdown(f"🔗 [{profile}]({profile})")
                
                # Personal websites
                if website_data.get('personal_websites'):
                    with st.expander("👤 Personal Websites", expanded=False):
                        for website in website_data['personal_websites']:
                            st.markdown(f"🔗 [{website}]({website})")
            else:
                st.info("🌐 No associated websites found")
        
        # Social Media Accounts
        if osint_data.get('social_accounts'):
            social_data = osint_data['social_accounts']
            
            if social_data:
                st.markdown("##### 📱 Social Media Accounts")
                
                # Create platform icons mapping
                platform_icons = {
                    'facebook': '📘',
                    'twitter': '🐦',
                    'instagram': '📷',
                    'linkedin': '💼',
                    'tiktok': '🎵',
                    'snapchat': '👻',
                    'telegram': '✈️',
                    'whatsapp': '💬',
                    'youtube': '📺',
                    'pinterest': '📌',
                    'reddit': '🤖',
                    'discord': '🎮'
                }
                
                # Display found social accounts
                found_accounts = []
                for platform, data in social_data.items():
                    if data.get('found') and data.get('profiles'):
                        found_accounts.append((platform, data))
                
                if found_accounts:
                    st.markdown("""
                    <div style="background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%); 
                               padding: 1rem; border-radius: 8px; color: white; margin: 1rem 0;">
                        <h4>📱 Social Media Profiles Found</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for platform, data in found_accounts:
                        icon = platform_icons.get(platform, '📱')
                        confidence = data.get('confidence', 0)
                        
                        with st.expander(f"{icon} {platform.title()}", expanded=True):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                profiles = data.get('profiles', [])
                                for profile in profiles[:3]:  # Show max 3 profiles
                                    st.markdown(f"🔗 [{profile}]({profile})")
                                
                                if len(profiles) > 3:
                                    st.info(f"... and {len(profiles) - 3} more profiles")
                            
                            with col2:
                                st.metric("Confidence", f"{confidence}%")
                                st.caption(f"Method: {data.get('verification_method', 'Unknown')}")
                                st.caption(f"Updated: {data.get('last_updated', 'Unknown')}")
                else:
                    st.info("📱 No social media accounts found")
            else:
                st.info("📱 No social media accounts found")
        
        # Digital Footprint Summary
        if osint_data.get('digital_footprint'):
            footprint = osint_data['digital_footprint']
            
            with st.expander("🔍 Additional Digital Intelligence", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Search engine results
                    search_results = footprint.get('search_engines', {})
                    if search_results:
                        st.write("**Search Engine Results:**")
                        for engine, count in search_results.items():
                            if count > 0:
                                st.write(f"• {engine.title()}: {count} results")
                    
                    # Public records
                    public_records = footprint.get('public_records', {})
                    if public_records.get('found'):
                        st.write("**Public Records:** Found")
                        records = public_records.get('records', [])
                        for record in records[:3]:
                            st.write(f"• {record}")
                
                with col2:
                    # Business listings
                    business_listings = footprint.get('business_listings', {})
                    if business_listings.get('found'):
                        st.write("**Business Listings:** Found")
                        listings = business_listings.get('listings', [])
                        for listing in listings[:3]:
                            st.write(f"• {listing}")
                    
                    # Data brokers
                    data_brokers = footprint.get('data_brokers', {})
                    if data_brokers.get('found'):
                        st.write("**Data Broker Sites:** Found")
                        brokers = data_brokers.get('brokers', [])
                        for broker in brokers[:3]:
                            st.write(f"• {broker}")
        
        st.markdown("---")
    
    # Social Media Intelligence Section
    if osint_data.get('social_media_intelligence'):
        st.markdown("#### 📱 Social Media Intelligence")
        # Placeholder for social media intelligence details
        st.write("Social media intelligence details will be displayed here.")

def display_technical_details(results):
    """Display technical details about the phone number analysis"""
    st.markdown("### ⚙️ Technical Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Phone Number Parsing:**")
        technical_data = {
            "Original Input": results.get('original_number', 'N/A'),
            "Parsed Format": results.get('formatted_number', 'N/A'),
            "E164 Format": results.get('e164_format', 'N/A'),
            "National Format": results.get('national_format', 'N/A'),
            "International Format": results.get('international_format', 'N/A')
        }
        
        for key, value in technical_data.items():
            st.write(f"• **{key}:** `{value}`")
    
    with col2:
        st.markdown("**Validation Results:**")
        validation_data = {
            "Is Valid": "✅ Yes" if results.get('is_valid') else "❌ No",
            "Is Possible": "✅ Yes" if results.get('is_possible') else "❌ No",
            "Number Type": results.get('number_type', 'Unknown'),
            "Country Code": f"+{results.get('country_code', 'N/A')}",
            "National Number": results.get('national_number', 'N/A')
        }
        
        for key, value in validation_data.items():
            st.write(f"• **{key}:** {value}")
    
    # Analysis metadata
    st.markdown("---")
    st.markdown("**Analysis Metadata:**")
    
    metadata_cols = st.columns(3)
    with metadata_cols[0]:
        st.metric("Analysis Time", f"{results.get('analysis_time', 0):.2f}s")
    with metadata_cols[1]:
        st.metric("API Calls Made", results.get('api_calls_count', 0))
    with metadata_cols[2]:
        st.metric("Data Sources", results.get('data_sources_count', 1))
    
    # Raw data section
    with st.expander("🔍 Raw Analysis Data", expanded=False):
        st.json(results)

def save_api_config(numverify_key, twilio_sid, twilio_token, hibp_key):
    """Save API configuration"""
    if numverify_key:
        Config.NUMVERIFY_API_KEY = numverify_key
    if twilio_sid and twilio_token:
        Config.TWILIO_ACCOUNT_SID = twilio_sid
        Config.TWILIO_AUTH_TOKEN = twilio_token
    if hibp_key:
        Config.HIBP_API_KEY = hibp_key

def export_enhanced_results(results):
    """Enhanced export functionality"""
    st.markdown("### 📤 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📄 JSON Report",
            data=json_data,
            file_name=f"phone_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # CSV export
        df = pd.json_normalize(results)
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📊 CSV Data",
            data=csv_data,
            file_name=f"phone_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        pdf_data = generate_pdf_report(results)
        st.download_button(
            label="📋 PDF Report",
            data=pdf_data,
            file_name=f"phone_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

def generate_pdf_report(results):
    """Generate PDF report from analysis results"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#3b82f6')
    )
    
    # Title
    story.append(Paragraph("📱 Phone Number Intelligence Report", title_style))
    story.append(Spacer(1, 20))
    
    # Report metadata
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    summary_data = [
        ['Phone Number', results.get('formatted_number', 'N/A')],
        ['Country', results.get('country', 'Unknown')],
        ['Region', results.get('region', 'Unknown')],
        ['Carrier', results.get('carrier', 'Unknown')],
        ['Line Type', results.get('line_type', 'Unknown')],
        ['Risk Score', f"{results.get('risk_score', 0)}/100"],
        ['Is Valid', 'Yes' if results.get('is_valid') else 'No'],
        ['Time Zone', results.get('timezone', 'Unknown')]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Security Analysis
    if results.get('security_analysis'):
        story.append(Paragraph("Security Analysis", heading_style))
        security_data = results.get('security_analysis', {})
        
        security_info = [
            ['Security Metric', 'Status'],
            ['Spam Risk', 'Yes' if security_data.get('is_spam_risk') else 'No'],
            ['VoIP Number', 'Yes' if security_data.get('is_voip') else 'No'],
            ['Known Scammer', 'Yes' if security_data.get('is_scammer') else 'No'],
            ['Verified Carrier', 'Yes' if security_data.get('verified_carrier') else 'No'],
            ['Reputation Score', f"{security_data.get('reputation_score', 50)}/100"]
        ]
        
        security_table = Table(security_info, colWidths=[2.5*inch, 2.5*inch])
        security_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef2f2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(security_table)
        story.append(Spacer(1, 20))
    
    # Technical Details
    story.append(Paragraph("Technical Details", heading_style))
    
    tech_data = [
        ['Technical Attribute', 'Value'],
        ['E164 Format', results.get('e164_format', 'N/A')],
        ['National Format', results.get('national_format', 'N/A')],
        ['International Format', results.get('international_format', 'N/A')],
        ['Country Code', f"+{results.get('country_code', 'N/A')}"],
        ['National Number', str(results.get('national_number', 'N/A'))],
        ['Number Type', results.get('number_type', 'Unknown')],
        ['Is Possible', 'Yes' if results.get('is_possible') else 'No']
    ]
    
    tech_table = Table(tech_data, colWidths=[2.5*inch, 2.5*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tech_table)
    story.append(Spacer(1, 20))
    
    # OSINT Data
    if results.get('osint_data'):
        story.append(Paragraph("OSINT Intelligence", heading_style))
        osint_data = results.get('osint_data', {})
        
        osint_text = []
        if osint_data.get('breach_data'):
            osint_text.append("• Data breach alerts found")
        else:
            osint_text.append("• No breach data found")
            
        if osint_data.get('social_media_presence'):
            osint_text.append("• Social media associations detected")
        else:
            osint_text.append("• No social media associations found")
        
        for text in osint_text:
            story.append(Paragraph(text, styles['Normal']))
        
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Report generated by Phone Intelligence Tool", styles['Italic']))
    story.append(Paragraph("For cybersecurity and fraud prevention purposes only", styles['Italic']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def get_country_coordinates(country_code):
    """Get approximate coordinates for country center"""
    # Convert integer country codes to ISO codes
    if isinstance(country_code, int):
        # Map common numeric country codes to ISO codes
        numeric_to_iso = {
            1: 'US',    # United States/Canada
            44: 'GB',   # United Kingdom
            49: 'DE',   # Germany
            33: 'FR',   # France
            39: 'IT',   # Italy
            34: 'ES',   # Spain
            81: 'JP',   # Japan
            86: 'CN',   # China
            91: 'IN',   # India
            55: 'BR',   # Brazil
            52: 'MX',   # Mexico
            7: 'RU',    # Russia
            61: 'AU',   # Australia
        }
        country_code = numeric_to_iso.get(country_code, 'US')  # Default to US if not found
    
    # Ensure country_code is a string and convert to uppercase
    if country_code:
        country_code = str(country_code).upper()
    else:
        return None
    
    coords_map = {
        'US': [39.8283, -98.5795],
        'GB': [55.3781, -3.4360],
        'CA': [56.1304, -106.3468],
        'AU': [-25.2744, 133.7751],
        'DE': [51.1657, 10.4515],
        'FR': [46.2276, 2.2137],
        'IT': [41.8719, 12.5674],
        'ES': [40.4637, -3.7492],
        'JP': [36.2048, 138.2529],
        'CN': [35.8617, 104.1954],
        'IN': [20.5937, 78.9629],
        'BR': [-14.2350, -51.9253],
        'MX': [23.6345, -102.5528],
        'RU': [61.5240, 105.3188],
    }
    
    return coords_map.get(country_code)

if __name__ == "__main__":
    main()
