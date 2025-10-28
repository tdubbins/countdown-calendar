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

def validate_calendar_title(title: str) -> Tuple[bool, str]:
    """Validate calendar title meets requirements"""
    if not title or not title.strip():
        return False, "Title is required"
    
    title = title.strip()
    if len(title) < 1:
        return False, "Title cannot be empty"
    
    if len(title) > 100:
        return False, "Title must be 100 characters or less"
    
    return True, title

def validate_calendar_duration(duration) -> Tuple[bool, int, str]:
    """Validate calendar duration is between 1-31 days"""
    try:
        duration_int = int(duration)
        if duration_int < 1:
            return False, 0, "Duration must be at least 1 day"
        if duration_int > 31:
            return False, 0, "Duration cannot exceed 31 days"
        return True, duration_int, ""
    except (ValueError, TypeError):
        return False, 0, "Duration must be a valid number"

def validate_calendar_start_date(start_date: str) -> Tuple[bool, str, str]:
    """Validate start date format and value"""
    import re
    from datetime import datetime
    
    if not start_date or not start_date.strip():
        return False, "", "Start date is required"
    
    # Validate ISO date format (YYYY-MM-DD)
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', start_date.strip()):
        return False, "", "Start date must be in YYYY-MM-DD format"
    
    try:
        # Validate date is parseable
        datetime.strptime(start_date.strip(), '%Y-%m-%d')
        return True, start_date.strip(), ""
    except ValueError:
        return False, "", "Invalid date provided"