# Calendar Service - Business Logic for Calendar Operations
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple, Optional

from app.utils.json_db import calendars_db
from app.utils.validators import (
    validate_calendar_title,
    validate_calendar_title_uniqueness,
    validate_calendar_duration, 
    validate_calendar_start_date,
    validate_required_fields
)

def _validate_title_with_uniqueness(user_id: str, title: str, calendar_id: str = None) -> Tuple[bool, str, str]:
    """
    Helper function to validate calendar title format and uniqueness
    
    Args:
        user_id: The user ID to check uniqueness within
        title: The title to validate
        calendar_id: Optional calendar ID for updates (allows same title for same calendar)
    
    Returns:
        Tuple of (is_valid, clean_title, error_message)
    """
    # Validate title format first
    title_valid, title_result = validate_calendar_title(title)
    if not title_valid:
        return False, "", title_result
    
    clean_title = title_result
    
    # Check title uniqueness for this user
    user_calendars_success, user_calendars_list, user_calendars_error = get_user_calendars(user_id)
    if not user_calendars_success:
        return False, "", f"Unable to verify title uniqueness: {user_calendars_error}"
    
    uniqueness_valid, clean_title_final, uniqueness_error = validate_calendar_title_uniqueness(
        user_calendars_list, clean_title, calendar_id
    )
    if not uniqueness_valid:
        return False, "", uniqueness_error
    
    return True, clean_title_final, ""

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
        
        # Validate title format and uniqueness
        title_valid, clean_title, title_error = _validate_title_with_uniqueness(user_id, title)
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
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
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
    
    NFR Compliance:
        - [P3] Calendar Rendering: Optimized for <3 second response time
        - [SC1] User Database Capacity: Handles 100+ users with O(n) complexity
        - [P4] Concurrent Users: Thread-safe JSON file operations
    
    Performance Characteristics:
        - Time Complexity: O(n) where n = total calendars in system
        - Space Complexity: O(m) where m = calendars for this user
        - Acceptable for small-medium scale (100 users, 1000 total calendars)
        - May need optimization for larger datasets (>5000 calendars)
    
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

def update_calendar(calendar_id: str, user_id: str, title: Optional[str] = None, 
                   start_date: Optional[str] = None, duration: Optional[int] = None) -> Tuple[bool, Dict[str, Any], str]:
    """
    Update a specific calendar for the authenticated user
    
    NFR Compliance:
        - [S4] Input Validation: All inputs validated using existing validation functions
        - [SC3] Modular Architecture: Service layer separation of concerns
        - [P3] Calendar Rendering: Optimized updates for <3 second response time
    
    Args:
        calendar_id: str - The calendar ID to update
        user_id: str - The authenticated user ID
        title: Optional[str] - New calendar title
        start_date: Optional[str] - New start date in YYYY-MM-DD format
        duration: Optional[int] - New duration in days (1-31)
    
    Returns:
        - success: bool
        - calendar_data: Dict with updated calendar info or empty dict
        - error_message: str with error details or empty string
    """
    try:
        # First, get the calendar and verify ownership
        calendar_exists, existing_calendar, error_msg = get_calendar_by_id(calendar_id, user_id)
        if not calendar_exists:
            return False, {}, error_msg
        
        # Prepare update data - only include provided fields
        update_data = {}
        
        # Validate and process title if provided
        if title is not None:
            title_valid, clean_title, title_error = _validate_title_with_uniqueness(user_id, title, calendar_id)
            if not title_valid:
                return False, {}, title_error
            update_data['title'] = clean_title
        
        # Validate and process start date if provided
        if start_date is not None:
            date_valid, clean_start_date, date_error = validate_calendar_start_date(start_date)
            if not date_valid:
                return False, {}, date_error
            update_data['startDate'] = clean_start_date
        
        # Validate and process duration if provided
        if duration is not None:
            duration_valid, clean_duration, duration_error = validate_calendar_duration(duration)
            if not duration_valid:
                return False, {}, duration_error
            update_data['duration'] = clean_duration
        
        # If no updates provided, return error
        if not update_data:
            return False, {}, "No valid update fields provided"
        
        # Calculate derived fields if start_date or duration changed
        final_start_date = update_data.get('startDate', existing_calendar['startDate'])
        final_duration = update_data.get('duration', existing_calendar['duration'])
        
        # Recalculate end date and date range if start date or duration changed
        if 'startDate' in update_data or 'duration' in update_data:
            start_datetime = datetime.strptime(final_start_date, '%Y-%m-%d')
            end_datetime = start_datetime + timedelta(days=final_duration - 1)
            update_data['endDate'] = end_datetime.strftime('%Y-%m-%d')
            update_data['dateRange'] = f"{final_start_date} to {update_data['endDate']}"
        
        # Update timestamp
        update_data['updatedAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Update calendar in database (NFR [SC3]: Modular architecture)
        updated_calendar = calendars_db.update('calendars', calendar_id, update_data)
        
        if updated_calendar:
            return True, updated_calendar, ""
        else:
            return False, {}, "Failed to update calendar in database"
            
    except Exception as e:
        print(f"Calendar update error: {str(e)}")
        return False, {}, "Internal server error during calendar update"

def delete_calendar(calendar_id: str, user_id: str) -> Tuple[bool, str]:
    """
    Delete a specific calendar for the authenticated user
    
    Args:
        calendar_id: str - The calendar ID to delete
        user_id: str - The authenticated user ID
    
    Returns:
        - success: bool
        - error_message: str with error details or empty string
    """
    try:
        # First, get the calendar and verify ownership
        calendar_exists, existing_calendar, error_msg = get_calendar_by_id(calendar_id, user_id)
        if not calendar_exists:
            return False, error_msg
        
        # Delete calendar from database
        deleted = calendars_db.delete('calendars', calendar_id)
        
        if deleted:
            return True, ""
        else:
            return False, "Failed to delete calendar from database"
            
    except Exception as e:
        print(f"Calendar deletion error: {str(e)}")
        return False, "Internal server error during calendar deletion"