# Phone Number Intelligence Tool

A comprehensive phone number analysis tool designed for cybersecurity professionals, fraud investigators, and security researchers. This tool provides detailed intelligence about phone numbers while maintaining strict ethical and legal compliance.

## ⚠️ Legal Disclaimer

**IMPORTANT:** This tool is designed for legitimate cybersecurity research, fraud prevention, and authorized investigations only. Users must ensure compliance with all applicable laws and regulations, including privacy laws (GDPR, CCPA, etc.) and obtain proper authorization before analyzing phone numbers.

## Features

### Core Analysis
- **Phone Number Parsing & Validation**: Supports international and local formats
- **Geographic Information**: Country, region, and timezone identification
- **Carrier Intelligence**: Network provider, line type (mobile/landline/VoIP)
- **Security Assessment**: Spam risk analysis and reputation scoring
- **Technical Details**: Multiple format outputs (E164, international, national)

### Advanced Intelligence
- **OSINT Enrichment**: Open source intelligence gathering
- **Breach Database Checking**: Integration with HaveIBeenPwned API
- **Risk Scoring**: Comprehensive risk assessment (0-100 scale)
- **Visual Analytics**: Interactive maps and risk visualizations
- **Audit Logging**: Complete activity tracking for compliance

### API Integrations
- **Numverify**: Enhanced carrier and validation data
- **Twilio Lookup**: Advanced security and reputation information
- **HaveIBeenPwned**: Breach database checking
- **Extensible Plugin System**: Easy integration of additional data sources

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project files**

2. **Install dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Set up API keys** (optional but recommended):
   
   Create a `.env` file in the project root:
   \`\`\`env
   NUMVERIFY_API_KEY=your_numverify_key_here
   TWILIO_ACCOUNT_SID=your_twilio_sid_here
   TWILIO_AUTH_TOKEN=your_twilio_token_here
   HIBP_API_KEY=your_hibp_key_here
   \`\`\`

4. **Run the application**:
   \`\`\`bash
   streamlit run app.py
   \`\`\`

5. **Access the web interface**:
   Open your browser to `http://localhost:8501`

## API Key Setup

### Numverify API
1. Sign up at [numverify.com](https://numverify.com)
2. Get your free API key (1000 requests/month)
3. Add to `.env` file or enter in the web interface

### Twilio Lookup API
1. Create account at [twilio.com](https://twilio.com)
2. Get Account SID and Auth Token from console
3. Add to `.env` file or enter in the web interface

### HaveIBeenPwned API
1. Subscribe at [haveibeenpwned.com/API/Key](https://haveibeenpwned.com/API/Key)
2. Get your API key
3. Add to `.env` file or enter in the web interface

## Usage

### Basic Analysis
1. Enter a phone number in any format
2. Click "Analyze" to start the investigation
3. Review the comprehensive results across multiple tabs

### Export Results
- **JSON Format**: Complete data export for further analysis
- **CSV Format**: Spreadsheet-compatible format for reporting

### Security Features
- All analysis activities are logged for audit purposes
- Legal disclaimer must be acknowledged before use
- No unauthorized geolocation or privacy violations
- Strict compliance with data protection regulations

## Plugin System

The tool includes an extensible plugin architecture for adding custom analysis capabilities:

### Creating a Plugin
\`\`\`python
from plugins import PluginBase

class MyPlugin(PluginBase):
    def __init__(self):
        super().__init__("My Plugin", "1.0.0")
        self.description = "Custom analysis plugin"
    
    def analyze(self, phone_number, context=None):
        # Your analysis logic here
        return {'custom_data': 'analysis_result'}
\`\`\`

### Available Plugins
- **Fraud Detection**: ML-based fraud probability scoring
- **Custom integrations**: Easy to add new data sources

## Architecture

\`\`\`
phone-intelligence-tool/
├── app.py                 # Main Streamlit application
├── phone_intelligence.py  # Core analysis engine
├── config.py             # Configuration management
├── plugins/              # Plugin system
│   ├── __init__.py
│   └── fraud_detection.py
├── requirements.txt      # Python dependencies
└── README.md            # This file
\`\`\`

## Security Considerations

### Data Protection
- No persistent storage of analyzed phone numbers
- Secure API key handling
- Comprehensive audit logging
- GDPR/CCPA compliance features

### Ethical Use
- Built-in legal disclaimers
- Usage warnings and guidelines
- Audit trail for accountability
- No unauthorized surveillance capabilities

## Troubleshooting

### Common Issues

**"Invalid phone number format"**
- Try different formats: +1-555-123-4567, (555) 123-4567
- Include country code for international numbers

**"API key not working"**
- Verify API keys are correctly entered
- Check API quotas and billing status
- Ensure proper permissions for API keys

**"Map not displaying"**
- Check internet connection
- Verify country code is recognized
- Some regions may not have map data

### Logging
Check `phone_intelligence.log` for detailed error information and analysis history.

## Contributing

This tool is designed for professional cybersecurity use. Contributions should focus on:
- Enhanced security analysis capabilities
- Additional legitimate data source integrations
- Improved compliance and audit features
- Better visualization and reporting

## License

This tool is provided for educational and legitimate cybersecurity purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations.

## Support

For technical issues or questions about legitimate use cases, please review the documentation and logs first. This tool is designed for professional cybersecurity practitioners who understand the legal and ethical implications of phone number intelligence gathering.
# phone-osint-GUI
