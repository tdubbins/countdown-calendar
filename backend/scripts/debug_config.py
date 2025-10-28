#!/usr/bin/env python3
"""
Debug script to check Flask-Mail configuration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask app context
app = create_app()

def debug_mail_config():
    """Debug Flask-Mail configuration"""
    
    with app.app_context():
        print("🔧 Clean Email Configuration:")
        email_config = app.config.get('EMAIL_CONFIG', {})
        print(f"   Server: {email_config.get('server')}")
        print(f"   Port: {email_config.get('port')}")
        print(f"   Username: {email_config.get('username')}")
        print(f"   Password: {'***' if email_config.get('password') else 'None'}")
        print(f"   Sender: {email_config.get('sender')}")
        print(f"   Use SSL: {email_config.get('use_ssl')}")
        print(f"   Use TLS: {email_config.get('use_tls')}")
        print(f"   Timeout: {email_config.get('timeout')}")
        
        print(f"\n📧 Frontend URL: {app.config.get('FRONTEND_URL')}")
        print(f"📧 Backend URL: {app.config.get('BACKEND_URL')}")
        
        print("\n🌍 Environment Variables:")
        print(f"   SMTP_SERVER: {os.environ.get('SMTP_SERVER')}")
        print(f"   SMTP_PORT: {os.environ.get('SMTP_PORT')}")
        print(f"   EMAIL_USER: {os.environ.get('EMAIL_USER')}")
        print(f"   EMAIL_PASSWORD: {'***' if os.environ.get('EMAIL_PASSWORD') else 'None'}")
        print(f"   MAIL_USE_TLS: {os.environ.get('MAIL_USE_TLS')}")
        print(f"   MAIL_USE_SSL: {os.environ.get('MAIL_USE_SSL')}")

if __name__ == "__main__":
    debug_mail_config()