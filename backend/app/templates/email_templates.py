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

    @staticmethod
    def password_changed(email: str, app_name: str = "Countdown Calendar") -> dict:
        """
        Generate password change notification template

        Args:
            email: User's email address
            app_name: Application name for branding

        Returns:
            dict: Contains 'subject' and 'body' keys
        """
        return {
            'subject': f"Password Changed - {app_name}",
            'body': f"""Password Change Confirmation

Your {app_name} password was successfully changed.

If you made this change, no action is needed. You can continue using your account with your new password.

If you did NOT change your password, please contact support immediately as your account may be compromised.

For security, you have been logged out of all devices. Please log in again with your new password.

Best regards,
{app_name} Team"""
        }

    @staticmethod
    def account_deleted(email: str, app_name: str = "Countdown Calendar") -> dict:
        """
        Generate account deletion confirmation template

        Args:
            email: User's email address
            app_name: Application name for branding

        Returns:
            dict: Contains 'subject' and 'body' keys
        """
        return {
            'subject': f"Account Deleted - {app_name}",
            'body': f"""Account Deletion Confirmation

Your {app_name} account has been permanently deleted.

All your data has been removed:
- User account and profile information
- All calendars and their content
- All uploaded videos and media files
- All associated metadata

This action cannot be undone.

We're sorry to see you go. If you change your mind, you're always welcome to create a new account.

If you did not request this deletion, please contact support immediately.

Best regards,
{app_name} Team"""
        }

    @staticmethod
    def profile_updated(email: str, changes: list, app_name: str = "Countdown Calendar") -> dict:
        """
        Generate profile update notification template

        Args:
            email: User's email address
            changes: List of fields that were changed (e.g., ['email', 'display name'])
            app_name: Application name for branding

        Returns:
            dict: Contains 'subject' and 'body' keys
        """
        changes_text = ", ".join(changes) if changes else "profile information"

        return {
            'subject': f"Profile Updated - {app_name}",
            'body': f"""Profile Update Notification

Your {app_name} profile was recently updated.

Changed fields: {changes_text}

If you made these changes, no action is needed.

If you did not make these changes, please contact support immediately.

Best regards,
{app_name} Team"""
        }