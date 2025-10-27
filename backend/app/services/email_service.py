# Email Service - Email Verification Business Logic
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
from flask_mail import Message
from flask import current_app

from app import mail
from app.utils.json_db import email_tokens_db, users_db

class EmailService:
    """Email verification business logic"""
    
    @staticmethod
    def generate_verification_token(user_id: str, email: str) -> str:
        """Generate unique verification token for email verification"""
        token = str(uuid.uuid4())
        expiry_time = datetime.now() + timedelta(hours=24)  # 24-hour expiration
        
        token_data = {
            'token': token,
            'user_id': user_id,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'expires_at': expiry_time.isoformat(),
            'used': False
        }
        
        email_tokens_db.create('tokens', token, token_data)
        return token
    
    @staticmethod
    def send_verification_email(email: str, token: str) -> Tuple[bool, str]:
        """Send verification email to user"""
        try:
            # Create verification URL
            verification_url = f"http://localhost:8100/verify-email/{token}"
            
            # Create email message
            msg = Message(
                subject="Verify Your Email - Countdown Calendar",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            
            # Email body (HTML)
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #667eea;">📅 Countdown Calendar</h1>
                    </div>
                    
                    <h2>Welcome! Please verify your email address</h2>
                    
                    <p>Thank you for registering with Countdown Calendar! To complete your registration and activate your account, please click the button below to verify your email address.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="display: inline-block; padding: 15px 30px; background-color: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                            Verify Email Address
                        </a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                    
                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 14px; color: #666;">
                        <p><strong>Important:</strong> This verification link will expire in 24 hours.</p>
                        <p>If you didn't create this account, please ignore this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version (fallback)
            msg.body = f"""
            Welcome to Countdown Calendar!
            
            Please verify your email address by clicking this link:
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create this account, please ignore this email.
            """
            
            # Send email
            mail.send(msg)
            return True, "Verification email sent successfully"
            
        except Exception as e:
            print(f"Email sending error: {str(e)}")
            return False, f"Failed to send email: {str(e)}"
    
    @staticmethod
    def verify_email_token(token: str) -> Tuple[bool, str, Optional[Dict]]:
        """Verify email using verification token"""
        # Find token
        token_info = email_tokens_db.find_by_id('tokens', token)
        if not token_info:
            return False, "Invalid token", None
        
        # Check if token is already used
        if token_info.get('used', False):
            return False, "Token has already been used", None
        
        # Check if token is expired
        expiry_time = datetime.fromisoformat(token_info['expires_at'])
        if datetime.now() > expiry_time:
            return False, "Token has expired", None
        
        # Find user and update verification status
        user = users_db.find_by_id('users', token_info['user_id'])
        if not user:
            return False, "User not found", None
        
        # Update user's email verification status
        users_db.update('users', user['id'], {
            'email_verified': True,
            'email_verified_at': datetime.now().isoformat()
        })
        
        # Mark token as used
        email_tokens_db.update('tokens', token, {
            'used': True,
            'used_at': datetime.now().isoformat()
        })
        
        # Clean up expired tokens (optional)
        EmailService._cleanup_expired_tokens()
        
        return True, "Email verified successfully! Your account is now active.", {
            'user_id': user['id']
        }
    
    @staticmethod
    def _cleanup_expired_tokens() -> None:
        """Remove expired tokens from storage"""
        all_tokens = email_tokens_db.find_all('tokens')
        current_time = datetime.now()
        
        for token_id, token_data in list(all_tokens.items()):
            expiry_time = datetime.fromisoformat(token_data['expires_at'])
            if current_time > expiry_time:
                email_tokens_db.delete('tokens', token_id)