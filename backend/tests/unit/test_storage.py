"""
Unit tests for video storage utilities
Tests file path generation, cleanup functions, and security
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


class TestStorageUtilities(unittest.TestCase):
    """Test suite for storage utility functions"""

    def setUp(self):
        """Set up test fixtures - create temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_video_base = storage.VIDEO_BASE_DIR
        self.original_thumbnail_base = storage.THUMBNAIL_BASE_DIR

        # Override base directories to use test directory
        storage.VIDEO_BASE_DIR = Path(self.test_dir) / "videos"
        storage.THUMBNAIL_BASE_DIR = Path(self.test_dir) / "thumbnails"

    def tearDown(self):
        """Clean up test fixtures"""
        # Restore original paths
        storage.VIDEO_BASE_DIR = self.original_video_base
        storage.THUMBNAIL_BASE_DIR = self.original_thumbnail_base

        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_video_path_creates_directory(self):
        """Test that get_video_path creates directory structure"""
        path = storage.get_video_path("user123", "cal456", 1)

        self.assertTrue(path.parent.exists(), "Video directory should be created")
        self.assertEqual(path.name, "1.mp4")
        self.assertIn("user123", str(path))
        self.assertIn("cal456", str(path))

    def test_get_video_path_naming_convention(self):
        """Test video file naming follows convention"""
        test_cases = [
            (1, "1.mp4"),
            (15, "15.mp4"),
            (31, "31.mp4")
        ]

        for day, expected_name in test_cases:
            with self.subTest(day=day):
                path = storage.get_video_path("user123", "cal456", day)
                self.assertEqual(path.name, expected_name)

    def test_get_video_path_invalid_day(self):
        """Test get_video_path rejects invalid day numbers"""
        invalid_days = [0, -1, 32, 100]

        for day in invalid_days:
            with self.subTest(day=day):
                with self.assertRaises(ValueError):
                    storage.get_video_path("user123", "cal456", day)

    def test_get_video_path_sanitization(self):
        """Test path sanitization prevents directory traversal"""
        malicious_inputs = [
            "../../../etc/passwd",
            "../../secret",
            "user/../admin",
            "user\\..\\admin"
        ]

        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                with self.assertRaises(ValueError):
                    storage.get_video_path(malicious_input, "cal456", 1)

    def test_get_thumbnail_path_creates_directory(self):
        """Test that get_thumbnail_path creates directory structure"""
        path = storage.get_thumbnail_path("user123", "cal456", 1)

        self.assertTrue(path.parent.exists(), "Thumbnail directory should be created")
        self.assertEqual(path.name, "1.jpg")
        self.assertIn("user123", str(path))
        self.assertIn("cal456", str(path))

    def test_get_thumbnail_path_naming_convention(self):
        """Test thumbnail file naming follows convention"""
        test_cases = [
            (1, "1.jpg"),
            (15, "15.jpg"),
            (31, "31.jpg")
        ]

        for day, expected_name in test_cases:
            with self.subTest(day=day):
                path = storage.get_thumbnail_path("user123", "cal456", day)
                self.assertEqual(path.name, expected_name)

    def test_multi_tenant_isolation(self):
        """Test that different users have isolated directories"""
        user1_path = storage.get_video_path("user1", "cal1", 1)
        user2_path = storage.get_video_path("user2", "cal2", 1)

        self.assertNotEqual(user1_path.parent, user2_path.parent)
        self.assertIn("user1", str(user1_path))
        self.assertIn("user2", str(user2_path))

    def test_delete_video_file_removes_both_files(self):
        """Test delete_video_file removes both video and thumbnail"""
        # Create dummy files
        video_path = storage.get_video_path("user123", "cal456", 5)
        thumbnail_path = storage.get_thumbnail_path("user123", "cal456", 5)

        video_path.touch()
        thumbnail_path.touch()

        # Verify files exist
        self.assertTrue(video_path.exists())
        self.assertTrue(thumbnail_path.exists())

        # Delete
        result = storage.delete_video_file("user123", "cal456", 5)

        # Verify deletion
        self.assertTrue(result)
        self.assertFalse(video_path.exists())
        self.assertFalse(thumbnail_path.exists())

    def test_delete_video_file_nonexistent(self):
        """Test delete_video_file handles nonexistent files gracefully"""
        result = storage.delete_video_file("user123", "cal456", 5)
        self.assertFalse(result)  # Should return False when nothing to delete

    def test_delete_calendar_files_removes_directory(self):
        """Test delete_calendar_files removes entire calendar directory"""
        # Create multiple video files
        for day in [1, 2, 3]:
            video_path = storage.get_video_path("user123", "cal456", day)
            thumbnail_path = storage.get_thumbnail_path("user123", "cal456", day)
            video_path.touch()
            thumbnail_path.touch()

        video_dir = storage.get_calendar_video_dir("user123", "cal456")
        thumbnail_dir = storage.get_calendar_thumbnail_dir("user123", "cal456")

        # Verify directories exist
        self.assertTrue(video_dir.exists())
        self.assertTrue(thumbnail_dir.exists())

        # Delete calendar
        result = storage.delete_calendar_files("user123", "cal456")

        # Verify deletion
        self.assertTrue(result)
        self.assertFalse(video_dir.exists())
        self.assertFalse(thumbnail_dir.exists())

    def test_delete_user_files_removes_all_calendars(self):
        """Test delete_user_files removes all user data (GDPR)"""
        # Create files for multiple calendars
        for cal_id in ["cal1", "cal2", "cal3"]:
            video_path = storage.get_video_path("user123", cal_id, 1)
            thumbnail_path = storage.get_thumbnail_path("user123", cal_id, 1)
            video_path.touch()
            thumbnail_path.touch()

        user_video_dir = storage.VIDEO_BASE_DIR / "user123"
        user_thumbnail_dir = storage.THUMBNAIL_BASE_DIR / "user123"

        # Verify user directories exist
        self.assertTrue(user_video_dir.exists())
        self.assertTrue(user_thumbnail_dir.exists())

        # Delete all user files
        result = storage.delete_user_files("user123")

        # Verify complete deletion
        self.assertTrue(result)
        self.assertFalse(user_video_dir.exists())
        self.assertFalse(user_thumbnail_dir.exists())

    def test_get_calendar_storage_size(self):
        """Test storage size calculation"""
        # Create test files with known sizes
        for day in [1, 2, 3]:
            video_path = storage.get_video_path("user123", "cal456", day)
            video_path.write_bytes(b"x" * 1000)  # 1000 bytes each

        size = storage.get_calendar_storage_size("user123", "cal456")
        self.assertEqual(size, 3000)  # 3 files * 1000 bytes

    def test_get_calendar_storage_size_empty(self):
        """Test storage size for calendar with no videos"""
        size = storage.get_calendar_storage_size("user123", "cal456")
        self.assertEqual(size, 0)

    def test_list_calendar_videos(self):
        """Test listing video day numbers"""
        # Create videos for specific days
        days = [1, 5, 10, 15]
        for day in days:
            video_path = storage.get_video_path("user123", "cal456", day)
            video_path.touch()

        result = storage.list_calendar_videos("user123", "cal456")

        self.assertEqual(sorted(result), sorted(days))
        self.assertIsInstance(result, list)

    def test_list_calendar_videos_empty(self):
        """Test listing videos for calendar with no videos"""
        result = storage.list_calendar_videos("user123", "cal456")
        self.assertEqual(result, [])

    def test_ensure_upload_directories(self):
        """Test that ensure_upload_directories creates base structure"""
        # Remove test directories
        if storage.VIDEO_BASE_DIR.exists():
            shutil.rmtree(storage.VIDEO_BASE_DIR)
        if storage.THUMBNAIL_BASE_DIR.exists():
            shutil.rmtree(storage.THUMBNAIL_BASE_DIR)

        # Call initialization
        storage.ensure_upload_directories()

        # Verify base directories created
        self.assertTrue(storage.VIDEO_BASE_DIR.exists())
        self.assertTrue(storage.THUMBNAIL_BASE_DIR.exists())


if __name__ == '__main__':
    unittest.main()
