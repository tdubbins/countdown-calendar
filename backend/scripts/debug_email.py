#!/usr/bin/env python3
"""
Debug script to test Flask-Mail with the actual app configuration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from dotenv import load_dotenv
from app import create_app
from app.services.email_service import EmailService

# Load environment variables
load_dotenv()

# Create Flask app context
app = create_app()

def test_verification_email():
    """Test sending verification email using the actual EmailService"""
    
    with app.app_context():
        print("🧪 Testing Flask-Mail with actual EmailService...")
        
        # Generate a test token
        test_token = EmailService.generate_verification_token(
            "test-user-id", 
            "test@dubbins.de"
        )
        
        print(f"✅ Generated token: {test_token}")
        
        # Try to send verification email
        print("📧 Attempting to send verification email...")
        success, message = EmailService.send_verification_email(
            "test@dubbins.de", 
            test_token
        )
        
        if success:
            print(f"✅ Email sent successfully: {message}")
        else:
            print(f"❌ Email failed: {message}")
        
        return success

if __name__ == "__main__":
    try:
        test_verification_email()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()