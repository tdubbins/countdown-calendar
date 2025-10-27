# Authentication Service - Business Logic
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from flask import current_app

from app.utils.json_db import users_db, email_tokens_db
from app.utils.validators import (
    validate_email_address, 
    validate_password_strength, 
    validate_passwords_match,
    validate_required_fields
)

class AuthService:
    """Authentication business logic"""
    
    @staticmethod
    def register_user(email: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Register a new user"""
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
            'email_verified': False
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
        token = AuthService._generate_jwt_token(user['id'], user['email'])
        
        # Update last login
        users_db.update('users', user['id'], {'last_login': datetime.now().isoformat()})
        
        return True, "Login successful", {
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'email_verified': user['email_verified'],
                'created_at': user['created_at']
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
    def _generate_jwt_token(user_id: str, email: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')