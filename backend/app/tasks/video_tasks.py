# Video Compression Tasks - Background Video Processing
import logging
import os
import time
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

from app.services.video_service import process_uploaded_video, get_video_metadata
from app.tasks.task_queue import TaskQueue, TaskStatus, TaskType
from app.utils.json_db import calendars_db

# Configure logger (no timestamp - journalctl provides it)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent duplicate logs from root logger

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[VIDEO] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


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
        thumbnail_already_generated = metadata.get('thumbnail_already_generated', False)

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

            # If thumbnail already generated at upload, start progress higher
            initial_progress = 10 if thumbnail_already_generated else 5
            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=initial_progress)

            # Callback when thumbnail is ready (before compression starts)
            # Only used if thumbnail wasn't already generated at upload
            def on_thumbnail_ready():
                logger.info(f"Thumbnail ready for calendar={calendar_id[:8]}... day={day}")
                TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=10)
                # Update calendar with thumbnail info so frontend can fetch it early
                VideoCompressionTask._update_calendar_thumbnail(
                    calendar_id=calendar_id,
                    day=day,
                    thumbnail_path=thumbnail_path
                )

            start_time = time.time()
            success, stats, error = process_uploaded_video(
                original_path=original_path,
                compressed_path=compressed_path,
                thumbnail_path=thumbnail_path,
                delete_original=True,
                on_thumbnail_ready=on_thumbnail_ready if not thumbnail_already_generated else None,
                skip_thumbnail=thumbnail_already_generated
            )

            processing_time = time.time() - start_time

            if not success:
                error_msg = f"Video processing failed: {error}"
                # Clean up temp file on failure
                if os.path.exists(original_path):
                    try:
                        os.remove(original_path)
                        logger.info(f"Cleaned up temp file: {original_path}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to clean up temp file: {cleanup_error}")
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
                return False, error_msg

            logger.info(f"Compression done | time={processing_time:.2f}s | original={stats['original_size_mb']}MB | compressed={stats['compressed_size_mb']}MB | reduction={stats['reduction_percent']}%")

            TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=80)

            metadata_success, video_metadata, metadata_error = get_video_metadata(compressed_path)
            if not metadata_success:
                logger.warning(f"Could not extract video metadata: {metadata_error}")
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
            logger.error(f"Video compression task error: {error_msg}")
            # Clean up temp file on unexpected error
            if original_path and os.path.exists(original_path):
                try:
                    os.remove(original_path)
                    logger.info(f"Cleaned up temp file: {original_path}")
                except Exception:
                    pass
            TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
            return False, error_msg

    @staticmethod
    def _update_calendar_thumbnail(
        calendar_id: str,
        day: int,
        thumbnail_path: str
    ) -> Tuple[bool, str]:
        """
        Update calendar with thumbnail info (called early, before compression).
        Sets status to 'processing' so frontend knows thumbnail is available.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            calendar = calendars_db.read_calendar_meta(calendar_id)
            if not calendar:
                return False, "Calendar not found"

            # Set minimal video info with thumbnail and processing status
            video_info = {
                'thumbnail': os.path.basename(thumbnail_path),
                'status': 'processing'  # Indicates thumbnail ready, compression ongoing
            }

            videos = calendar.get('videos', {})
            videos[str(day)] = video_info

            calendars_db.update_calendar_meta(calendar_id, {'videos': videos})

            return True, ""

        except Exception as e:
            logger.error(f"Calendar thumbnail update error: {str(e)}")
            return False, str(e)

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
        Update calendar with full video information (called after compression).

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get calendar metadata from distributed structure
            calendar = calendars_db.read_calendar_meta(calendar_id)
            if not calendar:
                return False, "Calendar not found"

            # Prepare full video data for calendar
            video_info = {
                'filename': os.path.basename(compressed_path),
                'thumbnail': os.path.basename(thumbnail_path),
                'size': compression_stats.get('compressed_size', 0),
                'duration': video_metadata.get('duration', 0),
                'uploaded_at': calendar.get('updatedAt'),
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
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def create_video_task(
        user_id: str,
        calendar_id: str,
        day: int,
        original_path: str,
        thumbnail_already_generated: bool = False
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
            thumbnail_already_generated: If True, skip thumbnail generation (already done at upload)

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
                'thumbnail_path': thumbnail_path,
                'thumbnail_already_generated': thumbnail_already_generated
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
            logger.error(error_msg)
            return False, None, error_msg
