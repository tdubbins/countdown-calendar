"""
Unit tests for video processing service
Tests video compression, thumbnail generation, and metadata extraction
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services import video_service


class TestVideoService(unittest.TestCase):
    """Test suite for video service functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_video_metadata_file_not_found(self):
        """Test get_video_metadata with nonexistent file"""
        success, metadata, error = video_service.get_video_metadata("/nonexistent/video.mp4")

        self.assertFalse(success)
        self.assertIsNone(metadata)
        self.assertEqual(error, "Video file not found")

    def test_compress_video_input_not_found(self):
        """Test compress_video with nonexistent input file"""
        output_path = os.path.join(self.test_dir, "output.mp4")

        success, stats, error = video_service.compress_video(
            "/nonexistent/input.mp4",
            output_path
        )

        self.assertFalse(success)
        self.assertIsNone(stats)
        self.assertEqual(error, "Input video file not found")

    def test_compress_video_creates_no_partial_files_on_error(self):
        """Test that compress_video cleans up partial files on error"""
        # Create an invalid input file (not a real video)
        input_path = os.path.join(self.test_dir, "fake_input.mp4")
        output_path = os.path.join(self.test_dir, "output.mp4")

        with open(input_path, 'w') as f:
            f.write("not a video")

        success, stats, error = video_service.compress_video(input_path, output_path)

        # Should fail (not a real video)
        self.assertFalse(success)
        self.assertIsNone(stats)
        self.assertNotEqual(error, "")

        # Output file should NOT exist (cleaned up)
        self.assertFalse(os.path.exists(output_path), "Partial output file should be cleaned up")

    def test_generate_thumbnail_video_not_found(self):
        """Test generate_thumbnail with nonexistent video"""
        thumbnail_path = os.path.join(self.test_dir, "thumb.jpg")

        success, error = video_service.generate_thumbnail(
            "/nonexistent/video.mp4",
            thumbnail_path
        )

        self.assertFalse(success)
        self.assertEqual(error, "Video file not found")

    def test_generate_thumbnail_creates_no_partial_files_on_error(self):
        """Test that generate_thumbnail cleans up partial files on error"""
        # Create an invalid video file
        video_path = os.path.join(self.test_dir, "fake_video.mp4")
        thumbnail_path = os.path.join(self.test_dir, "thumb.jpg")

        with open(video_path, 'w') as f:
            f.write("not a video")

        success, error = video_service.generate_thumbnail(video_path, thumbnail_path)

        # Should fail (not a real video)
        self.assertFalse(success)
        self.assertNotEqual(error, "")

        # Thumbnail file should NOT exist (cleaned up)
        self.assertFalse(os.path.exists(thumbnail_path), "Partial thumbnail should be cleaned up")

    def test_process_uploaded_video_input_not_found(self):
        """Test process_uploaded_video with nonexistent input"""
        original_path = "/nonexistent/original.mp4"
        compressed_path = os.path.join(self.test_dir, "compressed.mp4")
        thumbnail_path = os.path.join(self.test_dir, "thumb.jpg")

        success, stats, error = video_service.process_uploaded_video(
            original_path,
            compressed_path,
            thumbnail_path,
            delete_original=False
        )

        self.assertFalse(success)
        self.assertIsNone(stats)
        self.assertIn("not found", error.lower())

    def test_process_uploaded_video_cleanup_on_thumbnail_failure(self):
        """Test that process_uploaded_video cleans up compressed video if thumbnail fails"""
        # Create fake original file
        original_path = os.path.join(self.test_dir, "original.mp4")
        compressed_path = os.path.join(self.test_dir, "compressed.mp4")
        thumbnail_path = os.path.join(self.test_dir, "thumb.jpg")

        with open(original_path, 'w') as f:
            f.write("not a video")

        success, stats, error = video_service.process_uploaded_video(
            original_path,
            compressed_path,
            thumbnail_path,
            delete_original=False
        )

        # Should fail
        self.assertFalse(success)
        self.assertIsNone(stats)

        # Neither compressed video nor thumbnail should exist
        self.assertFalse(os.path.exists(compressed_path), "Compressed video should be cleaned up")
        self.assertFalse(os.path.exists(thumbnail_path), "Thumbnail should not exist")

        # Original should still exist (delete_original=False)
        self.assertTrue(os.path.exists(original_path), "Original should not be deleted on failure")

    def test_compress_video_return_value_structure(self):
        """Test that compress_video returns correct tuple structure"""
        # Even with invalid input, should return proper tuple structure
        success, stats, error = video_service.compress_video(
            "/nonexistent/input.mp4",
            "/nonexistent/output.mp4"
        )

        # Check tuple structure
        self.assertIsInstance(success, bool)
        self.assertTrue(stats is None or isinstance(stats, dict))
        self.assertIsInstance(error, str)

    def test_generate_thumbnail_return_value_structure(self):
        """Test that generate_thumbnail returns correct tuple structure"""
        success, error = video_service.generate_thumbnail(
            "/nonexistent/video.mp4",
            "/nonexistent/thumb.jpg"
        )

        # Check tuple structure
        self.assertIsInstance(success, bool)
        self.assertIsInstance(error, str)

    def test_get_video_metadata_return_value_structure(self):
        """Test that get_video_metadata returns correct tuple structure"""
        success, metadata, error = video_service.get_video_metadata("/nonexistent/video.mp4")

        # Check tuple structure
        self.assertIsInstance(success, bool)
        self.assertTrue(metadata is None or isinstance(metadata, dict))
        self.assertIsInstance(error, str)

    def test_process_uploaded_video_return_value_structure(self):
        """Test that process_uploaded_video returns correct tuple structure"""
        success, stats, error = video_service.process_uploaded_video(
            "/nonexistent/original.mp4",
            "/nonexistent/compressed.mp4",
            "/nonexistent/thumb.jpg"
        )

        # Check tuple structure
        self.assertIsInstance(success, bool)
        self.assertTrue(stats is None or isinstance(stats, dict))
        self.assertIsInstance(error, str)


if __name__ == '__main__':
    unittest.main()
