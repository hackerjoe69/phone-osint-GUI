import os
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration class for API keys and settings"""
    
    # API Keys (set via environment variables or Streamlit inputs)
    NUMVERIFY_API_KEY: str = os.getenv('NUMVERIFY_API_KEY', '')
    TWILIO_ACCOUNT_SID: str = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN: str = os.getenv('TWILIO_AUTH_TOKEN', '')
    HIBP_API_KEY: str = os.getenv('HIBP_API_KEY', '')
    
    # Application settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_REQUESTS_PER_HOUR: int = int(os.getenv('MAX_REQUESTS_PER_HOUR', '100'))
    
    # Security settings
    ENABLE_AUDIT_LOG: bool = os.getenv('ENABLE_AUDIT_LOG', 'true').lower() == 'true'
    REQUIRE_DISCLAIMER_ACCEPTANCE: bool = True
    
    # Feature flags
    ENABLE_OSINT_ENRICHMENT: bool = os.getenv('ENABLE_OSINT_ENRICHMENT', 'true').lower() == 'true'
    ENABLE_BREACH_CHECKING: bool = os.getenv('ENABLE_BREACH_CHECKING', 'true').lower() == 'true'
    ENABLE_SOCIAL_MEDIA_LOOKUP: bool = os.getenv('ENABLE_SOCIAL_MEDIA_LOOKUP', 'false').lower() == 'true'
