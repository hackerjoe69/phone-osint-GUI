#!/usr/bin/env python3
"""
Environment setup script for Phone Intelligence Tool
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file template"""
    env_template = """# Phone Intelligence Tool Configuration
# Add your API keys here (optional but recommended for full functionality)

# Numverify API (https://numverify.com)
NUMVERIFY_API_KEY=

# Twilio API (https://twilio.com)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=

# HaveIBeenPwned API (https://haveibeenpwned.com/API/Key)
HIBP_API_KEY=

# Application Settings
LOG_LEVEL=INFO
MAX_REQUESTS_PER_HOUR=100
ENABLE_AUDIT_LOG=true
ENABLE_OSINT_ENRICHMENT=true
ENABLE_BREACH_CHECKING=true
ENABLE_SOCIAL_MEDIA_LOOKUP=false
"""
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(env_template)
        print("✅ Created .env file template")
        print("📝 Please edit .env file to add your API keys")
    else:
        print("ℹ️  .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "exports", "plugins"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up Phone Intelligence Tool...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file to add your API keys (optional)")
    print("2. Run: streamlit run app.py")
    print("3. Open browser to http://localhost:8501")
    print("\n⚠️  Remember to review the legal disclaimer before use!")

if __name__ == "__main__":
    main()
