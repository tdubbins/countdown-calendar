"""
Unit tests for video validation functions
Tests video file type, size, day number, and duration validation
"""

import unittest
import sys
import os
import tempfile

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.utils import validators


class TestVideoValidators(unittest.TestCase):
    """Test suite for video validation functions"""

    def test_validate_video_file_type_valid(self):
        """Test valid video file extensions"""
        valid_files = [
            "video.mp4",
            "movie.mov",
            "clip.avi",
            "recording.webm",
            "VIDEO.MP4",  # Test case insensitivity
            "my.video.file.mp4"  # Multiple dots
        ]

        for filename in valid_files:
            with self.subTest(filename=filename):
                valid, error = validators.validate_video_file_type(filename)
                self.assertTrue(valid, f"{filename} should be valid but got: {error}")
                self.assertEqual(error, "")

    def test_validate_video_file_type_invalid(self):
        """Test invalid video file extensions"""
        invalid_files = [
            "document.pdf",
            "image.jpg",
            "audio.mp3",
            "archive.zip",
            "video.mkv",  # Not in allowed list
            "file.txt"
        ]

        for filename in invalid_files:
            with self.subTest(filename=filename):
                valid, error = validators.validate_video_file_type(filename)
                self.assertFalse(valid)
                self.assertIn("Invalid file type", error)
                self.assertNotEqual(error, "")

    def test_validate_video_file_type_empty(self):
        """Test empty filename"""
        valid, error = validators.validate_video_file_type("")
        self.assertFalse(valid)
        self.assertEqual(error, "Filename is required")

    def test_validate_video_file_size_valid(self):
        """Test valid video file sizes"""
        valid_sizes = [
            (1024, True),  # 1 KB
            (1024 * 1024, True),  # 1 MB
            (10 * 1024 * 1024, True),  # 10 MB
            (50 * 1024 * 1024, True),  # 50 MB (max)
            (49 * 1024 * 1024, True)  # Just under max
        ]

        for size, expected_valid in valid_sizes:
            with self.subTest(size=size):
                valid, error = validators.validate_video_file_size(size)
                self.assertEqual(valid, expected_valid)
                if expected_valid:
                    self.assertEqual(error, "")

    def test_validate_video_file_size_too_large(self):
        """Test file size exceeds maximum (1GB limit)"""
        invalid_sizes = [
            1025 * 1024 * 1024,  # 1025 MB (1.001GB)
            2 * 1024 * 1024 * 1024,  # 2 GB
            5 * 1024 * 1024 * 1024  # 5 GB
        ]

        for size in invalid_sizes:
            with self.subTest(size=size):
                valid, error = validators.validate_video_file_size(size)
                self.assertFalse(valid)
                self.assertIn("exceeds maximum", error)
                self.assertIn("1024MB", error)  # Updated to 1GB limit

    def test_validate_video_file_size_zero_or_negative(self):
        """Test zero or negative file sizes"""
        invalid_sizes = [0, -1, -1000]

        for size in invalid_sizes:
            with self.subTest(size=size):
                valid, error = validators.validate_video_file_size(size)
                self.assertFalse(valid)
                self.assertIn("greater than 0", error)

    def test_validate_video_day_number_valid(self):
        """Test valid day numbers within calendar duration"""
        test_cases = [
            (1, 10, True),  # Day 1 of 10-day calendar
            (5, 10, True),  # Day 5 of 10-day calendar
            (10, 10, True),  # Last day
            (1, 31, True),  # Day 1 of max duration
            (31, 31, True)  # Day 31 of max duration
        ]

        for day, duration, expected_valid in test_cases:
            with self.subTest(day=day, duration=duration):
                valid, error = validators.validate_video_day_number(day, duration)
                self.assertEqual(valid, expected_valid)
                if expected_valid:
                    self.assertEqual(error, "")

    def test_validate_video_day_number_exceeds_duration(self):
        """Test day number exceeds calendar duration"""
        test_cases = [
            (11, 10),  # Day 11 of 10-day calendar
            (32, 31),  # Day 32 of 31-day calendar
            (100, 10)  # Way over
        ]

        for day, duration in test_cases:
            with self.subTest(day=day, duration=duration):
                valid, error = validators.validate_video_day_number(day, duration)
                self.assertFalse(valid)
                self.assertIn("exceeds", error)
                self.assertIn(str(day), error)

    def test_validate_video_day_number_invalid(self):
        """Test invalid day numbers (zero or negative)"""
        invalid_days = [0, -1, -10]

        for day in invalid_days:
            with self.subTest(day=day):
                valid, error = validators.validate_video_day_number(day, 10)
                self.assertFalse(valid)
                self.assertIn("at least 1", error)

    def test_validate_video_duration_file_not_found(self):
        """Test validation with nonexistent file"""
        valid, duration, error = validators.validate_video_duration("/nonexistent/video.mp4")
        self.assertFalse(valid)
        self.assertIsNone(duration)
        self.assertIn("not found", error)

    def test_validate_video_duration_ffprobe_not_installed(self):
        """Test graceful handling when FFprobe not installed"""
        # Create a temporary empty file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # This will likely fail because the file isn't a valid video,
            # OR it will succeed if FFprobe isn't installed (returns True, None, "")
            valid, duration, error = validators.validate_video_duration(tmp_path)

            # Either it's valid (FFprobe not installed) or invalid (file not valid video)
            # Both are acceptable outcomes
            if valid:
                # FFprobe not installed - should return (True, None, "")
                self.assertIsNone(duration)
                self.assertEqual(error, "")
            else:
                # FFprobe installed but file invalid
                self.assertIn("metadata", error.lower())

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == '__main__':
    unittest.main()
