"""
Unit tests for video storage utilities
Tests file path generation, cleanup functions, and security
Updated for per-calendar folder structure (no user_id in paths)
Updated to use valid UUID format for calendar IDs (security requirement)
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.utils import storage

# Valid UUID for testing (must use real UUIDs since security update)
TEST_CALENDAR_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_CALENDAR_ID_2 = "550e8400-e29b-41d4-a716-446655440001"


class TestStorageUtilities(unittest.TestCase):
    """Test suite for storage utility functions"""

    def setUp(self):
        """Set up test fixtures - create temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_calendars_base = storage.CALENDARS_BASE_DIR

        # Override base directory to use test directory
        storage.CALENDARS_BASE_DIR = Path(self.test_dir) / "calendars"

    def tearDown(self):
        """Clean up test fixtures"""
        # Restore original path
        storage.CALENDARS_BASE_DIR = self.original_calendars_base

        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_video_path_creates_directory(self):
        """Test that get_video_path returns correct path"""
        path = storage.get_video_path(TEST_CALENDAR_ID, 1)

        # Verify path structure
        self.assertEqual(path.name, "day_1.mp4")
        self.assertIn(TEST_CALENDAR_ID, str(path))
        self.assertIn("videos", str(path))

        # Create directory and verify it works
        path.parent.mkdir(parents=True, exist_ok=True)
        self.assertTrue(path.parent.exists(), "Video directory should be creatable")

    def test_get_video_path_naming_convention(self):
        """Test video file naming follows convention"""
        test_cases = [
            (1, "day_1.mp4"),
            (15, "day_15.mp4"),
            (31, "day_31.mp4")
        ]

        for day, expected_name in test_cases:
            with self.subTest(day=day):
                path = storage.get_video_path(TEST_CALENDAR_ID, day)
                self.assertEqual(path.name, expected_name)

    def test_get_video_path_invalid_day(self):
        """Test get_video_path rejects invalid day numbers"""
        invalid_days = [0, -1, 32, 100]

        for day in invalid_days:
            with self.subTest(day=day):
                with self.assertRaises(ValueError):
                    storage.get_video_path(TEST_CALENDAR_ID, day)

    def test_get_video_path_sanitization(self):
        """Test path sanitization prevents directory traversal"""
        malicious_inputs = [
            "../../../etc/passwd",
            "../../secret",
            "cal/../admin",
            "cal\\..\\admin"
        ]

        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                with self.assertRaises(ValueError):
                    storage.get_video_path(malicious_input, 1)

    def test_get_thumbnail_path_creates_directory(self):
        """Test that get_thumbnail_path returns correct path"""
        path = storage.get_thumbnail_path(TEST_CALENDAR_ID, 1)

        # Verify path structure
        self.assertEqual(path.name, "day_1_thumb.jpg")
        self.assertIn(TEST_CALENDAR_ID, str(path))
        self.assertIn("thumbnails", str(path))

        # Create directory and verify it works
        path.parent.mkdir(parents=True, exist_ok=True)
        self.assertTrue(path.parent.exists(), "Thumbnail directory should be creatable")

    def test_get_thumbnail_path_naming_convention(self):
        """Test thumbnail file naming follows convention"""
        test_cases = [
            (1, "day_1_thumb.jpg"),
            (15, "day_15_thumb.jpg"),
            (31, "day_31_thumb.jpg")
        ]

        for day, expected_name in test_cases:
            with self.subTest(day=day):
                path = storage.get_thumbnail_path(TEST_CALENDAR_ID, day)
                self.assertEqual(path.name, expected_name)

    def test_multi_tenant_isolation(self):
        """Test that different calendars have isolated directories"""
        cal1_path = storage.get_video_path(TEST_CALENDAR_ID, 1)
        cal2_path = storage.get_video_path(TEST_CALENDAR_ID_2, 1)

        self.assertNotEqual(cal1_path.parent, cal2_path.parent)
        self.assertIn(TEST_CALENDAR_ID, str(cal1_path))
        self.assertIn(TEST_CALENDAR_ID_2, str(cal2_path))

    def test_delete_video_file_removes_both_files(self):
        """Test delete_video_file removes both video and thumbnail"""
        # Create dummy files
        video_path = storage.get_video_path(TEST_CALENDAR_ID, 5)
        thumbnail_path = storage.get_thumbnail_path(TEST_CALENDAR_ID, 5)

        # Create directories first
        video_path.parent.mkdir(parents=True, exist_ok=True)
        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

        video_path.touch()
        thumbnail_path.touch()

        # Verify files exist
        self.assertTrue(video_path.exists())
        self.assertTrue(thumbnail_path.exists())

        # Delete
        result = storage.delete_video_file(TEST_CALENDAR_ID, 5)

        # Verify deletion
        self.assertTrue(result)
        self.assertFalse(video_path.exists())
        self.assertFalse(thumbnail_path.exists())

    def test_delete_video_file_nonexistent(self):
        """Test delete_video_file handles nonexistent files gracefully"""
        result = storage.delete_video_file(TEST_CALENDAR_ID, 5)
        self.assertFalse(result)  # Should return False when nothing to delete

    def test_delete_calendar_files_removes_directory(self):
        """Test delete_calendar_files removes video and thumbnail subdirectories"""
        # Create directory structure
        calendar_dir = storage.CALENDARS_BASE_DIR / TEST_CALENDAR_ID
        calendar_dir.mkdir(parents=True, exist_ok=True)

        # Create multiple video files
        for day in [1, 2, 3]:
            video_path = storage.get_video_path(TEST_CALENDAR_ID, day)
            thumbnail_path = storage.get_thumbnail_path(TEST_CALENDAR_ID, day)

            video_path.parent.mkdir(parents=True, exist_ok=True)
            thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

            video_path.touch()
            thumbnail_path.touch()

        video_dir = storage.get_calendar_video_dir(TEST_CALENDAR_ID)
        thumbnail_dir = storage.get_calendar_thumbnail_dir(TEST_CALENDAR_ID)

        # Verify directories exist
        self.assertTrue(video_dir.exists())
        self.assertTrue(thumbnail_dir.exists())

        # Delete calendar files (videos and thumbnails subdirectories)
        result = storage.delete_calendar_files(TEST_CALENDAR_ID)

        # Verify deletion of subdirectories
        self.assertTrue(result)
        self.assertFalse(video_dir.exists())
        self.assertFalse(thumbnail_dir.exists())
        # Parent calendar directory may still exist (that's OK - deleted by CalendarDatabase)

    def test_get_calendar_storage_size(self):
        """Test storage size calculation"""
        # Create test files with known sizes
        for day in [1, 2, 3]:
            video_path = storage.get_video_path(TEST_CALENDAR_ID, day)
            video_path.parent.mkdir(parents=True, exist_ok=True)
            video_path.write_bytes(b"x" * 1000)  # 1000 bytes each

        size = storage.get_calendar_storage_size(TEST_CALENDAR_ID)
        self.assertEqual(size, 3000)  # 3 files * 1000 bytes

    def test_get_calendar_storage_size_empty(self):
        """Test storage size for calendar with no videos"""
        size = storage.get_calendar_storage_size(TEST_CALENDAR_ID)
        self.assertEqual(size, 0)

    def test_list_calendar_videos(self):
        """Test listing video day numbers"""
        # Create videos for specific days
        days = [1, 5, 10, 15]
        for day in days:
            video_path = storage.get_video_path(TEST_CALENDAR_ID, day)
            video_path.parent.mkdir(parents=True, exist_ok=True)
            video_path.touch()

        result = storage.list_calendar_videos(TEST_CALENDAR_ID)

        self.assertEqual(sorted(result), sorted(days))
        self.assertIsInstance(result, list)

    def test_list_calendar_videos_empty(self):
        """Test listing videos for calendar with no videos"""
        result = storage.list_calendar_videos(TEST_CALENDAR_ID)
        self.assertEqual(result, [])

    def test_ensure_upload_directories(self):
        """Test that ensure_upload_directories creates base structure"""
        # Remove test directory
        if storage.CALENDARS_BASE_DIR.exists():
            shutil.rmtree(storage.CALENDARS_BASE_DIR)

        # Call initialization
        storage.ensure_upload_directories()

        # Verify base directory created
        self.assertTrue(storage.CALENDARS_BASE_DIR.exists())

    def test_get_calendar_video_dir(self):
        """Test get_calendar_video_dir returns correct path"""
        video_dir = storage.get_calendar_video_dir(TEST_CALENDAR_ID)

        # Use resolve() for comparison since security code returns resolved paths
        expected_path = (storage.CALENDARS_BASE_DIR / TEST_CALENDAR_ID / "videos").resolve()
        self.assertEqual(video_dir, expected_path)

    def test_get_calendar_thumbnail_dir(self):
        """Test get_calendar_thumbnail_dir returns correct path"""
        thumbnail_dir = storage.get_calendar_thumbnail_dir(TEST_CALENDAR_ID)

        # Use resolve() for comparison since security code returns resolved paths
        expected_path = (storage.CALENDARS_BASE_DIR / TEST_CALENDAR_ID / "thumbnails").resolve()
        self.assertEqual(thumbnail_dir, expected_path)


if __name__ == '__main__':
    unittest.main()
