# Email Service
import uuid
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

from app.utils.json_db import email_tokens_db, users_db
from app.templates.email_templates import EmailTemplates

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    """Email verification business logic"""
    
    @staticmethod
    def generate_verification_token(user_id: str, email: str) -> str:
        """Generate unique verification token for email verification"""
        current_time = datetime.now()  # Single timestamp for consistency
        token = str(uuid.uuid4())
        expiry_time = current_time + timedelta(hours=24)  # 24-hour expiration
        
        token_data = {
            'token': token,
            'user_id': user_id,
            'email': email,
            'created_at': current_time.isoformat(),
            'expires_at': expiry_time.isoformat(),
            'used': False
        }
        
        email_tokens_db.create('tokens', token, token_data)
        logger.info(f"Generated verification token for user {user_id}")
        return token
    
    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> Tuple[bool, str]:
        """
        Generic email sending function that can send any email template

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get clean email configuration
            email_config = current_app.config.get('EMAIL_CONFIG', {})

            # Validate email configuration
            required_fields = ['server', 'username', 'password', 'sender']
            missing_fields = [field for field in required_fields if not email_config.get(field)]
            if missing_fields:
                logger.error(f"Missing email configuration: {missing_fields}")
                return False, f"Email configuration incomplete: {missing_fields}"

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender']
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Send email using SMTP_SSL
            with smtplib.SMTP_SSL(
                email_config['server'],
                email_config['port']
            ) as server:
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False, "Email authentication failed"
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection failed: {e}")
            return False, "Email server connection failed"
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False, f"Email sending failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected email error: {e}")
            return False, "Email sending failed"

    @staticmethod
    def send_verification_email(email: str, token: str, frontend_url: str = None) -> Tuple[bool, str]:
        """Send verification email using clean configuration and templates

        Args:
            email: Recipient email address
            token: Verification token
            frontend_url: Frontend URL for verification link (passed from frontend request)
        """
        try:
            # Frontend URL must be provided - never use a fallback/default
            if not frontend_url or not frontend_url.strip():
                logger.error("Frontend URL not provided in request - refusing to send email")
                return False, "Frontend URL not provided"

            frontend_url = frontend_url.strip()
            if not frontend_url.startswith(('http://', 'https://')):
                logger.error(f"Invalid frontend URL format: {frontend_url}")
                return False, "Invalid frontend URL format"

            verification_url = f"{frontend_url}/verify-email/{token}"

            # In debug mode, log verification link instead of sending email
            if current_app.debug:
                logger.info(f"[DEBUG] Verification link for {email}: {verification_url}")
                return True, "Verification link logged to console (debug mode)"

            # Generate email content using template
            email_template = EmailTemplates.verification_email(verification_url)

            # Use generic send_email function
            return EmailService.send_email(
                to_email=email,
                subject=email_template['subject'],
                body=email_template['body']
            )

        except Exception as e:
            logger.error(f"Unexpected email error: {e}")
            return False, "Email sending failed"
    
    @staticmethod
    def verify_email_token(token: str) -> Tuple[bool, str, Optional[Dict]]:
        """Verify email using verification token with improved error handling"""
        current_time = datetime.now()  # Single timestamp for consistency
        
        try:
            # Find token
            token_info = email_tokens_db.find_by_id('tokens', token)
            if not token_info:
                logger.warning(f"Invalid verification token attempted: {token}")
                return False, "Invalid token", None
            
            # Check if token is already used
            if token_info.get('used', False):
                logger.warning(f"Already used token attempted: {token}")
                return False, "Token has already been used", None
            
            # Check if token is expired
            expiry_time = datetime.fromisoformat(token_info['expires_at'])
            if current_time > expiry_time:
                logger.warning(f"Expired token attempted: {token}")
                return False, "Token has expired", None
            
            # Find user and update verification status
            user = users_db.find_by_id('users', token_info['user_id'])
            if not user:
                logger.error(f"User not found for token: {token}")
                return False, "User not found", None
            
            # Update user's email verification status
            users_db.update('users', user['id'], {
                'email_verified': True,
                'email_verified_at': current_time.isoformat()
            })
            
            # Mark token as used
            email_tokens_db.update('tokens', token, {
                'used': True,
                'used_at': current_time.isoformat()
            })
            
            # Clean up expired tokens
            EmailService._cleanup_expired_tokens()
            
            logger.info(f"Email verified successfully for user {user['id']}")
            return True, "Email verified successfully! Your account is now active.", {
                'user_id': user['id']
            }
            
        except Exception as e:
            logger.error(f"Error verifying email token {token}: {e}")
            return False, "Verification failed", None
    
    @staticmethod
    def _cleanup_expired_tokens() -> None:
        """Remove expired tokens from storage with logging"""
        try:
            all_tokens = email_tokens_db.find_all('tokens')
            current_time = datetime.now()
            deleted_count = 0
            
            for token_id, token_data in list(all_tokens.items()):
                expiry_time = datetime.fromisoformat(token_data['expires_at'])
                if current_time > expiry_time:
                    email_tokens_db.delete('tokens', token_id)
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired email tokens")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")