# Email Templates - Centralized email content management

class EmailTemplates:
    """Centralized email template management"""
    
    @staticmethod
    def verification_email(verification_url: str, app_name: str = "Countdown Calendar") -> dict:
        """
        Generate email verification template
        
        Args:
            verification_url: URL for email verification
            app_name: Application name for branding
            
        Returns:
            dict: Contains 'subject' and 'body' keys
        """
        return {
            'subject': f"Email Verification - {app_name}",
            'body': f"""Welcome to {app_name}!

Please verify your email address by clicking this link:
{verification_url}

This link will expire in 24 hours.

If you did not create this account, please ignore this email.

Thank you!
{app_name} Team"""
        }
    
    @staticmethod
    def password_reset(reset_url: str, app_name: str = "Countdown Calendar") -> dict:
        """
        Generate password reset template (for future use)
        
        Args:
            reset_url: URL for password reset
            app_name: Application name for branding
            
        Returns:
            dict: Contains 'subject' and 'body' keys
        """
        return {
            'subject': f"Password Reset - {app_name}",
            'body': f"""Password Reset Request

Someone requested a password reset for your {app_name} account.

Click this link to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this reset, please ignore this email.

{app_name} Team"""
        }