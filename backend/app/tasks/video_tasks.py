# Video Compression Tasks - Background Video Processing
import os
import time
from typing import Tuple, Dict, Any
from pathlib import Path

from app.services.video_service import process_uploaded_video, get_video_metadata
from app.tasks.task_queue import TaskQueue, TaskStatus, TaskType
from app.utils.json_db import calendars_db


class VideoCompressionTask:
    """
    Video Compression Task Handler

    NFR Compliance:
        - [P2] Video compression processing <30 seconds per video
        - [R1] Compressed videos <50% of original size
        - [SC3] Modular architecture: Separate task execution logic
        - [RE1] Graceful error handling with retry logic

    This class handles the execution of video compression tasks.
    It coordinates between the task queue, video service, and calendar updates.
    """

    @staticmethod
    def execute(task_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute video compression task

        This is the main entry point called by the Worker.
        It orchestrates the complete video processing workflow:
        1. Mark task as processing
        2. Compress video and generate thumbnail
        3. Update calendar with video metadata
        4. Mark task as completed or failed

        Args:
            task_data: Task data from task queue containing:
                - task_id: Task identifier
                - user_id: User who owns the video
                - calendar_id: Calendar ID
                - day: Day number (1-31)
                - metadata: Contains file paths

        Returns:
            Tuple of (success, error_message)
        """
        task_id = task_data.get('task_id')
        user_id = task_data.get('user_id')
        calendar_id = task_data.get('calendar_id')
        day = task_data.get('day')
        metadata = task_data.get('metadata', {})

        try:
            # Step 1: Mark task as processing
            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=0)

            # Step 2: Get file paths from metadata
            original_path = metadata.get('original_path')
            compressed_path = metadata.get('compressed_path')
            thumbnail_path = metadata.get('thumbnail_path')

            if not all([original_path, compressed_path, thumbnail_path]):
                error_msg = "Missing required file paths in task metadata"
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            # Verify original file exists
            if not os.path.exists(original_path):
                error_msg = f"Original video file not found: {original_path}"
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            # Step 3: Update progress - starting compression
            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=20)

            # Step 4: Process video (compress + generate thumbnail)
            start_time = time.time()
            success, stats, error = process_uploaded_video(
                original_path=original_path,
                compressed_path=compressed_path,
                thumbnail_path=thumbnail_path,
                delete_original=True  # Delete original after successful compression
            )

            processing_time = time.time() - start_time

            if not success:
                error_msg = f"Video processing failed: {error}"
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            # Log compression stats (NFR [P2] and [R1] monitoring)
            print(f"Video compression completed in {processing_time:.2f}s")
            print(f"Original size: {stats['original_size_mb']}MB")
            print(f"Compressed size: {stats['compressed_size_mb']}MB")
            print(f"Size reduction: {stats['reduction_percent']}%")

            # Step 5: Update progress - compression complete
            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=80)

            # Step 6: Get video metadata for calendar update
            metadata_success, video_metadata, metadata_error = get_video_metadata(compressed_path)
            if not metadata_success:
                # Non-critical error - continue without metadata
                print(f"Warning: Could not extract video metadata: {metadata_error}")
                video_metadata = {}

            # Step 7: Update calendar with video information
            update_success, update_error = VideoCompressionTask._update_calendar_video(
                calendar_id=calendar_id,
                day=day,
                compressed_path=compressed_path,
                thumbnail_path=thumbnail_path,
                video_metadata=video_metadata,
                compression_stats=stats
            )

            if not update_success:
                error_msg = f"Failed to update calendar: {update_error}"
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            # Step 8: Mark task as completed
            TaskQueue.update_task_status(task_id, TaskStatus.COMPLETED, progress=100)

            return True, ""

        except Exception as e:
            error_msg = f"Unexpected error during video processing: {str(e)}"
            print(f"Video compression task error: {error_msg}")
            TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
            return False, error_msg

    @staticmethod
    def _update_calendar_video(
        calendar_id: str,
        day: int,
        compressed_path: str,
        thumbnail_path: str,
        video_metadata: Dict[str, Any],
        compression_stats: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Update calendar with video information

        This updates the calendar's videos object and videoCount.
        NFR Compliance: [SC3] Modular architecture

        Args:
            calendar_id: Calendar ID to update
            day: Day number (1-31)
            compressed_path: Path to compressed video file
            thumbnail_path: Path to thumbnail image
            video_metadata: Video metadata (duration, size, etc.)
            compression_stats: Compression statistics

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get calendar
            calendar = calendars_db.find_by_id('calendars', calendar_id)
            if not calendar:
                return False, "Calendar not found"

            # Prepare video data for calendar
            video_info = {
                'filename': os.path.basename(compressed_path),
                'thumbnail': os.path.basename(thumbnail_path),
                'size': compression_stats.get('compressed_size', 0),
                'duration': video_metadata.get('duration', 0),
                'uploaded_at': calendar.get('updatedAt'),  # Use calendar's updatedAt timestamp
                'status': 'completed'
            }

            # Update calendar videos object
            videos = calendar.get('videos', {})
            videos[str(day)] = video_info

            # Count total videos
            video_count = len(videos)

            # Calculate total storage used
            total_storage = sum(
                video.get('size', 0) for video in videos.values()
            )

            # Update calendar
            updates = {
                'videos': videos,
                'videoCount': video_count,
                'videoStorageUsed': total_storage
            }

            calendars_db.update('calendars', calendar_id, updates)

            return True, ""

        except Exception as e:
            error_msg = f"Calendar update error: {str(e)}"
            print(error_msg)
            return False, error_msg

    @staticmethod
    def create_video_task(
        user_id: str,
        calendar_id: str,
        day: int,
        original_path: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Create a new video compression task

        This is a convenience method called by the upload endpoint.
        It generates file paths and creates the task.

        Args:
            user_id: User ID who owns the video
            calendar_id: Calendar ID
            day: Day number (1-31)
            original_path: Path to original uploaded video file

        Returns:
            Tuple of (success, task_id, error_message)
        """
        try:
            # Generate paths for compressed video and thumbnail
            compressed_path = f"uploads/videos/{user_id}/{calendar_id}/{day}.mp4"
            thumbnail_path = f"uploads/thumbnails/{user_id}/{calendar_id}/{day}.jpg"

            # Ensure directories exist
            os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

            # Create task metadata
            metadata = {
                'original_path': original_path,
                'compressed_path': compressed_path,
                'thumbnail_path': thumbnail_path
            }

            # Create task in queue
            success, task_id, error = TaskQueue.create_task(
                task_type=TaskType.VIDEO_COMPRESSION,
                user_id=user_id,
                calendar_id=calendar_id,
                day=day,
                metadata=metadata
            )

            if not success:
                return False, None, error

            return True, task_id, ""

        except Exception as e:
            error_msg = f"Failed to create video task: {str(e)}"
            print(error_msg)
            return False, None, error_msg
