#!/usr/bin/env python3
"""
Email Configuration Test Script - Using Working SMTP_SSL Method
Test your custom domain email configuration before using it in the app
"""

import os
import smtplib
import pytest
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    """Test SMTP connection with your custom domain using SMTP_SSL"""
    
    # Get configuration from environment (matching working script)
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 465))
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    
    # Validate configuration
    if not all([smtp_server, email_user, email_password]):
        print("❌ Error: Missing email configuration!")
        print("Required environment variables:")
        print("  - SMTP_SERVER")
        print("  - EMAIL_USER")
        print("  - EMAIL_PASSWORD")
        return False
    
    print(f"🔧 Testing email configuration (SMTP_SSL method):")
    print(f"   SMTP Server: {smtp_server}")
    print(f"   Port: {smtp_port}")
    print(f"   Username: {email_user}")
    print()
    
    try:
        # Use SMTP_SSL directly (matching working script)
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            # Login
            server.login(email_user, email_password)
            print("✅ SMTP connection successful!")

    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Check your email credentials")
        pytest.fail(f"SMTP Authentication failed: {e}")
    except smtplib.SMTPConnectError as e:
        print(f"❌ Connection failed: {e}")
        print("   Check your SMTP server and port settings")
        pytest.fail(f"SMTP Connection failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        pytest.fail(f"SMTP test failed: {e}")

def send_test_email(to_email):
    """Send a test email using the working SMTP_SSL method"""
    
    # Get configuration from environment
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 465))
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    default_sender = os.environ.get('MAIL_DEFAULT_SENDER', email_user)
    
    try:
        # Create message (matching working script format)
        msg = MIMEMultipart()
        msg['From'] = default_sender
        msg['To'] = to_email
        msg['Subject'] = 'Email Verification Test'
        
        # Simple body content
        body = 'This is a test email from Countdown Calendar. Your email configuration is working!'
        msg.attach(MIMEText(body, 'plain'))
        
        # Use SMTP_SSL directly (matching working script)
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            # Login
            server.login(email_user, email_password)
            
            # Send email
            server.send_message(msg)

        print(f"✅ Test email sent successfully to {to_email}")
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        pytest.fail(f"Failed to send test email: {e}")

def main():
    """Main test function"""
    print("📧 Countdown Calendar Email Configuration Test")
    print("=" * 50)
    
    # Test connection
    if not test_smtp_connection():
        print("\n💡 Check your .env file configuration")
        return
    
    # Offer to send test email
    print("\n🔬 Would you like to send a test email? (y/n): ", end="")
    if input().lower().startswith('y'):
        print("Enter test email address: ", end="")
        test_email = input().strip()
        if test_email:
            send_test_email(test_email)
    
    print("\n🎉 Email configuration test complete!")

if __name__ == "__main__":
    main()