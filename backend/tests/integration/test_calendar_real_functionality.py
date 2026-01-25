"""
Simple integration tests for calendar functionality
Tests real calendar service functions with actual data
Updated for per-calendar folder structure
"""

import unittest
import tempfile
import os
import shutil
import json
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_path)

try:
    from app.services.calendar_service import create_calendar, get_user_calendars, get_calendar_by_id, update_calendar, delete_calendar
    from app.utils.json_db import CalendarDatabase, JSONDatabase
except ImportError:
    # Skip if imports fail
    import unittest
    raise unittest.SkipTest("Flask dependencies not available")


class TestCalendarRealFunctionality(unittest.TestCase):
    """Integration tests for real calendar functionality"""

    def setUp(self):
        """Set up temporary directories for testing"""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.temp_calendars_dir = os.path.join(self.temp_dir, 'calendars')
        self.temp_users_file = os.path.join(self.temp_dir, 'users.json')
        os.makedirs(self.temp_calendars_dir)

        # Create a temporary users.json with test user
        test_users_data = {
            'users': {
                'test-user-123': {
                    'id': 'test-user-123',
                    'email': 'test@example.com',
                    'calendar_ids': []
                }
            }
        }
        with open(self.temp_users_file, 'w') as f:
            json.dump(test_users_data, f)

        # Replace the databases with our test databases
        from app.utils import json_db

        self.original_calendars_dir = CalendarDatabase.CALENDARS_DIR
        self.original_users_db = json_db.users_db

        CalendarDatabase.CALENDARS_DIR = self.temp_calendars_dir
        json_db.users_db = JSONDatabase(self.temp_users_file)

        # Also patch the import in calendar_service
        from app.services import calendar_service
        calendar_service.calendars_db.CALENDARS_DIR = self.temp_calendars_dir

        self.test_user_id = "test-user-123"

    def tearDown(self):
        """Clean up temporary directories"""
        # Restore original databases
        from app.utils import json_db
        from app.services import calendar_service

        CalendarDatabase.CALENDARS_DIR = self.original_calendars_dir
        json_db.users_db = self.original_users_db
        calendar_service.calendars_db.CALENDARS_DIR = self.original_calendars_dir

        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_calendar_crud_workflow(self):
        """Test complete calendar CRUD workflow"""

        # 1. CREATE - Test calendar creation
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="My Advent Calendar",
            start_date="2026-12-01",
            duration=25
        )

        self.assertTrue(success, f"Calendar creation failed: {error}")
        self.assertIsNotNone(calendar_data.get('id'))
        self.assertEqual(calendar_data['title'], "My Advent Calendar")
        self.assertEqual(calendar_data['startDate'], "2026-12-01")
        self.assertEqual(calendar_data['duration'], 25)
        self.assertEqual(calendar_data['endDate'], "2026-12-25")

        calendar_id = calendar_data['id']

        # Verify calendar folder was created
        calendar_dir = os.path.join(self.temp_calendars_dir, calendar_id)
        self.assertTrue(os.path.exists(calendar_dir))
        self.assertTrue(os.path.exists(os.path.join(calendar_dir, 'meta.json')))
        self.assertTrue(os.path.exists(os.path.join(calendar_dir, 'videos')))
        self.assertTrue(os.path.exists(os.path.join(calendar_dir, 'thumbnails')))

        # 2. READ - Test getting user calendars
        success, calendars, error = get_user_calendars(self.test_user_id)

        self.assertTrue(success)
        self.assertEqual(len(calendars), 1)
        self.assertEqual(calendars[0]['id'], calendar_id)
        self.assertEqual(calendars[0]['title'], "My Advent Calendar")

        # 3. READ BY ID - Test getting specific calendar
        success, retrieved_calendar, error = get_calendar_by_id(calendar_id, self.test_user_id)

        self.assertTrue(success)
        self.assertEqual(retrieved_calendar['id'], calendar_id)
        self.assertEqual(retrieved_calendar['title'], "My Advent Calendar")

        # 4. UPDATE - Test updating calendar
        success, updated_calendar, error = update_calendar(
            calendar_id=calendar_id,
            user_id=self.test_user_id,
            title="Updated Calendar Title",
            description="New description"
        )

        self.assertTrue(success, f"Calendar update failed: {error}")
        self.assertEqual(updated_calendar['title'], "Updated Calendar Title")
        self.assertEqual(updated_calendar['description'], "New description")

        # 5. DELETE - Test deleting calendar
        success, error = delete_calendar(calendar_id, self.test_user_id)

        self.assertTrue(success, f"Calendar deletion failed: {error}")

        # Verify calendar folder was deleted
        self.assertFalse(os.path.exists(calendar_dir))

        # Verify calendar removed from user's calendar_ids
        success, calendars, error = get_user_calendars(self.test_user_id)
        self.assertTrue(success)
        self.assertEqual(len(calendars), 0)

    def test_calendar_date_calculations(self):
        """Test calendar end date calculations"""

        test_cases = [
            (1, "2026-12-01", "2026-12-01"),   # 1 day calendar
            (7, "2026-12-01", "2026-12-07"),   # 7 day calendar
            (25, "2026-12-01", "2026-12-25"),  # 25 day calendar
            (31, "2026-12-01", "2026-12-31"),  # 31 day calendar
        ]

        for duration, start_date, expected_end_date in test_cases:
            with self.subTest(duration=duration):
                success, calendar_data, error = create_calendar(
                    user_id=self.test_user_id,
                    title=f"Test {duration} Day Calendar",
                    start_date=start_date,
                    duration=duration
                )

                self.assertTrue(success)
                self.assertEqual(calendar_data['endDate'], expected_end_date)

                # Clean up
                calendar_id = calendar_data['id']
                delete_calendar(calendar_id, self.test_user_id)

    def test_calendar_ownership_security(self):
        """Test that users can only access their own calendars"""

        # Create calendar for test user
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="User 1 Calendar",
            start_date="2026-12-01",
            duration=25
        )
        self.assertTrue(success)
        calendar_id = calendar_data['id']

        # Try to access with different user (should fail or not include it in their list)
        different_user_id = "different-user-456"
        success, calendars, error = get_user_calendars(different_user_id)

        # Different user should have empty calendar list
        self.assertTrue(success)
        self.assertEqual(len(calendars), 0)

        # Clean up
        delete_calendar(calendar_id, self.test_user_id)

    def test_calendar_validation_integration(self):
        """Test calendar creation with invalid input"""

        # Test invalid title
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="",  # Empty title
            start_date="2026-12-01",
            duration=25
        )
        self.assertFalse(success)
        self.assertIn("title", error.lower())

        # Test invalid duration
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="Valid Title",
            start_date="2026-12-01",
            duration=0  # Invalid duration
        )
        self.assertFalse(success)
        self.assertIn("duration", error.lower())

        # Test invalid date format
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="Valid Title",
            start_date="invalid-date",
            duration=25
        )
        self.assertFalse(success)

    def test_empty_database_scenarios(self):
        """Test behavior with empty/non-existent calendars"""

        # Test getting calendars for user with no calendars
        success, calendars, error = get_user_calendars(self.test_user_id)
        self.assertTrue(success)
        self.assertEqual(len(calendars), 0)

        # Test getting non-existent calendar
        success, calendar, error = get_calendar_by_id("non-existent-id", self.test_user_id)
        self.assertFalse(success)
        self.assertIn("not found", error.lower())

        # Test deleting non-existent calendar
        success, error = delete_calendar("non-existent-id", self.test_user_id)
        self.assertFalse(success)

    def test_multiple_calendars_same_user(self):
        """Test user can have multiple calendars"""

        calendar_ids = []

        # Create 3 calendars
        for i in range(3):
            success, calendar_data, error = create_calendar(
                user_id=self.test_user_id,
                title=f"Calendar {i+1}",
                start_date="2026-12-01",
                duration=25
            )
            self.assertTrue(success)
            calendar_ids.append(calendar_data['id'])

        # Verify user has all 3 calendars
        success, calendars, error = get_user_calendars(self.test_user_id)
        self.assertTrue(success)
        self.assertEqual(len(calendars), 3)

        # Clean up
        for calendar_id in calendar_ids:
            delete_calendar(calendar_id, self.test_user_id)


if __name__ == '__main__':
    unittest.main()
