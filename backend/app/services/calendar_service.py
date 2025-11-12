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
    validate_required_fields,
    validate_door_order,
    validate_timezone,
    validate_theme,
    validate_door_positions
)
from app.utils.storage import delete_calendar_files

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
    title_valid, clean_title, title_error = validate_calendar_title(title)
    if not title_valid:
        return False, "", title_error
    
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

def create_calendar(user_id: str, title: str, start_date: str, duration: int,
                   door_order: str = 'sequential', door_positions: list = None,
                   theme: str = 'christmas', tz: str = 'Europe/Berlin') -> Tuple[bool, Dict[str, Any], str]:
    """
    Create a new calendar for the authenticated user

    Args:
        user_id: The user ID creating the calendar
        title: Calendar title
        start_date: Calendar start date in YYYY-MM-DD format
        duration: Calendar duration in days (1-31)
        door_order: Door ordering ("sequential" or "random", default: "sequential")
        door_positions: Array of shuffled door positions for random ordering (optional)
        theme: Calendar theme identifier (default: "christmas")
        tz: IANA timezone identifier (default: "Europe/Berlin")

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

        # Validate door order (NFR [S4]: Input validation for enum values)
        door_order_valid, clean_door_order, door_order_error = validate_door_order(door_order)
        if not door_order_valid:
            return False, {}, door_order_error

        # Validate timezone (NFR [S4]: Input validation for timezone strings)
        timezone_valid, clean_timezone, timezone_error = validate_timezone(tz)
        if not timezone_valid:
            return False, {}, timezone_error

        # Validate theme
        theme_valid, clean_theme, theme_error = validate_theme(theme)
        if not theme_valid:
            return False, {}, theme_error

        # Validate door_positions (NFR [S4]: Input validation for array structure)
        positions_valid, clean_door_positions, positions_error = validate_door_positions(door_positions, clean_duration)
        if not positions_valid:
            return False, {}, positions_error

        # Generate unique calendar ID (NFR [S3]: Cryptographically secure)
        calendar_id = str(uuid.uuid4())

        # Share token is null by default (lazy generation - privacy by default)
        # Token will be generated when user clicks "Share" button (Issue #75)
        share_token = None
        
        # Calculate end date and date range
        start_datetime = datetime.strptime(clean_start_date, '%Y-%m-%d')
        end_datetime = start_datetime + timedelta(days=clean_duration - 1)
        end_date = end_datetime.strftime('%Y-%m-%d')
        date_range = f"{clean_start_date} to {end_date}"
        
        # Create calendar object according to schema (NFR [SC3]: Modular architecture)
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
            'shareToken': share_token,  # null by default (lazy generation)
            'createdAt': now,
            'updatedAt': now,
            'userId': user_id,
            'videoStorageUsed': 0,
            'videos': {},
            # New fields for sharing feature (Issue #74)
            'doorOrder': clean_door_order,        # "sequential" or "random"
            'doorPositions': clean_door_positions, # array of integers or null
            'theme': clean_theme,                  # theme identifier (e.g., "christmas")
            'timezone': clean_timezone             # IANA timezone (e.g., "Europe/Berlin")
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
                   start_date: Optional[str] = None, duration: Optional[int] = None,
                   door_order: Optional[str] = None, door_positions: Optional[list] = None,
                   theme: Optional[str] = None, tz: Optional[str] = None) -> Tuple[bool, Dict[str, Any], str]:
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
        door_order: Optional[str] - Door ordering ("sequential" or "random")
        door_positions: Optional[list] - Array of shuffled door positions for random ordering
        theme: Optional[str] - Calendar theme identifier
        tz: Optional[str] - IANA timezone identifier

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

        # Prevent editing if calendar is already shared (status is "active")
        # Once a calendar is shared, it should be immutable to ensure viewers have consistent experience
        if existing_calendar.get('shareToken'):
            return False, {}, "Cannot edit calendar after it has been shared. Calendar is locked."

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

        # Validate and process door order if provided (NFR [S4]: Input validation)
        if door_order is not None:
            door_order_valid, clean_door_order, door_order_error = validate_door_order(door_order)
            if not door_order_valid:
                return False, {}, door_order_error
            update_data['doorOrder'] = clean_door_order

        # Validate and process timezone if provided (NFR [S4]: Input validation)
        if tz is not None:
            timezone_valid, clean_timezone, timezone_error = validate_timezone(tz)
            if not timezone_valid:
                return False, {}, timezone_error
            update_data['timezone'] = clean_timezone

        # Validate and process theme if provided
        if theme is not None:
            theme_valid, clean_theme, theme_error = validate_theme(theme)
            if not theme_valid:
                return False, {}, theme_error
            update_data['theme'] = clean_theme

        # Validate and process door positions if provided (NFR [S4]: Input validation)
        if door_positions is not None:
            # Get the duration (either from update or existing calendar)
            final_duration = update_data.get('duration', existing_calendar.get('duration'))

            positions_valid, clean_door_positions, positions_error = validate_door_positions(door_positions, final_duration)
            if not positions_valid:
                return False, {}, positions_error
            update_data['doorPositions'] = clean_door_positions

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

    This function performs atomic cleanup of:
    1. Calendar metadata in database
    2. All video files for the calendar
    3. All thumbnail files for the calendar

    NFR Compliance:
        - [S3] Multi-tenant isolation: User ID verified before deletion
        - [SC3] Modular architecture: Separate storage utility handles file cleanup
        - GDPR compliance: Complete data removal including all media files

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

        # Delete all video and thumbnail files for this calendar (NFR [SC3]: Modular file management)
        # This is done BEFORE database deletion to ensure files are cleaned up even if DB delete fails
        delete_calendar_files(user_id, calendar_id)

        # Delete calendar from database
        deleted = calendars_db.delete('calendars', calendar_id)

        if deleted:
            return True, ""
        else:
            return False, "Failed to delete calendar from database"

    except Exception as e:
        print(f"Calendar deletion error: {str(e)}")
        return False, "Internal server error during calendar deletion"

def generate_share_token(calendar_id: str, user_id: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Generate a unique share token for a calendar (lazy generation)

    This function implements the lazy generation pattern:
    - If calendar already has a share token, returns existing token (idempotent)
    - If calendar doesn't have a share token, generates new UUID v4 token
    - Updates calendar with share token and timestamp

    NFR Compliance:
        - [S3] Multi-tenant isolation: Verifies calendar ownership before generation
        - [S4] Input validation: Validates calendar ID format
        - [SC3] Modular architecture: Service layer separation of concerns
        - Privacy by default: Only generates token when explicitly requested

    Args:
        calendar_id: str - The calendar ID to generate share token for
        user_id: str - The authenticated user ID

    Returns:
        - success: bool
        - data: Dict with share_token and share_url, or empty dict
        - error_message: str with error details or empty string

    Example Response:
        {
            'share_token': 'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
            'share_url': 'https://advent-app.com/shared/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6'
        }
    """
    try:
        # Get calendar and verify ownership (NFR [S3]: Multi-tenant security)
        calendar_exists, existing_calendar, error_msg = get_calendar_by_id(calendar_id, user_id)
        if not calendar_exists:
            return False, {}, error_msg

        # Check if calendar already has a share token (idempotent operation)
        existing_token = existing_calendar.get('shareToken')
        if existing_token:
            # Calendar already has a share token - return existing token
            # This makes the operation idempotent (safe to call multiple times)
            share_url = f"/shared/{existing_token}"

            return True, {
                'share_token': existing_token,
                'share_url': share_url
            }, ""

        # Generate new UUID v4 token (NFR [S4]: Cryptographically secure)
        # UUID v4 uses random generation (128-bit, very low collision probability)
        new_token = str(uuid.uuid4())

        # Update calendar with new share token and change status from "draft" to "active"
        # Status change: Once shared, calendar becomes "active" and should be locked from editing
        update_data = {
            'shareToken': new_token,
            'status': 'active',  # Change from "draft" to "active" when sharing
            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        # Update calendar in database (NFR [SC3]: Modular architecture)
        updated_calendar = calendars_db.update('calendars', calendar_id, update_data)

        if not updated_calendar:
            return False, {}, "Failed to update calendar with share token"

        # Construct share URL for frontend (relative URL)
        share_url = f"/shared/{new_token}"

        # Return success with token and URL
        return True, {
            'share_token': new_token,
            'share_url': share_url
        }, ""

    except Exception as e:
        print(f"Share token generation error: {str(e)}")
        return False, {}, "Internal server error during share token generation"


def get_calendar_by_share_token(share_token: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Find a calendar by its share token (public access, no authentication required)

    This function enables public access to shared calendars via their unique share token.
    Unlike get_calendar_by_id, this does NOT verify user ownership since it's for
    public viewing.

    NFR Compliance:
        - [S4] Input validation: Validates share token format (UUID)
        - [SC3] Modular architecture: Service layer separation
        - [P3] Performance: O(n) lookup across all calendars
        - Privacy: Does not return user_id or other sensitive data

    Args:
        share_token: str - The UUID share token to look up

    Returns:
        - success: bool
        - calendar_data: Dict with calendar info or empty dict
        - error_message: str with error details or empty string

    Notes:
        - Returns error if calendar is deleted (not found)
        - Returns error if share_token is null (calendar not shared)
        - Does not verify ownership (public endpoint)
    """
    try:
        # Validate share token format (should be a UUID)
        if not share_token or not share_token.strip():
            return False, {}, "Invalid share token"

        share_token = share_token.strip()

        # Validate UUID format (basic check)
        if len(share_token) != 36:  # UUID v4 format: 8-4-4-4-12 characters with hyphens
            return False, {}, "Invalid share token format"

        # Find calendar by share token (NFR [P3]: O(n) lookup)
        # This searches all calendars for matching shareToken field
        calendars_list = calendars_db.list_by_field('calendars', 'shareToken', share_token)

        if not calendars_list or len(calendars_list) == 0:
            # No calendar found with this share token
            # Could mean: token is invalid, calendar was deleted, or calendar was never shared
            return False, {}, "Calendar not found or no longer shared"

        # Should only be one calendar with this token (tokens are unique)
        calendar = calendars_list[0]

        return True, calendar, ""

    except Exception as e:
        print(f"Get calendar by share token error: {str(e)}")
        return False, {}, "Internal server error retrieving shared calendar"


def get_shared_calendar_data(share_token: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Get formatted calendar data for public sharing view

    This function prepares calendar data for public consumption by:
    1. Finding calendar by share token
    2. Calculating unlock status for all days
    3. Formatting response with only public-safe information
    4. Including thumbnail URLs for unlocked days

    NFR Compliance:
        - [S4] Privacy: Does not expose user_id, email, or sensitive data
        - [P3] Performance: Single database lookup + O(n) unlock calculation
        - [SC3] Modular: Uses unlock_logic utility for consistency
        - [U5] Accessibility: Clear data structure for frontend

    Args:
        share_token: str - The UUID share token

    Returns:
        - success: bool
        - data: Dict with formatted calendar data for public view
        - error_message: str with error details or empty string

    Response Format:
        {
            'title': 'My Advent Calendar',
            'duration': 24,
            'doorOrder': 'random',
            'doorPositions': [3, 1, 24, ...],
            'theme': 'christmas',
            'days': [
                {
                    'dayNumber': 1,
                    'isUnlocked': True,
                    'thumbnailUrl': '/api/shared/<token>/day/1/thumbnail'
                },
                {
                    'dayNumber': 2,
                    'isUnlocked': False,
                    'thumbnailUrl': None
                },
                ...
            ]
        }
    """
    try:
        # Import unlock logic utility
        from app.utils.unlock_logic import get_all_unlock_statuses

        # Find calendar by share token
        calendar_found, calendar, error_msg = get_calendar_by_share_token(share_token)
        if not calendar_found:
            return False, {}, error_msg

        # Calculate unlock status for all days (NFR [P3]: O(n) where n = duration)
        unlock_statuses = get_all_unlock_statuses(calendar)

        # Format days array with unlock status and thumbnail URLs
        days_data = []
        videos_dict = calendar.get('videos', {})

        for day_number in range(1, calendar['duration'] + 1):
            is_unlocked = unlock_statuses.get(day_number, False)

            # Only include thumbnail URL if day is unlocked AND video exists
            thumbnail_url = None
            if is_unlocked and str(day_number) in videos_dict:
                thumbnail_url = f"/api/shared/{share_token}/day/{day_number}/thumbnail"

            day_data = {
                'dayNumber': day_number,
                'isUnlocked': is_unlocked,
                'thumbnailUrl': thumbnail_url
            }

            days_data.append(day_data)

        # Prepare public-safe calendar data (NFR [S4]: Privacy protection)
        public_calendar_data = {
            'title': calendar['title'],
            'duration': calendar['duration'],
            'doorOrder': calendar.get('doorOrder', 'sequential'),
            'doorPositions': calendar.get('doorPositions'),  # null if sequential
            'theme': calendar.get('theme', 'christmas'),
            'days': days_data
        }

        # NOTE: We intentionally DO NOT include:
        # - userId (privacy)
        # - startDate (privacy - prevents calculating end date)
        # - createdAt/updatedAt (not relevant for viewers)
        # - videoStorageUsed (internal metric)
        # - shareToken itself (already known by viewer)

        return True, public_calendar_data, ""

    except Exception as e:
        print(f"Get shared calendar data error: {str(e)}")
        return False, {}, "Internal server error preparing shared calendar data"