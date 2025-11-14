# Calendar Service - Business Logic for Calendar Operations (Refactored for per-calendar folders)
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple, Optional

from app.utils.json_db import calendars_db, add_calendar_to_user, remove_calendar_from_user, get_user_calendar_ids
from app.utils.validators import (
    validate_calendar_title,
    validate_calendar_duration,
    validate_calendar_start_date,
    validate_required_fields,
    validate_door_order,
    validate_timezone,
    validate_theme,
    validate_door_positions
)


def create_calendar(user_id: str, title: str, start_date: str, duration: int,
                   door_order: str = 'sequential', door_positions: list = None,
                   theme: str = 'christmas', tz: str = 'Europe/Berlin',
                   description: str = '') -> Tuple[bool, Dict[str, Any], str]:
    """
    Create a new calendar for the authenticated user

    Creates folder structure: data/calendars/<uuid>/
    Adds calendar_id to user's calendar_ids array
    """
    try:
        # Validate required fields
        data = {'title': title, 'startDate': start_date, 'duration': duration}
        fields_valid, fields_error = validate_required_fields(data, ['title', 'startDate', 'duration'])
        if not fields_valid:
            return False, {}, fields_error

        # Validate title format
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

        # Validate door order
        door_order_valid, clean_door_order, door_order_error = validate_door_order(door_order)
        if not door_order_valid:
            return False, {}, door_order_error

        # Validate timezone
        timezone_valid, clean_timezone, timezone_error = validate_timezone(tz)
        if not timezone_valid:
            return False, {}, timezone_error

        # Validate theme
        theme_valid, clean_theme, theme_error = validate_theme(theme)
        if not theme_valid:
            return False, {}, theme_error

        # Validate door_positions
        positions_valid, clean_door_positions, positions_error = validate_door_positions(door_positions, clean_duration)
        if not positions_valid:
            return False, {}, positions_error

        # Generate unique calendar ID
        calendar_id = str(uuid.uuid4())

        # Create calendar folder structure
        if not calendars_db.create_calendar_structure(calendar_id):
            return False, {}, "Failed to create calendar folder structure"

        # Calculate end date
        start_datetime = datetime.strptime(clean_start_date, '%Y-%m-%d')
        end_datetime = start_datetime + timedelta(days=clean_duration - 1)
        end_date = end_datetime.strftime('%Y-%m-%d')

        # Create calendar metadata
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        date_range = f"{clean_start_date} to {end_date}"

        # Calculate status based on dates
        today = datetime.now().date()
        start_dt = datetime.strptime(clean_start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()

        if today < start_dt:
            status = 'upcoming'
        elif today > end_dt:
            status = 'ended'
        else:
            status = 'active'

        calendar_data = {
            'id': calendar_id,
            'title': clean_title,
            'startDate': clean_start_date,
            'endDate': end_date,
            'dateRange': date_range,
            'duration': clean_duration,
            'status': status,
            'published': False,  # Unpublished by default
            'doorOrder': clean_door_order,
            'doorPositions': clean_door_positions,
            'theme': clean_theme,
            'timezone': clean_timezone,
            'description': description,
            'videos': {},
            'videoCount': 0,
            'videoStorageUsed': 0,
            'createdAt': now,
            'updatedAt': now
        }

        # Write meta.json
        if not calendars_db.write_calendar_meta(calendar_id, calendar_data):
            return False, {}, "Failed to write calendar metadata"

        # Add calendar to user's calendar_ids array
        if not add_calendar_to_user(user_id, calendar_id):
            # Rollback: delete calendar folder
            calendars_db.delete_calendar_folder(calendar_id)
            return False, {}, "Failed to associate calendar with user"

        return True, calendar_data, ""

    except Exception as e:
        print(f"Calendar creation error: {str(e)}")
        return False, {}, "Internal server error during calendar creation"


def get_user_calendars(user_id: str) -> Tuple[bool, list, str]:
    """
    Get all calendars for a specific user

    Reads user's calendar_ids array and fetches each calendar's meta.json
    """
    try:
        calendar_ids = get_user_calendar_ids(user_id)
        calendars = []

        for calendar_id in calendar_ids:
            meta = calendars_db.read_calendar_meta(calendar_id)
            if meta:
                calendars.append(meta)

        return True, calendars, ""

    except Exception as e:
        print(f"Get user calendars error: {str(e)}")
        return False, [], "Internal server error retrieving calendars"


def get_calendar_by_id(calendar_id: str, user_id: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Get a specific calendar by ID, ensuring it belongs to the user

    Returns calendar if user owns it
    """
    try:
        # Check if calendar exists
        if not calendars_db.calendar_exists(calendar_id):
            return False, {}, "Calendar not found"

        # Check ownership
        user_calendar_ids = get_user_calendar_ids(user_id)
        if calendar_id not in user_calendar_ids:
            return False, {}, "Calendar not found"  # Don't reveal existence

        # Read calendar meta.json
        calendar_data = calendars_db.read_calendar_meta(calendar_id)
        if not calendar_data:
            return False, {}, "Calendar not found"

        return True, calendar_data, ""

    except Exception as e:
        print(f"Get calendar error: {str(e)}")
        return False, {}, "Internal server error retrieving calendar"


def update_calendar(calendar_id: str, user_id: str, title: Optional[str] = None,
                   start_date: Optional[str] = None, duration: Optional[int] = None,
                   door_order: Optional[str] = None, door_positions: Optional[list] = None,
                   theme: Optional[str] = None, tz: Optional[str] = None,
                   description: Optional[str] = None) -> Tuple[bool, Dict[str, Any], str]:
    """
    Update a calendar (owner only)
    """
    try:
        # Get existing calendar
        success, calendar_data, error = get_calendar_by_id(calendar_id, user_id)
        if not success:
            return False, {}, error

        updates = {}

        # Validate and update fields if provided
        if title is not None:
            title_valid, clean_title, title_error = validate_calendar_title(title)
            if not title_valid:
                return False, {}, title_error
            updates['title'] = clean_title

        if start_date is not None:
            date_valid, clean_start_date, date_error = validate_calendar_start_date(start_date)
            if not date_valid:
                return False, {}, date_error
            updates['startDate'] = clean_start_date

        if duration is not None:
            duration_valid, clean_duration, duration_error = validate_calendar_duration(duration)
            if not duration_valid:
                return False, {}, duration_error
            updates['duration'] = clean_duration

        if door_order is not None:
            order_valid, clean_order, order_error = validate_door_order(door_order)
            if not order_valid:
                return False, {}, order_error
            updates['doorOrder'] = clean_order

        if door_positions is not None:
            current_duration = updates.get('duration', calendar_data['duration'])
            pos_valid, clean_pos, pos_error = validate_door_positions(door_positions, current_duration)
            if not pos_valid:
                return False, {}, pos_error
            updates['doorPositions'] = clean_pos

        if theme is not None:
            theme_valid, clean_theme, theme_error = validate_theme(theme)
            if not theme_valid:
                return False, {}, theme_error
            updates['theme'] = clean_theme

        if tz is not None:
            tz_valid, clean_tz, tz_error = validate_timezone(tz)
            if not tz_valid:
                return False, {}, tz_error
            updates['timezone'] = clean_tz

        if description is not None:
            updates['description'] = description

        # Recalculate endDate and dateRange if startDate or duration changed
        if 'startDate' in updates or 'duration' in updates:
            new_start_date = updates.get('startDate', calendar_data['startDate'])
            new_duration = updates.get('duration', calendar_data['duration'])

            start_dt = datetime.strptime(new_start_date, '%Y-%m-%d')
            end_dt = start_dt + timedelta(days=new_duration - 1)
            new_end_date = end_dt.strftime('%Y-%m-%d')

            updates['endDate'] = new_end_date
            updates['dateRange'] = f"{new_start_date} to {new_end_date}"

        updates['updatedAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Update meta.json
        updated_calendar = calendars_db.update_calendar_meta(calendar_id, updates)
        if not updated_calendar:
            return False, {}, "Failed to update calendar"

        return True, updated_calendar, ""

    except Exception as e:
        print(f"Update calendar error: {str(e)}")
        return False, {}, "Internal server error updating calendar"


def delete_calendar(calendar_id: str, user_id: str) -> Tuple[bool, str]:
    """
    Delete a calendar (owner only)

    Deletes entire calendar folder and removes from user's calendar_ids
    """
    try:
        # Verify ownership
        success, calendar_data, error = get_calendar_by_id(calendar_id, user_id)
        if not success:
            return False, error

        # Delete calendar folder (includes videos, thumbnails, meta.json)
        if not calendars_db.delete_calendar_folder(calendar_id):
            return False, "Failed to delete calendar folder"

        # Remove from user's calendar_ids array
        if not remove_calendar_from_user(user_id, calendar_id):
            print(f"Warning: Calendar {calendar_id} deleted but not removed from user {user_id}")

        return True, ""

    except Exception as e:
        print(f"Delete calendar error: {str(e)}")
        return False, "Internal server error deleting calendar"


def publish_calendar(calendar_id: str, user_id: str) -> Tuple[bool, str]:
    """
    Publish calendar (make it publicly accessible)
    """
    try:
        # Verify ownership
        success, calendar_data, error = get_calendar_by_id(calendar_id, user_id)
        if not success:
            return False, error

        # Update published flag
        updates = {
            'published': True,
            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        updated_calendar = calendars_db.update_calendar_meta(calendar_id, updates)
        if not updated_calendar:
            return False, "Failed to publish calendar"

        return True, ""

    except Exception as e:
        print(f"Publish calendar error: {str(e)}")
        return False, "Internal server error publishing calendar"


def unpublish_calendar(calendar_id: str, user_id: str) -> Tuple[bool, str]:
    """
    Unpublish calendar (make it private again)
    """
    try:
        # Verify ownership
        success, calendar_data, error = get_calendar_by_id(calendar_id, user_id)
        if not success:
            return False, error

        # Update published flag
        updates = {
            'published': False,
            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        updated_calendar = calendars_db.update_calendar_meta(calendar_id, updates)
        if not updated_calendar:
            return False, "Failed to unpublish calendar"

        return True, ""

    except Exception as e:
        print(f"Unpublish calendar error: {str(e)}")
        return False, "Internal server error unpublishing calendar"


def get_public_calendar(calendar_id: str, viewer_user_id: str = None) -> Tuple[bool, Dict[str, Any], str]:
    """
    Get calendar for public viewing

    Access control:
    - If published: Anyone can access
    - If not published: Only owner can access
    - Returns isOwner flag if viewer owns calendar
    """
    try:
        # Check if calendar exists
        if not calendars_db.calendar_exists(calendar_id):
            return False, {}, "Calendar not found"

        # Read calendar meta.json
        calendar_data = calendars_db.read_calendar_meta(calendar_id)
        if not calendar_data:
            return False, {}, "Calendar not found"

        # Check if viewer is owner by querying user's calendar_ids from database
        is_owner = False
        if viewer_user_id:
            user_calendar_ids = get_user_calendar_ids(viewer_user_id)
            is_owner = calendar_id in user_calendar_ids

        # Access control
        if not calendar_data.get('published', False) and not is_owner:
            return False, {}, "Calendar not found"  # Don't reveal existence

        # Add isOwner flag
        calendar_data['isOwner'] = is_owner

        # Build days array with unlock statuses and thumbnail URLs
        from app.utils.unlock_logic import is_day_unlocked

        duration = calendar_data.get('duration', 0)
        videos = calendar_data.get('videos', {})
        days = []

        for day_number in range(1, duration + 1):
            day_unlocked = is_day_unlocked(calendar_data, day_number)

            # Check if video exists for this day
            video_info = videos.get(str(day_number))
            thumbnail_url = None
            has_video = False

            if video_info and video_info.get('status') == 'completed':
                # Construct thumbnail URL for this day
                thumbnail_url = f"/api/calendars/{calendar_id}/videos/{day_number}/thumbnail"
                has_video = True

            day_data = {
                'dayNumber': day_number,
                'isUnlocked': day_unlocked,
                'hasVideo': has_video,
                'thumbnailUrl': thumbnail_url
            }
            days.append(day_data)

        calendar_data['days'] = days

        return True, calendar_data, ""

    except Exception as e:
        print(f"Get public calendar error: {str(e)}")
        return False, {}, "Internal server error retrieving calendar"
