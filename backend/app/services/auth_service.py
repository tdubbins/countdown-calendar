# Authentication Service - Business Logic
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from flask import current_app

from app.utils.json_db import users_db, email_tokens_db
from app.utils.validators import (
    validate_email_address,
    validate_password_strength,
    validate_passwords_match,
    validate_required_fields
)
from app.utils.rate_limiter import check_rate_limit, get_rate_limit_update_data

class AuthService:
    """Authentication business logic"""
    
    @staticmethod
    def register_user(email: str, password: str, confirm_password: str, display_name: Optional[str] = None) -> Tuple[bool, str, Optional[Dict]]:
        """Register a new user with optional display name"""
        # Validate required fields
        is_valid, error = validate_required_fields(
            {'email': email, 'password': password, 'confirmPassword': confirm_password},
            ['email', 'password', 'confirmPassword']
        )
        if not is_valid:
            return False, error, None

        # Validate email format
        is_valid, normalized_email, error = validate_email_address(email)
        if not is_valid:
            return False, error, None

        # Validate passwords match
        is_valid, error = validate_passwords_match(password, confirm_password)
        if not is_valid:
            return False, error, None

        # Validate password strength
        is_valid, error = validate_password_strength(password)
        if not is_valid:
            return False, error, None

        # Check if email already exists
        existing_user = users_db.find_by_field('users', 'email', normalized_email.lower())
        if existing_user:
            return False, "Email address is already registered", None

        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = AuthService._hash_password(password)

        user_data = {
            'id': user_id,
            'email': normalized_email,
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat(),
            'email_verified': False,
            'calendar_ids': [],  # Initialize empty calendar_ids array
            'display_name': display_name.strip() if display_name else None  # Optional display name
        }

        # Save user to database
        users_db.create('users', user_id, user_data)

        return True, "User registered successfully", {
            'user_id': user_id,
            'email': normalized_email
        }
    
    @staticmethod
    def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Authenticate user login"""
        # Validate required fields
        is_valid, error = validate_required_fields(
            {'email': email, 'password': password},
            ['email', 'password']
        )
        if not is_valid:
            return False, error, None
        
        # Validate email format
        is_valid, normalized_email, error = validate_email_address(email)
        if not is_valid:
            return False, error, None
        
        # Find user by email
        user = users_db.find_by_field('users', 'email', normalized_email.lower())
        if not user:
            return False, "Invalid email or password", None
        
        # Check if user's email is verified
        if not user.get('email_verified', False):
            return False, "Please verify your email before logging in", None
        
        # Verify password
        if not AuthService._verify_password(user['password_hash'], password):
            return False, "Invalid email or password", None
        
        # Generate JWT token
        token = AuthService._generate_jwt_token(user['id'])
        
        # Update last login
        users_db.update('users', user['id'], {'last_login': datetime.now().isoformat()})
        
        return True, "Login successful", {
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'email_verified': user['email_verified'],
                'created_at': user['created_at'],
                'display_name': user.get('display_name')  # Include display name if present
            }
        }
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        user = users_db.find_by_id('users', user_id)
        if user:
            # Remove password hash from response
            user_copy = user.copy()
            user_copy.pop('password_hash', None)
            return user_copy
        return None

    @staticmethod
    def update_user_profile(user_id: str, update_fields: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict]]:
        """
        Update user profile information

        Args:
            user_id: User's unique identifier
            update_fields: Dict containing fields to update (e.g., {'email': '...', 'display_name': '...'})

        Returns:
            Tuple of (success, message, result_data)
        """
        # Get current user
        user = users_db.find_by_id('users', user_id)
        if not user:
            return False, "User not found", None

        update_data = {}
        changes = []

        # Handle email update
        if 'email' in update_fields:
            email = update_fields['email']

            if not email:
                return False, "Email cannot be empty", None

            if email != user.get('email'):
                # Validate email format
                is_valid, normalized_email, error = validate_email_address(email)
                if not is_valid:
                    return False, error, None

                # Check if new email is already taken
                existing_user = users_db.find_by_field('users', 'email', normalized_email.lower())
                if existing_user and existing_user['id'] != user_id:
                    return False, "Email address is already in use", None

                update_data['email'] = normalized_email
                changes.append('email')

        # Handle display name update (can be None to clear it)
        if 'display_name' in update_fields:
            display_name = update_fields['display_name']
            # Strip whitespace and convert empty strings to None
            cleaned_display_name = display_name.strip() if display_name else None
            current_display_name = user.get('display_name')

            # Check if display name is actually changing
            if cleaned_display_name != current_display_name:
                update_data['display_name'] = cleaned_display_name
                changes.append('display name')

        # Check if there are any changes
        if not update_data:
            return False, "No changes detected", None

        # Add updated timestamp
        update_data['updated_at'] = datetime.now().isoformat()

        # Update user in database
        users_db.update('users', user_id, update_data)

        # Get updated user data
        updated_user = AuthService.get_user_by_id(user_id)

        return True, "Profile updated successfully", {
            'user': updated_user,
            'changes': changes
        }

    @staticmethod
    def change_user_password(user_id: str, current_password: str, new_password: str, confirm_password: str) -> Tuple[bool, str]:
        """
        Change user's password with current password verification

        Args:
            user_id: User's unique identifier
            current_password: Current password for verification
            new_password: New password to set
            confirm_password: Confirmation of new password

        Returns:
            Tuple of (success, message)
        """
        # Get current user
        user = users_db.find_by_id('users', user_id)
        if not user:
            return False, "User not found"

        # Verify current password
        if not AuthService._verify_password(user['password_hash'], current_password):
            return False, "Current password is incorrect"

        # Validate passwords match
        is_valid, error = validate_passwords_match(new_password, confirm_password)
        if not is_valid:
            return False, error

        # Validate new password strength
        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            return False, error

        # Check that new password is different from current
        if AuthService._verify_password(user['password_hash'], new_password):
            return False, "New password must be different from current password"

        # Hash new password
        new_password_hash = AuthService._hash_password(new_password)

        # Update password in database
        update_data = {
            'password_hash': new_password_hash,
            'password_changed_at': datetime.now().isoformat()
        }
        users_db.update('users', user_id, update_data)

        return True, "Password changed successfully"

    @staticmethod
    def delete_user_account(user_id: str, password: str) -> Tuple[bool, str]:
        """
        Delete user account and ALL associated data (GDPR compliant)

        Args:
            user_id: User's unique identifier
            password: Current password for verification

        Returns:
            Tuple of (success, message)
        """
        # Get current user
        user = users_db.find_by_id('users', user_id)
        if not user:
            return False, "User not found"

        # Verify password (security requirement)
        if not AuthService._verify_password(user['password_hash'], password):
            return False, "Password is incorrect"

        # Import calendars_db for folder deletion
        from app.utils.json_db import calendars_db, email_tokens_db, tasks_db

        # 1. Delete all calendar folders (includes videos, thumbnails, meta.json)
        calendar_ids = user.get('calendar_ids', [])
        for calendar_id in calendar_ids:
            try:
                calendars_db.delete_calendar_folder(calendar_id)
                print(f"Deleted calendar folder: {calendar_id}")
            except Exception as e:
                print(f"Warning: Failed to delete calendar {calendar_id}: {e}")
                # Continue deletion process even if one calendar fails

        # 2. Delete all email verification tokens for this user
        try:
            all_tokens = email_tokens_db.find_all('tokens')
            for token_id, token_data in list(all_tokens.items()):
                if token_data.get('user_id') == user_id:
                    email_tokens_db.delete('tokens', token_id)
                    print(f"Deleted email token: {token_id}")
        except Exception as e:
            print(f"Warning: Failed to delete email tokens: {e}")

        # 3. Delete all background tasks for this user
        try:
            all_tasks = tasks_db.find_all('tasks')
            for task_id, task_data in list(all_tasks.items()):
                if task_data.get('user_id') == user_id:
                    tasks_db.delete('tasks', task_id)
                    print(f"Deleted task: {task_id}")
        except Exception as e:
            print(f"Warning: Failed to delete tasks: {e}")

        # 4. Delete user record (last step - confirms complete deletion)
        try:
            users_db.delete('users', user_id)
            print(f"Deleted user: {user_id}")
        except Exception as e:
            print(f"Error: Failed to delete user record: {e}")
            return False, "Failed to delete user account"

        return True, "Account deleted successfully"

    @staticmethod
    def verify_jwt_token(token: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def _verify_password(stored_hash: str, provided_password: str) -> bool:
        """Verify password against stored hash"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    @staticmethod
    def resend_verification_email(email: str) -> Tuple[bool, str]:
        """Resend verification email to unverified user"""
        # Validate email format
        is_valid, normalized_email, error = validate_email_address(email)
        if not is_valid:
            return False, error

        # Find user by email
        user = users_db.find_by_field('users', 'email', normalized_email.lower())

        # Generic response for privacy (don't reveal if user exists)
        # But still handle the logic correctly
        if not user:
            return True, "If this email is registered and unverified, a new verification link has been sent."

        # Check if already verified
        if user.get('email_verified', False):
            return True, "If this email is registered and unverified, a new verification link has been sent."

        # Check rate limiting using utility (3 requests per hour)
        is_allowed, new_count, rate_limit_error = check_rate_limit(
            user=user,
            action='verification_email',
            limit=3,
            window_hours=1
        )

        if not is_allowed:
            return False, rate_limit_error

        # Invalidate all old unused tokens for this user
        from app.services.email_service import EmailService
        all_tokens = email_tokens_db.find_all('tokens')
        for token_id, token_data in all_tokens.items():
            if token_data.get('user_id') == user['id'] and not token_data.get('used', False):
                email_tokens_db.update('tokens', token_id, {'used': True})

        # Generate new token and send email
        verification_token = EmailService.generate_verification_token(
            user['id'],
            user['email']
        )
        email_sent, email_message = EmailService.send_verification_email(
            user['email'],
            verification_token
        )

        # Update rate limiting tracking
        rate_limit_data = get_rate_limit_update_data('verification_email', new_count)
        users_db.update('users', user['id'], rate_limit_data)

        if not email_sent:
            # Don't reveal email sending failure to user (security)
            # But log it for debugging
            print(f"Warning: Failed to resend verification email: {email_message}")

        return True, "Verification email sent! Please check your inbox and spam folder."

    @staticmethod
    def _generate_jwt_token(user_id: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),
            'iat': datetime.now(timezone.utc)
        }

        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')