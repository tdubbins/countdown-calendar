# Calendar Service - Business Logic for Calendar Operations
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional

from app.utils.json_db import calendars_db
from app.utils.validators import (
    validate_calendar_title,
    validate_calendar_duration, 
    validate_calendar_start_date,
    validate_required_fields
)

def create_calendar(user_id: str, title: str, start_date: str, duration: int) -> Tuple[bool, Dict[str, Any], str]:
    """
    Create a new calendar for the authenticated user
    
    Returns:
        - success: bool
        - calendar_data: Dict with calendar info or empty dict
        - error_message: str with error details or empty string
    """
    try:
        # Validate required fields are present
        data = {'title': title, 'startDate': start_date, 'duration': duration}
        fields_valid, fields_error = validate_required_fields(data, ['title', 'startDate', 'duration'])
        if not fields_valid:
            return False, {}, fields_error
        
        # Validate title
        title_valid, clean_title, title_error = validate_calendar_title(title)
        if not title_valid:
            return False, {}, title_error
        
        # Validate start date
        date_valid, clean_start_date, date_error = validate_calendar_start_date(start_date)
        if not date_valid:
            return False, {}, date_error
        
        # Validate duration
        duration_valid, clean_duration, duration_error = validate_calendar_duration(duration)
        if not duration_valid:
            return False, {}, duration_error
        
        # Generate unique calendar ID and share token (NFR [S3]: Cryptographically secure)
        calendar_id = str(uuid.uuid4())
        share_token = str(uuid.uuid4())
        
        # Calculate end date and date range
        start_datetime = datetime.strptime(clean_start_date, '%Y-%m-%d')
        end_datetime = start_datetime + timedelta(days=clean_duration - 1)
        end_date = end_datetime.strftime('%Y-%m-%d')
        date_range = f"{clean_start_date} to {end_date}"
        
        # Create calendar object according to schema
        now = datetime.utcnow().isoformat() + 'Z'
        calendar_data = {
            'id': calendar_id,
            'title': clean_title,
            'startDate': clean_start_date,
            'duration': clean_duration,
            'endDate': end_date,
            'dateRange': date_range,
            'videoCount': 0,
            'status': 'draft',
            'shareToken': share_token,
            'createdAt': now,
            'updatedAt': now,
            'userId': user_id,
            'videoStorageUsed': 0,
            'videos': {}
        }
        
        # Save to database (NFR [SC3]: Modular architecture)
        saved_calendar = calendars_db.create('calendars', calendar_id, calendar_data)
        
        if saved_calendar:
            return True, saved_calendar, ""
        else:
            return False, {}, "Failed to save calendar to database"
            
    except Exception as e:
        print(f"Calendar creation error: {str(e)}")
        return False, {}, "Internal server error during calendar creation"

def get_user_calendars(user_id: str) -> Tuple[bool, list, str]:
    """
    Get all calendars for a specific user
    
    Returns:
        - success: bool
        - calendars: list of calendar objects
        - error_message: str with error details or empty string
    """
    try:
        # Use database method to find calendars by user ID (NFR [SC1]: Efficient queries)
        user_calendars = calendars_db.list_by_field('calendars', 'userId', user_id)
        return True, user_calendars, ""
        
    except Exception as e:
        print(f"Get user calendars error: {str(e)}")
        return False, [], "Internal server error retrieving calendars"

def get_calendar_by_id(calendar_id: str, user_id: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Get a specific calendar by ID, ensuring it belongs to the user
    
    Returns:
        - success: bool
        - calendar_data: Dict with calendar info or empty dict
        - error_message: str with error details or empty string
    """
    try:
        # Find calendar by ID
        calendar = calendars_db.find_by_id('calendars', calendar_id)
        
        if not calendar:
            return False, {}, "Calendar not found"
        
        # Verify ownership
        if calendar.get('userId') != user_id:
            return False, {}, "Calendar not found"  # Don't reveal existence
        
        return True, calendar, ""
        
    except Exception as e:
        print(f"Get calendar by ID error: {str(e)}")
        return False, {}, "Internal server error retrieving calendar"