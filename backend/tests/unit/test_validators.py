"""
Unit tests for validation functions
Tests all input validation logic
"""

import unittest
import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.utils import validators
except ImportError:
    # Fallback for direct execution
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "validators",
        os.path.join(backend_path, "app", "utils", "validators.py")
    )
    validators = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validators)


class TestValidators(unittest.TestCase):
    """Test suite for validation functions"""

    def test_validate_email_address_valid(self):
        """Test valid email addresses"""
        valid_emails = [
            "test@gmail.com",
            "user.name@outlook.com",
            "user+tag@yahoo.com"
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                valid, result, error = validators.validate_email_address(email)
                self.assertTrue(valid, f"Email {email} should be valid but got error: {error}")
                self.assertIsNotNone(result)
                self.assertEqual(error, "")

    def test_validate_email_address_invalid(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user@domain",
            ""
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                valid, result, error = validators.validate_email_address(email)
                self.assertFalse(valid)
                self.assertEqual(result, "")
                self.assertEqual(error, "Invalid email format")

    def test_validate_password_strength_valid(self):
        """Test valid passwords"""
        valid_passwords = [
            "TestPass123",
            "MySecure1Password",
            "Password1!"
        ]
        
        for password in valid_passwords:
            with self.subTest(password=password):
                valid, message = validators.validate_password_strength(password)
                self.assertTrue(valid)
                self.assertEqual(message, "Password is valid")

    def test_validate_password_strength_too_short(self):
        """Test password too short"""
        valid, message = validators.validate_password_strength("Test1")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must be at least 8 characters long")

    def test_validate_password_strength_no_uppercase(self):
        """Test password without uppercase"""
        valid, message = validators.validate_password_strength("testpass123")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must contain at least one uppercase letter")

    def test_validate_password_strength_no_lowercase(self):
        """Test password without lowercase"""
        valid, message = validators.validate_password_strength("TESTPASS123")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must contain at least one lowercase letter")

    def test_validate_password_strength_no_number(self):
        """Test password without numbers"""
        valid, message = validators.validate_password_strength("TestPassword")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must contain at least one number")

    def test_validate_required_fields_all_present(self):
        """Test when all required fields are present"""
        data = {"name": "John", "email": "john@example.com", "age": 25}
        required = ["name", "email", "age"]
        
        valid, message = validators.validate_required_fields(data, required)
        self.assertTrue(valid)
        self.assertEqual(message, "")

    def test_validate_required_fields_missing(self):
        """Test when required fields are missing"""
        data = {"name": "John", "email": ""}
        required = ["name", "email", "age"]
        
        valid, message = validators.validate_required_fields(data, required)
        self.assertFalse(valid)
        self.assertIn("Missing required fields", message)
        self.assertIn("email", message)
        self.assertIn("age", message)

    def test_validate_passwords_match_success(self):
        """Test when passwords match"""
        valid, message = validators.validate_passwords_match("password123", "password123")
        self.assertTrue(valid)
        self.assertEqual(message, "")

    def test_validate_passwords_match_fail(self):
        """Test when passwords don't match"""
        valid, message = validators.validate_passwords_match("password123", "different123")
        self.assertFalse(valid)
        self.assertEqual(message, "Passwords do not match")

    def test_validate_calendar_title_valid(self):
        """Test valid calendar titles"""
        valid_titles = [
            "My Calendar",
            "A",
            "x" * 100  # Exactly 100 characters
        ]
        
        for title in valid_titles:
            with self.subTest(title=title):
                valid, result, error = validators.validate_calendar_title(title)
                self.assertTrue(valid)
                self.assertEqual(result, title.strip())

    def test_validate_calendar_title_empty(self):
        """Test empty calendar title"""
        invalid_titles = ["", "   ", None]
        
        for title in invalid_titles:
            with self.subTest(title=title):
                valid, result, error = validators.validate_calendar_title(title)
                self.assertFalse(valid)
                self.assertEqual(error, "Title is required")

    def test_validate_calendar_title_too_long(self):
        """Test calendar title too long"""
        long_title = "x" * 101
        valid, result, error = validators.validate_calendar_title(long_title)
        self.assertFalse(valid)
        self.assertEqual(error, "Title must be 100 characters or less")

    def test_validate_calendar_duration_valid(self):
        """Test valid calendar durations"""
        valid_durations = [1, 15, 31, "25"]
        
        for duration in valid_durations:
            with self.subTest(duration=duration):
                valid, result, error = validators.validate_calendar_duration(duration)
                self.assertTrue(valid)
                self.assertEqual(result, int(duration))
                self.assertEqual(error, "")

    def test_validate_calendar_duration_invalid_range(self):
        """Test invalid duration ranges"""
        test_cases = [
            (0, "Duration must be at least 1 day"),
            (-1, "Duration must be at least 1 day"),
            (32, "Duration cannot exceed 31 days"),
            (100, "Duration cannot exceed 31 days")
        ]
        
        for duration, expected_error in test_cases:
            with self.subTest(duration=duration):
                valid, result, error = validators.validate_calendar_duration(duration)
                self.assertFalse(valid)
                self.assertEqual(result, 0)
                self.assertEqual(error, expected_error)

    def test_validate_calendar_duration_invalid_type(self):
        """Test invalid duration types"""
        invalid_durations = ["abc", None, [], {}]
        
        for duration in invalid_durations:
            with self.subTest(duration=duration):
                valid, result, error = validators.validate_calendar_duration(duration)
                self.assertFalse(valid)
                self.assertEqual(result, 0)
                self.assertEqual(error, "Duration must be a valid number")

    def test_validate_calendar_start_date_valid(self):
        """Test valid start dates"""
        valid_dates = [
            "2026-12-01",
            "2027-01-01",
            "2026-12-31"
        ]
        
        for date in valid_dates:
            with self.subTest(date=date):
                valid, result, error = validators.validate_calendar_start_date(date)
                self.assertTrue(valid)
                self.assertEqual(result, date)
                self.assertEqual(error, "")

    def test_validate_calendar_start_date_empty(self):
        """Test empty start date"""
        empty_dates = ["", "   ", None]
        
        for date in empty_dates:
            with self.subTest(date=date):
                valid, result, error = validators.validate_calendar_start_date(date)
                self.assertFalse(valid)
                self.assertEqual(result, "")
                self.assertEqual(error, "Start date is required")

    def test_validate_calendar_start_date_invalid_format(self):
        """Test invalid date formats"""
        invalid_dates = [
            "12/01/2025",
            "2025-1-1",
            "2025/12/01",
            "01-12-2025",
            "not-a-date"
        ]
        
        for date in invalid_dates:
            with self.subTest(date=date):
                valid, result, error = validators.validate_calendar_start_date(date)
                self.assertFalse(valid)
                self.assertEqual(result, "")
                self.assertIn("YYYY-MM-DD", error)

    def test_validate_calendar_start_date_invalid_date(self):
        """Test invalid dates that match format but aren't real dates"""
        invalid_dates = [
            "2025-13-01",  # Invalid month
            "2025-02-30",  # Invalid day for February
            "2025-04-31"   # Invalid day for April
        ]
        
        for date in invalid_dates:
            with self.subTest(date=date):
                valid, result, error = validators.validate_calendar_start_date(date)
                self.assertFalse(valid)
                self.assertEqual(result, "")
                self.assertEqual(error, "Invalid date provided")


if __name__ == '__main__':
    unittest.main()