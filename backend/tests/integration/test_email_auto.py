#!/usr/bin/env python3
"""
Automated Email Test - No prompts
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_test_email():
    """Send a test email automatically"""
    
    # Get configuration from environment
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 465))
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    default_sender = os.environ.get('MAIL_DEFAULT_SENDER', email_user)
    
    to_email = 'test@dubbins.de'  # Test recipient
    
    print(f"📧 Testing email send to {to_email}")
    print(f"   Server: {smtp_server}:{smtp_port}")
    print(f"   From: {default_sender}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = default_sender
        msg['To'] = to_email
        msg['Subject'] = 'Email Verification Test'
        
        # Simple body content
        body = 'This is a test email from Countdown Calendar. Your email configuration is working!'
        msg.attach(MIMEText(body, 'plain'))
        
        # Use SMTP_SSL directly
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            # Login
            server.login(email_user, email_password)
            
            # Send email
            server.send_message(msg)
        
        print(f"✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

if __name__ == "__main__":
    send_test_email()