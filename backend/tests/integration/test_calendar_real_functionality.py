"""
Simple integration tests for calendar functionality
Tests real calendar service functions with actual data
"""

import unittest
import tempfile
import os
import json
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_path)

try:
    from app.services.calendar_service import create_calendar, get_user_calendars, get_calendar_by_id, update_calendar, delete_calendar
    from app.utils.json_db import JSONDatabase
except ImportError:
    # Skip if imports fail
    import unittest
    raise unittest.SkipTest("Flask dependencies not available")


class TestCalendarRealFunctionality(unittest.TestCase):
    """Integration tests for real calendar functionality"""

    def setUp(self):
        """Set up temporary database for testing"""
        # Create temporary JSON file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.write('{"calendars": {}}')
        self.temp_file.close()
        
        # Replace the calendars_db with our test database
        from app.utils import json_db
        self.original_db = json_db.calendars_db
        json_db.calendars_db = JSONDatabase(self.temp_file.name)
        
        # Also patch the import in calendar_service
        from app.services import calendar_service
        calendar_service.calendars_db = json_db.calendars_db
        
        self.test_user_id = "test-user-123"

    def tearDown(self):
        """Clean up temporary database"""
        # Restore original database
        from app.utils import json_db
        from app.services import calendar_service
        json_db.calendars_db = self.original_db
        calendar_service.calendars_db = self.original_db
        
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_calendar_crud_workflow(self):
        """Test complete calendar CRUD workflow"""
        
        # 1. CREATE - Test calendar creation
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="My Advent Calendar",
            start_date="2025-12-01",
            duration=25
        )
        
        self.assertTrue(success, f"Calendar creation failed: {error}")
        self.assertIsNotNone(calendar_data.get('id'))
        self.assertEqual(calendar_data['title'], "My Advent Calendar")
        self.assertEqual(calendar_data['startDate'], "2025-12-01")
        self.assertEqual(calendar_data['duration'], 25)
        self.assertEqual(calendar_data['endDate'], "2025-12-25")
        self.assertEqual(calendar_data['userId'], self.test_user_id)
        
        calendar_id = calendar_data['id']
        
        # 2. READ - Test getting user calendars
        success, calendars, error = get_user_calendars(self.test_user_id)
        
        self.assertTrue(success, f"Get calendars failed: {error}")
        self.assertEqual(len(calendars), 1)
        self.assertEqual(calendars[0]['id'], calendar_id)
        
        # 3. READ SINGLE - Test getting calendar by ID
        success, found_calendar, error = get_calendar_by_id(calendar_id, self.test_user_id)
        
        self.assertTrue(success, f"Get calendar by ID failed: {error}")
        self.assertEqual(found_calendar['id'], calendar_id)
        self.assertEqual(found_calendar['title'], "My Advent Calendar")
        
        # 4. UPDATE - Test updating calendar
        success, updated_calendar, error = update_calendar(
            calendar_id=calendar_id,
            user_id=self.test_user_id,
            title="Updated Calendar Title",
            duration=20
        )
        
        self.assertTrue(success, f"Calendar update failed: {error}")
        self.assertEqual(updated_calendar['title'], "Updated Calendar Title")
        self.assertEqual(updated_calendar['duration'], 20)
        self.assertEqual(updated_calendar['endDate'], "2025-12-20")  # Should recalculate
        
        # 5. DELETE - Test deleting calendar
        success, error = delete_calendar(calendar_id, self.test_user_id)
        
        self.assertTrue(success, f"Calendar deletion failed: {error}")
        
        # 6. VERIFY DELETION - Calendar should no longer exist
        success, found_calendar, error = get_calendar_by_id(calendar_id, self.test_user_id)
        
        self.assertFalse(success)
        self.assertIn("not found", error.lower())

    def test_multiple_calendars_same_user(self):
        """Test multiple calendars for the same user"""
        
        # Create first calendar
        success1, cal1, error1 = create_calendar(
            user_id=self.test_user_id,
            title="Calendar 1",
            start_date="2025-12-01",
            duration=25
        )
        self.assertTrue(success1)
        
        # Create second calendar
        success2, cal2, error2 = create_calendar(
            user_id=self.test_user_id,
            title="Calendar 2", 
            start_date="2025-11-01",
            duration=30
        )
        self.assertTrue(success2)
        
        # Get all calendars for user
        success, calendars, error = get_user_calendars(self.test_user_id)
        
        self.assertTrue(success)
        self.assertEqual(len(calendars), 2)
        
        # Verify both calendars exist
        calendar_titles = [cal['title'] for cal in calendars]
        self.assertIn("Calendar 1", calendar_titles)
        self.assertIn("Calendar 2", calendar_titles)

    def test_calendar_ownership_security(self):
        """Test that users can only access their own calendars"""
        
        user1_id = "user1"
        user2_id = "user2"
        
        # User1 creates a calendar
        success, calendar_data, error = create_calendar(
            user_id=user1_id,
            title="User1's Calendar",
            start_date="2025-12-01",
            duration=25
        )
        self.assertTrue(success)
        calendar_id = calendar_data['id']
        
        # User1 can access their calendar
        success, found_calendar, error = get_calendar_by_id(calendar_id, user1_id)
        self.assertTrue(success)
        self.assertEqual(found_calendar['title'], "User1's Calendar")
        
        # User2 cannot access User1's calendar
        success, found_calendar, error = get_calendar_by_id(calendar_id, user2_id)
        self.assertFalse(success)
        self.assertIn("not found", error.lower())
        
        # User2 cannot update User1's calendar
        success, updated_calendar, error = update_calendar(
            calendar_id=calendar_id,
            user_id=user2_id,
            title="Hacked Title"
        )
        self.assertFalse(success)
        self.assertIn("not found", error.lower())
        
        # User2 cannot delete User1's calendar
        success, error = delete_calendar(calendar_id, user2_id)
        self.assertFalse(success)
        self.assertIn("not found", error.lower())

    def test_calendar_validation_integration(self):
        """Test validation works in real integration"""
        
        # Test invalid title (too long)
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="x" * 101,  # Too long
            start_date="2025-12-01",
            duration=25
        )
        self.assertFalse(success)
        self.assertIn("100 characters", error)
        
        # Test invalid duration (too high)
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="Valid Title",
            start_date="2025-12-01",
            duration=50  # Too high
        )
        self.assertFalse(success)
        self.assertIn("cannot exceed 31", error)
        
        # Test invalid date format
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="Valid Title",
            start_date="12/01/2025",  # Wrong format
            duration=25
        )
        self.assertFalse(success)
        self.assertIn("YYYY-MM-DD", error)

    def test_calendar_date_calculations(self):
        """Test that date calculations work correctly"""
        
        # Test 31-day calendar starting Dec 1
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="Full Month Calendar",
            start_date="2025-12-01",
            duration=31
        )
        
        self.assertTrue(success)
        self.assertEqual(calendar_data['startDate'], "2025-12-01")
        self.assertEqual(calendar_data['endDate'], "2025-12-31")
        self.assertEqual(calendar_data['dateRange'], "2025-12-01 to 2025-12-31")
        
        # Test 1-day calendar
        success, calendar_data, error = create_calendar(
            user_id=self.test_user_id,
            title="Single Day",
            start_date="2025-12-25",
            duration=1
        )
        
        self.assertTrue(success)
        self.assertEqual(calendar_data['startDate'], "2025-12-25")
        self.assertEqual(calendar_data['endDate'], "2025-12-25")
        self.assertEqual(calendar_data['dateRange'], "2025-12-25 to 2025-12-25")

    def test_empty_database_scenarios(self):
        """Test behavior with empty database"""
        
        # Get calendars for user with no calendars
        success, calendars, error = get_user_calendars("nonexistent-user")
        
        self.assertTrue(success)
        self.assertEqual(len(calendars), 0)
        
        # Try to get nonexistent calendar
        success, calendar_data, error = get_calendar_by_id("nonexistent-id", self.test_user_id)
        
        self.assertFalse(success)
        self.assertIn("not found", error.lower())


if __name__ == '__main__':
    unittest.main()