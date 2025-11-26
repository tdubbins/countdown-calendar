# Input Validation Utilities
import re
import os
import subprocess
from pathlib import Path
from email_validator import validate_email, EmailNotValidError
from typing import Tuple, Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ============================================================================
# Constants
# ============================================================================

# Valid door ordering options for calendar sharing
VALID_DOOR_ORDERS = ['sequential', 'random']

def validate_email_address(email: str) -> Tuple[bool, str, str]:
    """Validate email address format"""
    try:
        valid_email = validate_email(email.strip())
        return True, valid_email.normalized, ""
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

def validate_calendar_title(title: str) -> Tuple[bool, str, str]:
    """
    Validate calendar title meets requirements

    Args:
        title: Calendar title string

    Returns:
        Tuple of (is_valid, clean_title, error_message)
    """
    if not title or not title.strip():
        return False, "", "Title is required"

    title = title.strip()
    if len(title) < 1:
        return False, "", "Title cannot be empty"

    if len(title) > 100:
        return False, "", "Title must be 100 characters or less"

    return True, title, ""

def validate_calendar_description(description: str) -> Tuple[bool, str, str]:
    """
    Validate and sanitize calendar description.

    Args:
        description: Calendar description string (optional)

    Returns:
        Tuple of (is_valid, clean_description, error_message)
    """
    # Description is optional, empty is valid
    if not description or not description.strip():
        return True, "", ""

    description = description.strip()

    # Remove HTML tags and dangerous characters for XSS prevention
    import re

    # Remove HTML tags
    clean_desc = re.sub(r'<[^>]*>', '', description)

    # Remove JavaScript protocol handlers
    clean_desc = re.sub(r'javascript:', '', clean_desc, flags=re.IGNORECASE)
    clean_desc = re.sub(r'data:', '', clean_desc, flags=re.IGNORECASE)
    clean_desc = re.sub(r'vbscript:', '', clean_desc, flags=re.IGNORECASE)

    # Remove event handler attributes
    clean_desc = re.sub(r'on\w+\s*=', '', clean_desc, flags=re.IGNORECASE)

    # Validate length after sanitization
    if len(clean_desc) > 500:
        return False, "", "Description must be 500 characters or less"

    if len(clean_desc) > 0 and len(clean_desc) < 3:
        return False, "", "Description must be at least 3 characters if provided"

    return True, clean_desc, ""

def validate_uniqueness_in_collection(
    collection: list, 
    field_name: str, 
    value: str, 
    exclude_id: str = None,
    id_field: str = 'id',
    case_sensitive: bool = False
) -> Tuple[bool, str, str]:
    """
    Generic validator for uniqueness within a collection
    
    Args:
        collection: List of items to check against
        field_name: Name of the field to check for uniqueness
        value: The value to validate
        exclude_id: Optional ID to exclude from check (for updates)
        id_field: Field name that contains the ID (default: 'id')
        case_sensitive: Whether comparison should be case sensitive
    
    Returns:
        Tuple of (is_valid, clean_value, error_message)
    """
    if not collection:
        return True, value.strip(), ""
    
    clean_value = value.strip()
    compare_value = clean_value if case_sensitive else clean_value.lower()
    
    for item in collection:
        existing_value = item.get(field_name, '')
        existing_compare = existing_value if case_sensitive else existing_value.lower().strip()
        existing_id = item.get(id_field, '')
        
        # Check if value conflicts with existing item (but allow updating same item)
        if (existing_compare == compare_value and existing_id != exclude_id):
            return False, "", f"A {field_name} with this name already exists. Please choose a different name."
    
    return True, clean_value, ""

def validate_calendar_title_uniqueness(user_calendars: list, title: str, calendar_id: str = None) -> Tuple[bool, str, str]:
    """
    Validate calendar title is unique for this user
    
    Args:
        user_calendars: List of user's existing calendars
        title: The title to validate
        calendar_id: Optional calendar ID (for updates - allow same title when editing same calendar)
    
    Returns:
        Tuple of (is_valid, clean_title, error_message)
    """
    is_valid, clean_title, error = validate_uniqueness_in_collection(
        collection=user_calendars,
        field_name='title',
        value=title,
        exclude_id=calendar_id,
        case_sensitive=False
    )
    
    if not is_valid:
        # Customize error message for calendar context
        return False, "", f"You already have a calendar named '{title}'. Please choose a different name."
    
    return True, clean_title, ""

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


def validate_door_order(door_order: str) -> Tuple[bool, str, str]:
    """
    Validate door order is a valid option.

    Args:
        door_order: Door ordering option ("sequential" or "random")

    Returns:
        Tuple of (is_valid, clean_door_order, error_message)
    """
    if not door_order or not door_order.strip():
        return False, "", "Door order is required"

    clean_door_order = door_order.strip().lower()

    if clean_door_order not in VALID_DOOR_ORDERS:
        return False, "", f"Invalid door order. Must be one of: {', '.join(VALID_DOOR_ORDERS)}"

    return True, clean_door_order, ""


