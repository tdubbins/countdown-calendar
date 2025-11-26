# Unlock Logic Utilities for Shared Calendars
"""
This module handles the day unlock logic for shared calendars.

Business Rules:
    - Days unlock at midnight in the calendar's timezone
    - Day 1 unlocks on start_date at 00:00
    - Day N unlocks on start_date + (N-1) days at 00:00
    - Past days remain accessible (can rewatch)
    - Future days are locked
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, Any


def is_day_unlocked(calendar: Dict[str, Any], day_number: int) -> bool:
    """
    Determine if a specific day is unlocked based on current time.

    Args:
        calendar: Calendar dict with startDate, timezone, and duration
        day_number: The day number to check (1-indexed)

    Returns:
        bool: True if day is unlocked, False otherwise
    """
    try:
        # Get timezone from calendar (default to Europe/Berlin for Phase 2)
        timezone_str = calendar.get('timezone', 'Europe/Berlin')
        tz = ZoneInfo(timezone_str)

        # Parse start date (format: YYYY-MM-DD)
        start_date_str = calendar.get('startDate')
        if not start_date_str:
            # Invalid calendar data - cannot determine unlock status
            return False

        # Convert start date string to date object
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        # Get current date and time in calendar's timezone
        current_datetime = datetime.now(tz)
        current_date = current_datetime.date()

        # Calculate unlock date for this specific day
        # Day 1 unlocks on start_date (offset = 0)
        # Day 2 unlocks on start_date + 1 day (offset = 1)
        # Day N unlocks on start_date + (N-1) days
        days_offset = day_number - 1
        unlock_date = start_date + timedelta(days=days_offset)

        # Day is unlocked if current date >= unlock date
        # This means:
        # - All past days remain accessible
        # - Today's day is accessible (unlocked at midnight)
        # - Future days are not accessible yet
        is_unlocked = current_date >= unlock_date

        return is_unlocked

    except (ValueError, KeyError, TypeError) as e:
        # Handle parsing errors, missing fields, or invalid data gracefully
        # In case of error, default to locked (safe default)
        print(f"Unlock logic error for day {day_number}: {str(e)}")
        return False


def get_all_unlock_statuses(calendar: Dict[str, Any]) -> Dict[int, bool]:
    """
    Get unlock status for all days in a calendar.

    Args:
        calendar: Calendar dict with startDate, timezone, and duration

    Returns:
        Dict mapping day_number to unlock status
    """
    duration = calendar.get('duration', 0)

    if duration <= 0:
        return {}

    unlock_statuses = {}

    # Calculate unlock status for each day
    for day_number in range(1, duration + 1):
        unlock_statuses[day_number] = is_day_unlocked(calendar, day_number)

    return unlock_statuses
