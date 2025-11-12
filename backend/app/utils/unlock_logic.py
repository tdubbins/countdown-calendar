# Unlock Logic Utilities for Shared Calendars
"""
This module handles the day unlock logic for shared calendars.

NFR Compliance:
    - [P3] Calendar Rendering: Optimized calculations for <3 second response time
    - [SC3] Modular Architecture: Separated unlock logic for reusability
    - [U5] Accessibility: Clear, testable unlock logic

Business Rules:
    - Days unlock at midnight in the calendar's timezone (Berlin for Phase 2)
    - Day 1 unlocks on start_date at 00:00
    - Day 2 unlocks on start_date + 1 day at 00:00
    - Past days remain accessible (can rewatch)
    - Future days are locked (not accessible yet)
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, Any


def is_day_unlocked(calendar: Dict[str, Any], day_number: int) -> bool:
    """
    Determine if a specific day is unlocked based on current time.

    This function implements the core unlock logic for shared calendar doors.
    It compares the current date in the calendar's timezone against the
    calculated unlock date for the requested day.

    NFR Compliance:
        - [P3] Performance: O(1) time complexity, <10ms execution
        - [S4] Input Validation: Handles edge cases gracefully
        - [SC3] Modular: Pure function, easy to test

    Args:
        calendar: Calendar dict containing:
            - startDate: str in YYYY-MM-DD format
            - timezone: str IANA timezone (e.g., "Europe/Berlin")
            - duration: int number of days in calendar
        day_number: int The day number to check (1-indexed, must be 1 to duration)

    Returns:
        bool: True if day is unlocked (current date >= unlock date), False otherwise

    Examples:
        >>> calendar = {
        ...     'startDate': '2025-12-01',
        ...     'timezone': 'Europe/Berlin',
        ...     'duration': 24
        ... }
        >>> # On December 1st, 2025 at 00:00 Berlin time
        >>> is_day_unlocked(calendar, 1)  # True - Day 1 is unlocked
        >>> is_day_unlocked(calendar, 2)  # False - Day 2 unlocks tomorrow
        >>> # On December 3rd, 2025 at 10:00 Berlin time
        >>> is_day_unlocked(calendar, 1)  # True - Past day
        >>> is_day_unlocked(calendar, 2)  # True - Past day
        >>> is_day_unlocked(calendar, 3)  # True - Today (unlocked at midnight)
        >>> is_day_unlocked(calendar, 4)  # False - Future day
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

    This is a convenience function for generating unlock status for all doors
    at once, useful for the public calendar viewer API.

    NFR Compliance:
        - [P3] Performance: O(n) where n = duration, typically <31 iterations
        - [SC3] Modular: Reuses is_day_unlocked for consistency

    Args:
        calendar: Calendar dict with startDate, timezone, and duration

    Returns:
        Dict mapping day_number (int) to unlock status (bool)

    Example:
        >>> calendar = {'startDate': '2025-12-01', 'timezone': 'Europe/Berlin', 'duration': 24}
        >>> statuses = get_all_unlock_statuses(calendar)
        >>> # Returns: {1: True, 2: True, 3: True, 4: False, ..., 24: False}
        >>> # (assuming current date is Dec 3, 2025)
    """
    duration = calendar.get('duration', 0)

    if duration <= 0:
        return {}

    unlock_statuses = {}

    # Calculate unlock status for each day
    for day_number in range(1, duration + 1):
        unlock_statuses[day_number] = is_day_unlocked(calendar, day_number)

    return unlock_statuses