def validate_timezone(timezone: str) -> Tuple[bool, str, str]:
    """
    Validate timezone is a valid IANA timezone identifier.

    Args:
        timezone: IANA timezone identifier (e.g., "Europe/Berlin", "America/New_York")

    Returns:
        Tuple of (is_valid, clean_timezone, error_message)
    """
    if not timezone or not timezone.strip():
        return False, "", "Timezone is required"

    clean_timezone = timezone.strip()

    # Validate against IANA timezone database
    try:
        # Try to create a ZoneInfo object - this will raise ZoneInfoNotFoundError if invalid
        ZoneInfo(clean_timezone)
        return True, clean_timezone, ""
    except ZoneInfoNotFoundError:
        return False, "", f"Invalid timezone '{clean_timezone}'. Must be a valid IANA timezone identifier (e.g., 'Europe/Berlin')"
    except (KeyError, ValueError) as e:
        # Handle edge cases like malformed timezone strings
        return False, "", f"Invalid timezone format: {str(e)}"


def validate_theme(theme: str) -> Tuple[bool, str, str]:
    """
    Validate theme is a non-empty string.

    Note: For Phase 2, only "christmas" theme is used, but validation is lenient
    to support future theme additions without code changes.

    Args:
        theme: Theme identifier string

    Returns:
        Tuple of (is_valid, clean_theme, error_message)
    """
    if not theme or not theme.strip():
        return False, "", "Theme is required"

    clean_theme = theme.strip().lower()

    if len(clean_theme) < 1:
        return False, "", "Theme cannot be empty"

    if len(clean_theme) > 50:
        return False, "", "Theme name must be 50 characters or less"

    return True, clean_theme, ""


def validate_door_positions(door_positions: Optional[List[int]], duration: int) -> Tuple[bool, Optional[List[int]], str]:
    """
    Validate door positions array for random door ordering.

    Args:
        door_positions: Array of shuffled door positions (1-indexed day numbers)
        duration: Calendar duration (number of days)

    Returns:
        Tuple of (is_valid, clean_door_positions, error_message)
    """
    # None is valid for sequential ordering
    if door_positions is None:
        return True, None, ""

    # Validate type
    if not isinstance(door_positions, list):
        return False, None, "Door positions must be an array"

    # Validate length matches duration
    if len(door_positions) != duration:
        return False, None, f"Door positions array length ({len(door_positions)}) must match duration ({duration})"

    # Verify all positions are valid day numbers (1 to duration, no duplicates)
    expected_positions = set(range(1, duration + 1))
    actual_positions = set(door_positions)

    if expected_positions != actual_positions:
        return False, None, "Door positions must contain each day number from 1 to duration exactly once"

    return True, door_positions, ""


# ============================================================================
# Video Upload Validation Functions
# ============================================================================

def validate_video_file_type(filename: str) -> Tuple[bool, str]:
    """
    Validate video file extension is allowed.

    Args:
        filename: Name of the uploaded file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is required"

    allowed_extensions = {'.mp4', '.mov', '.avi', '.webm'}
    file_ext = Path(filename).suffix.lower()

    if file_ext not in allowed_extensions:
        allowed_list = ', '.join(sorted(allowed_extensions))
        return False, f"Invalid file type. Allowed types: {allowed_list}"

    return True, ""


def validate_video_file_size(file_size: int) -> Tuple[bool, str]:
    """
    Validate video file size is within limits (max 1GB).

    Args:
        file_size: Size of file in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    max_size_bytes = 1024 * 1024 * 1024  # 1GB in bytes (1024MB)

    if file_size <= 0:
        return False, "File size must be greater than 0"

    if file_size > max_size_bytes:
        size_mb = file_size / (1024 * 1024)
        return False, f"File size ({size_mb:.1f}MB) exceeds maximum allowed size of 1024MB (1GB)"

    return True, ""


def validate_video_day_number(day: int, calendar_duration: int) -> Tuple[bool, str]:
    """
    Validate video day number is within calendar's duration.

    Args:
        day: Day number for the video (1-based)
        calendar_duration: Total duration of calendar in days

    Returns:
        Tuple of (is_valid, error_message)
    """
    if day < 1:
        return False, "Day number must be at least 1"

    if day > calendar_duration:
        return False, f"Day {day} exceeds calendar duration of {calendar_duration} days"

    return True, ""


def validate_video_duration(video_path: str, max_duration_seconds: int = 180) -> Tuple[bool, Optional[float], str]:
    """
    Validate video duration using FFprobe.

    Args:
        video_path: Path to the video file to validate
        max_duration_seconds: Maximum allowed duration (default: 180 seconds)

    Returns:
        Tuple of (is_valid, duration_seconds, error_message)
    """
    if not os.path.exists(video_path):
        return False, None, "Video file not found"

    try:
        # Check if ffprobe is available
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return False, None, "Unable to read video metadata"

        try:
            duration = float(result.stdout.strip())
        except ValueError:
            return False, None, "Invalid video duration metadata"

        if duration > max_duration_seconds:
            duration_mins = duration / 60
            max_mins = max_duration_seconds / 60
            return False, duration, f"Video duration ({duration_mins:.1f} minutes) exceeds maximum of {max_mins:.0f} minutes"

        return True, duration, ""

    except FileNotFoundError:
        # FFprobe not installed - skip duration validation
        return True, None, ""

    except subprocess.TimeoutExpired:
        return False, None, "Video validation timed out"

    except Exception as e:
        return False, None, f"Error validating video: {str(e)}"