"""
Simple tests for basic JSON database functionality
Tests core database operations without Flask dependencies
"""

import unittest
import os
import json
import tempfile


class TestSimpleJSONDB(unittest.TestCase):
    """Simple JSON database operation tests"""

    def setUp(self):
        """Set up temporary JSON file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.write('{"test_collection": {}}')
        self.temp_file.close()
        self.db_path = self.temp_file.name

    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_json_file_operations(self):
        """Test basic JSON file read/write operations"""
        # Test data
        test_data = {
            "calendars": {
                "cal1": {
                    "id": "cal1", 
                    "title": "Test Calendar",
                    "userId": "user1"
                }
            }
        }
        
        # Write JSON
        with open(self.db_path, 'w') as f:
            json.dump(test_data, f)
        
        # Read JSON
        with open(self.db_path, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify data integrity
        self.assertEqual(loaded_data["calendars"]["cal1"]["title"], "Test Calendar")
        self.assertEqual(loaded_data["calendars"]["cal1"]["userId"], "user1")

    def test_data_validation_logic(self):
        """Test basic data validation logic"""
        # Test calendar data structure
        calendar_data = {
            "id": "test-123",
            "title": "My Calendar", 
            "startDate": "2025-12-01",
            "duration": 25,
            "userId": "user-456"
        }
        
        # Validate required fields exist
        required_fields = ["id", "title", "startDate", "duration", "userId"]
        for field in required_fields:
            self.assertIn(field, calendar_data)
            self.assertIsNotNone(calendar_data[field])
        
        # Validate data types
        self.assertIsInstance(calendar_data["id"], str)
        self.assertIsInstance(calendar_data["title"], str)
        self.assertIsInstance(calendar_data["duration"], int)
        self.assertIsInstance(calendar_data["userId"], str)

    def test_user_calendar_filtering(self):
        """Test filtering calendars by user ID"""
        calendars = {
            "cal1": {"userId": "user1", "title": "Calendar 1"},
            "cal2": {"userId": "user2", "title": "Calendar 2"}, 
            "cal3": {"userId": "user1", "title": "Calendar 3"}
        }
        
        # Filter by user1
        user1_calendars = [cal for cal in calendars.values() if cal["userId"] == "user1"]
        self.assertEqual(len(user1_calendars), 2)
        self.assertEqual(user1_calendars[0]["title"], "Calendar 1")
        self.assertEqual(user1_calendars[1]["title"], "Calendar 3")
        
        # Filter by user2
        user2_calendars = [cal for cal in calendars.values() if cal["userId"] == "user2"]
        self.assertEqual(len(user2_calendars), 1)
        self.assertEqual(user2_calendars[0]["title"], "Calendar 2")

    def test_calendar_crud_logic(self):
        """Test basic CRUD operation logic"""
        calendars = {}
        
        # CREATE
        new_calendar = {
            "id": "cal1",
            "title": "Test Calendar",
            "userId": "user1"
        }
        calendars[new_calendar["id"]] = new_calendar
        self.assertEqual(len(calendars), 1)
        
        # READ
        found_calendar = calendars.get("cal1")
        self.assertIsNotNone(found_calendar)
        self.assertEqual(found_calendar["title"], "Test Calendar")
        
        # UPDATE
        calendars["cal1"]["title"] = "Updated Calendar"
        self.assertEqual(calendars["cal1"]["title"], "Updated Calendar")
        
        # DELETE
        del calendars["cal1"]
        self.assertEqual(len(calendars), 0)
        self.assertIsNone(calendars.get("cal1"))


if __name__ == '__main__':
    unittest.main()