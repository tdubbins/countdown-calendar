# Video Compression Tasks - Background Video Processing
import os
import time
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

from app.services.video_service import process_uploaded_video, get_video_metadata
from app.tasks.task_queue import TaskQueue, TaskStatus, TaskType
from app.utils.json_db import calendars_db


class VideoCompressionTask:
    """
    Video Compression Task Handler.

    Handles execution of video compression tasks, coordinating between
    the task queue, video service, and calendar updates.
    """

    @staticmethod
    def execute(task_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute video compression task.

        Args:
            task_data: Task data containing task_id, user_id, calendar_id, day, and metadata

        Returns:
            Tuple of (success, error_message)
        """
        task_id = task_data.get('task_id')
        user_id = task_data.get('user_id')
        calendar_id = task_data.get('calendar_id')
        day = task_data.get('day')
        metadata = task_data.get('metadata', {})
        original_path = metadata.get('original_path')  # For cleanup in except block

        try:
            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=0)
            compressed_path = metadata.get('compressed_path')
            thumbnail_path = metadata.get('thumbnail_path')

            if not all([original_path, compressed_path, thumbnail_path]):
                error_msg = "Missing required file paths in task metadata"
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            if not os.path.exists(original_path):
                error_msg = f"Original video file not found: {original_path}"
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=20)

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
                # Clean up temp file on failure
                if os.path.exists(original_path):
                    try:
                        os.remove(original_path)
                        print(f"Cleaned up temp file: {original_path}")
                    except Exception as cleanup_error:
                        print(f"Failed to clean up temp file: {cleanup_error}")
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            print(f"Video compression completed in {processing_time:.2f}s")
            print(f"Original size: {stats['original_size_mb']}MB")
            print(f"Compressed size: {stats['compressed_size_mb']}MB")
            print(f"Size reduction: {stats['reduction_percent']}%")

            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=80)

            metadata_success, video_metadata, metadata_error = get_video_metadata(compressed_path)
            if not metadata_success:
                print(f"Warning: Could not extract video metadata: {metadata_error}")
                video_metadata = {}

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

            TaskQueue.update_task_status(task_id, TaskStatus.COMPLETED, progress=100)

            return True, ""

        except Exception as e:
            error_msg = f"Unexpected error during video processing: {str(e)}"
            print(f"Video compression task error: {error_msg}")
            # Clean up temp file on unexpected error
            if original_path and os.path.exists(original_path):
                try:
                    os.remove(original_path)
                    print(f"Cleaned up temp file: {original_path}")
                except Exception:
                    pass
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
        Update calendar with video information.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get calendar metadata from distributed structure
            calendar = calendars_db.read_calendar_meta(calendar_id)
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

            # Update calendar metadata in distributed structure
            updates = {
                'videos': videos,
                'videoCount': video_count,
                'videoStorageUsed': total_storage
            }

            calendars_db.update_calendar_meta(calendar_id, updates)

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
            # Generate paths using storage utilities (distributed calendar structure)
            from app.utils.storage import get_video_path, get_thumbnail_path

            compressed_path = str(get_video_path(calendar_id, day))
            thumbnail_path = str(get_thumbnail_path(calendar_id, day))

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
