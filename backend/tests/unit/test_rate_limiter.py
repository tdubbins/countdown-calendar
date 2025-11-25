# Unit Tests for Rate Limiter Utility
import pytest
from datetime import datetime, timedelta
from app.utils.rate_limiter import check_rate_limit, get_rate_limit_update_data


class TestCheckRateLimit:
    """Test suite for check_rate_limit function"""

    def test_first_request_allowed(self):
        """First request should always be allowed"""
        user = {}  # Empty user, no previous requests

        is_allowed, count, error = check_rate_limit(
            user=user,
            action='test_action',
            limit=3,
            window_hours=1
        )

        assert is_allowed is True
        assert count == 1
        assert error == ""

    def test_within_limit_allowed(self):
        """Request within limit should be allowed"""
        current_time = datetime.now()
        user = {
            'test_action_last_sent': current_time.isoformat(),
            'test_action_count': 2
        }

        is_allowed, count, error = check_rate_limit(
            user=user,
            action='test_action',
            limit=3,
            window_hours=1
        )

        assert is_allowed is True
        assert count == 3  # Incremented from 2 to 3
        assert error == ""

    def test_at_limit_blocked(self):
        """Request at limit should be blocked"""
        current_time = datetime.now()
        user = {
            'test_action_last_sent': current_time.isoformat(),
            'test_action_count': 3
        }

        is_allowed, count, error = check_rate_limit(
            user=user,
            action='test_action',
            limit=3,
            window_hours=1
        )

        assert is_allowed is False
        assert count == 3  # Count stays the same
        assert "Too many requests" in error
        assert "try again" in error.lower()

    def test_window_expired_resets_count(self):
        """After window expires, count should reset"""
        past_time = datetime.now() - timedelta(hours=2)  # 2 hours ago
        user = {
            'test_action_last_sent': past_time.isoformat(),
            'test_action_count': 3  # Was at limit
        }

        is_allowed, count, error = check_rate_limit(
            user=user,
            action='test_action',
            limit=3,
            window_hours=1  # 1 hour window
        )

        assert is_allowed is True
        assert count == 1  # Reset to 1
        assert error == ""

    def test_multiple_actions_independent(self):
        """Different actions should have independent rate limits"""
        current_time = datetime.now()
        user = {
            'action1_last_sent': current_time.isoformat(),
            'action1_count': 3,  # Action1 at limit
            'action2_last_sent': current_time.isoformat(),
            'action2_count': 1   # Action2 not at limit
        }

        # Action1 should be blocked
        is_allowed1, count1, error1 = check_rate_limit(
            user=user,
            action='action1',
            limit=3,
            window_hours=1
        )
        assert is_allowed1 is False

        # Action2 should be allowed
        is_allowed2, count2, error2 = check_rate_limit(
            user=user,
            action='action2',
            limit=3,
            window_hours=1
        )
        assert is_allowed2 is True
        assert count2 == 2

    def test_invalid_timestamp_resets(self):
        """Invalid timestamp should allow request and reset"""
        user = {
            'test_action_last_sent': 'invalid-timestamp',
            'test_action_count': 5
        }

        is_allowed, count, error = check_rate_limit(
            user=user,
            action='test_action',
            limit=3,
            window_hours=1
        )

        assert is_allowed is True
        assert count == 1  # Reset
        assert error == ""

    def test_error_message_includes_time_remaining_hours(self):
        """Error message should include hours when > 1 hour remaining"""
        recent_time = datetime.now() - timedelta(minutes=10)  # 10 minutes ago
        user = {
            'test_action_last_sent': recent_time.isoformat(),
            'test_action_count': 5
        }

        is_allowed, count, error = check_rate_limit(
            user=user,
            action='test_action',
            limit=5,
            window_hours=2  # 2 hour window, so > 1 hour remaining
        )

        assert is_allowed is False
        assert "hour" in error.lower()

    def test_error_message_includes_time_remaining_minutes(self):
        """Error message should include minutes when < 1 hour remaining"""
        recent_time = datetime.now() - timedelta(minutes=30)  # 30 minutes ago
        user = {
            'test_action_last_sent': recent_time.isoformat(),
            'test_action_count': 3
        }

        is_allowed, count, error = check_rate_limit(
            user=user,
            action='test_action',
            limit=3,
            window_hours=1  # 1 hour window, so < 1 hour remaining
        )

        assert is_allowed is False
        assert "minute" in error.lower()


class TestGetRateLimitUpdateData:
    """Test suite for get_rate_limit_update_data function"""

    def test_returns_correct_fields(self):
        """Should return dictionary with correct field names"""
        result = get_rate_limit_update_data('test_action', 2)

        assert 'test_action_last_sent' in result
        assert 'test_action_count' in result
        assert result['test_action_count'] == 2

    def test_timestamp_is_recent(self):
        """Timestamp should be current"""
        result = get_rate_limit_update_data('test_action', 1)

        timestamp_str = result['test_action_last_sent']
        timestamp = datetime.fromisoformat(timestamp_str)

        # Should be within last second
        time_diff = datetime.now() - timestamp
        assert time_diff.total_seconds() < 1

    def test_works_with_different_actions(self):
        """Should work with any action name"""
        actions = ['email_verification', 'password_reset', 'api_call']

        for action in actions:
            result = get_rate_limit_update_data(action, 5)
            assert f'{action}_last_sent' in result
            assert f'{action}_count' in result
            assert result[f'{action}_count'] == 5
