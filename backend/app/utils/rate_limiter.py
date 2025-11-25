# Rate Limiting Utility
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

def check_rate_limit(
    user: Dict[str, Any],
    action: str,
    limit: int,
    window_hours: int
) -> Tuple[bool, int, str]:
    """
    Generic rate limiting checker for user actions

    NFR Compliance:
        - [S2] Rate limiting for security
        - [SC3] Modular architecture - DRY principle

    Args:
        user: User dictionary with rate limiting fields
        action: Action identifier (e.g., 'verification_email', 'password_reset')
        limit: Maximum number of requests allowed within window
        window_hours: Time window in hours

    Returns:
        Tuple of (is_allowed, current_count, error_message)
        - is_allowed: True if request is within rate limit
        - current_count: Updated count after this check
        - error_message: Empty string if allowed, error message if rate limited

    Example:
        >>> is_allowed, count, error = check_rate_limit(
        ...     user=user_dict,
        ...     action='verification_email',
        ...     limit=3,
        ...     window_hours=1
        ... )
        >>> if not is_allowed:
        ...     return False, error

    Usage in User Dictionary:
        User dict should have these fields for each action:
        - f'{action}_last_sent': ISO timestamp of last request
        - f'{action}_count': Count of requests in current window

    Design Pattern:
        This function only CHECKS the rate limit.
        The calling code is responsible for:
        1. Updating the user's rate limit fields after successful action
        2. Persisting the updated user data

        This separation of concerns makes the function more testable
        and flexible (can be used with any storage backend).
    """
    current_time = datetime.now()

    # Build field names for this action
    last_sent_key = f'{action}_last_sent'
    count_key = f'{action}_count'

    # Get current rate limit data
    last_sent = user.get(last_sent_key)
    count = user.get(count_key, 0)

    # If no previous request, allow immediately
    if not last_sent:
        return True, 1, ""

    # Parse last sent timestamp
    try:
        last_sent_time = datetime.fromisoformat(last_sent)
    except (ValueError, TypeError):
        # Invalid timestamp, reset counter
        return True, 1, ""

    # Calculate time since last request
    time_diff = current_time - last_sent_time
    window = timedelta(hours=window_hours)

    # If time window has passed, reset counter
    if time_diff > window:
        return True, 1, ""

    # Still within time window, check count
    if count >= limit:
        # Calculate remaining time
        time_remaining = window - time_diff
        hours_remaining = int(time_remaining.total_seconds() // 3600)
        minutes_remaining = int((time_remaining.total_seconds() % 3600) // 60)

        if hours_remaining > 0:
            time_str = f"{hours_remaining} hour{'s' if hours_remaining > 1 else ''}"
        else:
            time_str = f"{minutes_remaining} minute{'s' if minutes_remaining > 1 else ''}"

        error_msg = f"Too many requests. Please try again in {time_str}."
        return False, count, error_msg

    # Within limit, increment count
    return True, count + 1, ""


def get_rate_limit_update_data(action: str, new_count: int) -> Dict[str, Any]:
    """
    Helper to generate update dictionary for rate limit tracking

    Args:
        action: Action identifier
        new_count: New count value to store

    Returns:
        Dictionary with rate limit fields to update in user record

    Example:
        >>> update_data = get_rate_limit_update_data('verification_email', 2)
        >>> users_db.update('users', user_id, update_data)
    """
    return {
        f'{action}_last_sent': datetime.now().isoformat(),
        f'{action}_count': new_count
    }
