# Input Validation Utilities
import re
from email_validator import validate_email, EmailNotValidError
from typing import Tuple

def validate_email_address(email: str) -> Tuple[bool, str, str]:
    """Validate email address format"""
    try:
        valid_email = validate_email(email.strip())
        return True, valid_email.email, ""
    except EmailNotValidError:
        return False, "", "Invalid email format"

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, str]:
    """Validate that all required fields are present"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == "":
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, ""

def validate_passwords_match(password: str, confirm_password: str) -> Tuple[bool, str]:
    """Validate that passwords match"""
    if password != confirm_password:
        return False, "Passwords do not match"
    return True, ""