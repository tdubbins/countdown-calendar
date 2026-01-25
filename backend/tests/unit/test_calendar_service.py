# Unit Tests for Calendar Service
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_path)

try:
    from app.services.calendar_service import update_calendar, get_calendar_by_id, create_calendar, delete_calendar
except ImportError:
    import unittest
    raise unittest.SkipTest("Flask dependencies not available")

class TestCalendarService(unittest.TestCase):
    """Unit tests for calendar service functions"""
    
    def setUp(self):
        """Set up test data"""
        self.test_user_id = "test-user-123"
        self.test_calendar_id = "test-calendar-456"
        self.existing_calendar = {
            'id': self.test_calendar_id,
            'title': 'Original Title',
            'startDate': '2026-12-01',
            'duration': 25,
            'endDate': '2026-12-25',
            'dateRange': '2026-12-01 to 2026-12-25',
            'userId': self.test_user_id,
            'createdAt': '2026-10-29T10:00:00Z',
            'updatedAt': '2026-10-29T10:00:00Z'
        }

    @patch('app.services.calendar_service.get_calendar_by_id')
    @patch('app.services.calendar_service.calendars_db')
    def test_update_calendar_title_success(self, mock_db, mock_get_calendar):
        """Test successful calendar title update"""
        # Mock calendar exists and user owns it
        mock_get_calendar.return_value = (True, self.existing_calendar, "")
        
        # Mock database update success
        updated_calendar = self.existing_calendar.copy()
        updated_calendar['title'] = 'New Title'
        mock_db.update_calendar_meta.return_value = updated_calendar
        
        # Test update
        success, result, error = update_calendar(
            self.test_calendar_id, 
            self.test_user_id, 
            title='New Title'
        )
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(result['title'], 'New Title')
        self.assertEqual(error, "")
        mock_db.update_calendar_meta.assert_called_once()

    @patch('app.services.calendar_service.get_calendar_by_id')
    @patch('app.services.calendar_service.calendars_db')
    def test_update_calendar_start_date_and_duration(self, mock_db, mock_get_calendar):
        """Test updating start date and duration recalculates end date"""
        # Mock calendar exists and user owns it
        mock_get_calendar.return_value = (True, self.existing_calendar, "")
        
        # Mock database update success
        updated_calendar = self.existing_calendar.copy()
        updated_calendar.update({
            'startDate': '2026-12-10',
            'duration': 15,
            'endDate': '2026-12-24',
            'dateRange': '2026-12-10 to 2026-12-24'
        })
        mock_db.update_calendar_meta.return_value = updated_calendar
        
        # Test update
        success, result, error = update_calendar(
            self.test_calendar_id,
            self.test_user_id,
            start_date='2026-12-10',
            duration=15
        )
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(result['startDate'], '2026-12-10')
        self.assertEqual(result['duration'], 15)
        self.assertEqual(result['endDate'], '2026-12-24')
        self.assertEqual(result['dateRange'], '2026-12-10 to 2026-12-24')

    @patch('app.services.calendar_service.get_calendar_by_id')
    def test_update_calendar_not_found(self, mock_get_calendar):
        """Test update when calendar doesn't exist"""
        # Mock calendar not found
        mock_get_calendar.return_value = (False, {}, "Calendar not found")
        
        # Test update
        success, result, error = update_calendar(
            "nonexistent-id",
            self.test_user_id,
            title='New Title'
        )
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(result, {})
        self.assertEqual(error, "Calendar not found")

    @patch('app.services.calendar_service.get_calendar_by_id')
    def test_update_calendar_invalid_title(self, mock_get_calendar):
        """Test update with invalid title"""
        # Mock calendar exists and user owns it
        mock_get_calendar.return_value = (True, self.existing_calendar, "")
        
        # Test update with invalid title (too long)
        success, result, error = update_calendar(
            self.test_calendar_id,
            self.test_user_id,
            title='x' * 101  # Exceeds 100 character limit
        )
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(result, {})
        self.assertIn("100 characters", error)

    @patch('app.services.calendar_service.get_calendar_by_id')
    def test_update_calendar_invalid_duration(self, mock_get_calendar):
        """Test update with invalid duration"""
        # Mock calendar exists and user owns it
        mock_get_calendar.return_value = (True, self.existing_calendar, "")
        
        # Test update with invalid duration (too high)
        success, result, error = update_calendar(
            self.test_calendar_id,
            self.test_user_id,
            duration=50  # Exceeds 31 day limit
        )
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(result, {})
        self.assertIn("cannot exceed 31", error)

    @patch('app.services.calendar_service.get_calendar_by_id')
    def test_update_calendar_invalid_date(self, mock_get_calendar):
        """Test update with invalid date format"""
        # Mock calendar exists and user owns it
        mock_get_calendar.return_value = (True, self.existing_calendar, "")
        
        # Test update with invalid date format
        success, result, error = update_calendar(
            self.test_calendar_id,
            self.test_user_id,
            start_date='invalid-date'
        )
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(result, {})
        self.assertIn("YYYY-MM-DD", error)

    @patch('app.services.calendar_service.get_calendar_by_id')
    @patch('app.services.calendar_service.calendars_db')
    def test_update_calendar_no_fields(self, mock_db, mock_get_calendar):
        """Test update with no fields provided (should still update updatedAt)"""
        # Mock calendar exists and user owns it
        mock_get_calendar.return_value = (True, self.existing_calendar, "")

        # Mock database update success (will only have updatedAt field)
        updated_calendar = self.existing_calendar.copy()
        updated_calendar['updatedAt'] = '2026-11-13T12:00:00Z'
        mock_db.update_calendar_meta.return_value = updated_calendar

        # Test update with no fields (should still succeed with updatedAt)
        success, result, error = update_calendar(
            self.test_calendar_id,
            self.test_user_id
        )

        # Assertions - should succeed with only updatedAt updated
        self.assertTrue(success)
        self.assertIn('updatedAt', result)
        self.assertEqual(error, "")

    @patch('app.services.calendar_service.get_calendar_by_id')
    @patch('app.services.calendar_service.calendars_db')
    def test_update_calendar_database_error(self, mock_db, mock_get_calendar):
        """Test update when database fails"""
        # Mock calendar exists and user owns it
        mock_get_calendar.return_value = (True, self.existing_calendar, "")
        
        # Mock database update failure
        mock_db.update_calendar_meta.return_value = None
        
        # Test update
        success, result, error = update_calendar(
            self.test_calendar_id,
            self.test_user_id,
            title='New Title'
        )
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(result, {})
        self.assertEqual(error, "Failed to update calendar")

if __name__ == '__main__':
    unittest.main()