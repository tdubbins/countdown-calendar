"""
Video and thumbnail storage utilities for per-calendar file management.

Storage Structure:
- Videos: /backend/data/calendars/{calendar_id}/videos/day_{day}.mp4
- Thumbnails: /backend/data/calendars/{calendar_id}/thumbnails/day_{day}_thumb.jpg
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

# Base directories (relative to backend root)
BACKEND_ROOT = Path(__file__).parent.parent.parent  # Go up from app/utils/ to backend/
CALENDARS_BASE_DIR = BACKEND_ROOT / "data" / "calendars"


def _sanitize_path_component(component: str) -> str:
    """Validate calendar_id is a valid UUID format"""
    if not component:
        raise ValueError("Path component cannot be empty")

    component = str(component).strip()

    try:
        uuid.UUID(component)
        return component
    except ValueError:
        raise ValueError(f"Invalid calendar ID format: {component}")


def _validate_path_containment(path: Path, base_dir: Path) -> Path:
    """Validate path stays within base directory"""
    resolved_base = base_dir.resolve()
    resolved_path = path.resolve()

    if not str(resolved_path).startswith(str(resolved_base) + os.sep) and resolved_path != resolved_base:
        raise ValueError("Path traversal detected")

    return resolved_path


def get_video_path(calendar_id: str, day: int) -> Path:
    """Get the file path for a video file"""
    calendar_id = _sanitize_path_component(calendar_id)

    if not 1 <= day <= 31:
        raise ValueError(f"Day must be between 1 and 31, got {day}")

    path = CALENDARS_BASE_DIR / calendar_id / "videos" / f"day_{day}.mp4"
    return _validate_path_containment(path, CALENDARS_BASE_DIR)


def get_thumbnail_path(calendar_id: str, day: int) -> Path:
    """Get the file path for a video thumbnail"""
    calendar_id = _sanitize_path_component(calendar_id)

    if not 1 <= day <= 31:
        raise ValueError(f"Day must be between 1 and 31, got {day}")

    path = CALENDARS_BASE_DIR / calendar_id / "thumbnails" / f"day_{day}_thumb.jpg"
    return _validate_path_containment(path, CALENDARS_BASE_DIR)


def get_calendar_video_dir(calendar_id: str) -> Path:
    """Get the directory containing all videos for a calendar"""
    calendar_id = _sanitize_path_component(calendar_id)
    path = CALENDARS_BASE_DIR / calendar_id / "videos"
    return _validate_path_containment(path, CALENDARS_BASE_DIR)


def get_calendar_thumbnail_dir(calendar_id: str) -> Path:
    """Get the directory containing all thumbnails for a calendar"""
    calendar_id = _sanitize_path_component(calendar_id)
    path = CALENDARS_BASE_DIR / calendar_id / "thumbnails"
    return _validate_path_containment(path, CALENDARS_BASE_DIR)


def delete_video_file(calendar_id: str, day: int) -> bool:
    """
    Delete a single video file and its thumbnail.

    Args:
        calendar_id: Calendar ID
        day: Day number to delete

    Returns:
        True if files were deleted, False if they didn't exist
    """
    deleted = False

    try:
        video_path = get_video_path(calendar_id, day)
        if video_path.exists():
            video_path.unlink()
            logger.info(f"Deleted video: {video_path}")
            deleted = True
    except Exception as e:
        logger.error(f"Error deleting video for day {day}: {e}")

    try:
        thumbnail_path = get_thumbnail_path(calendar_id, day)
        if thumbnail_path.exists():
            thumbnail_path.unlink()
            logger.info(f"Deleted thumbnail: {thumbnail_path}")
            deleted = True
    except Exception as e:
        logger.error(f"Error deleting thumbnail for day {day}: {e}")

    return deleted


def rename_video_files(calendar_id: str, source_day: int, target_day: int) -> Tuple[bool, str]:
    """
    Rename video and thumbnail files from one day to another.

    Used when moving a video to an empty day slot.

    Args:
        calendar_id: Calendar ID
        source_day: Day number to move from (1-31)
        target_day: Day number to move to (1-31)

    Returns:
        Tuple of (success, error_message)
    """
    try:
        source_video = get_video_path(calendar_id, source_day)
        target_video = get_video_path(calendar_id, target_day)
        source_thumb = get_thumbnail_path(calendar_id, source_day)
        target_thumb = get_thumbnail_path(calendar_id, target_day)

        # Validate source exists
        if not source_video.exists():
            return False, f"Source video for day {source_day} does not exist"

        # Validate target doesn't exist (use swap_video_files for that)
        if target_video.exists():
            return False, f"Target day {target_day} already has a video. Use swap instead."

        # Rename video file
        source_video.rename(target_video)
        logger.info(f"Renamed video: day_{source_day}.mp4 -> day_{target_day}.mp4")

        # Rename thumbnail if exists
        if source_thumb.exists():
            source_thumb.rename(target_thumb)
            logger.info(f"Renamed thumbnail: day_{source_day}_thumb.jpg -> day_{target_day}_thumb.jpg")

        return True, ""

    except Exception as e:
        logger.error(f"Error renaming video files from day {source_day} to {target_day}: {e}")
        return False, f"Failed to rename video files: {str(e)}"


def swap_video_files(calendar_id: str, day_a: int, day_b: int) -> Tuple[bool, str]:
    """
    Swap video and thumbnail files between two days.

    Uses a temporary file to avoid collision during swap.

    Args:
        calendar_id: Calendar ID
        day_a: First day number (1-31)
        day_b: Second day number (1-31)

    Returns:
        Tuple of (success, error_message)
    """
    try:
        video_a = get_video_path(calendar_id, day_a)
        video_b = get_video_path(calendar_id, day_b)
        thumb_a = get_thumbnail_path(calendar_id, day_a)
        thumb_b = get_thumbnail_path(calendar_id, day_b)

        # Validate both videos exist
        if not video_a.exists():
            return False, f"Video for day {day_a} does not exist"
        if not video_b.exists():
            return False, f"Video for day {day_b} does not exist"

        # Create temp paths in the same directory
        video_dir = get_calendar_video_dir(calendar_id)
        thumb_dir = get_calendar_thumbnail_dir(calendar_id)
        temp_video = video_dir / "day_temp_swap.mp4"
        temp_thumb = thumb_dir / "day_temp_swap_thumb.jpg"

        # Swap videos: A -> temp, B -> A, temp -> B
        video_a.rename(temp_video)
        video_b.rename(video_a)
        temp_video.rename(video_b)
        logger.info(f"Swapped videos: day_{day_a}.mp4 <-> day_{day_b}.mp4")

        # Swap thumbnails if both exist
        if thumb_a.exists() and thumb_b.exists():
            thumb_a.rename(temp_thumb)
            thumb_b.rename(thumb_a)
            temp_thumb.rename(thumb_b)
            logger.info(f"Swapped thumbnails: day_{day_a}_thumb.jpg <-> day_{day_b}_thumb.jpg")
        elif thumb_a.exists():
            # Only A has thumbnail, move to B
            thumb_a.rename(thumb_b)
            logger.info(f"Moved thumbnail from day {day_a} to day {day_b}")
        elif thumb_b.exists():
            # Only B has thumbnail, move to A
            thumb_b.rename(thumb_a)
            logger.info(f"Moved thumbnail from day {day_b} to day {day_a}")

        return True, ""

    except Exception as e:
        logger.error(f"Error swapping video files between day {day_a} and {day_b}: {e}")
        return False, f"Failed to swap video files: {str(e)}"


def delete_calendar_files(calendar_id: str) -> bool:
    """
    Delete all videos and thumbnails for a calendar.

    This is called when a calendar is deleted. Removes videos and thumbnails
    subdirectories.

    Args:
        calendar_id: Calendar ID to delete

    Returns:
        True if directories were deleted, False if they didn't exist
    """
    deleted = False

    try:
        video_dir = get_calendar_video_dir(calendar_id)
        if video_dir.exists():
            shutil.rmtree(video_dir)
            logger.info(f"Deleted calendar video directory: {video_dir}")
            deleted = True
    except Exception as e:
        logger.error(f"Error deleting calendar videos: {e}")

    try:
        thumbnail_dir = get_calendar_thumbnail_dir(calendar_id)
        if thumbnail_dir.exists():
            shutil.rmtree(thumbnail_dir)
            logger.info(f"Deleted calendar thumbnail directory: {thumbnail_dir}")
            deleted = True
    except Exception as e:
        logger.error(f"Error deleting calendar thumbnails: {e}")

    return deleted


def get_calendar_storage_size(calendar_id: str) -> int:
    """
    Calculate total storage size used by a calendar's videos.

    Args:
        calendar_id: Calendar ID

    Returns:
        Total size in bytes
    """
    total_size = 0

    try:
        video_dir = get_calendar_video_dir(calendar_id)
        if video_dir.exists():
            for video_file in video_dir.glob("day_*.mp4"):
                total_size += video_file.stat().st_size
    except Exception as e:
        logger.error(f"Error calculating storage size: {e}")

    return total_size


def list_calendar_videos(calendar_id: str) -> List[int]:
    """
    List all video day numbers for a calendar.

    Args:
        calendar_id: Calendar ID

    Returns:
        Sorted list of day numbers that have videos
    """
    days = []

    try:
        video_dir = get_calendar_video_dir(calendar_id)
        if video_dir.exists():
            for video_file in video_dir.glob("day_*.mp4"):
                try:
                    # Extract day number from filename like "day_1.mp4"
                    day_str = video_file.stem.replace("day_", "")
                    day = int(day_str)
                    days.append(day)
                except ValueError:
                    logger.warning(f"Invalid video filename: {video_file.name}")
    except Exception as e:
        logger.error(f"Error listing calendar videos: {e}")

    return sorted(days)


def get_user_total_storage(user_id: str) -> int:
    """
    Calculate total storage used by a user across all calendars.

    Args:
        user_id: User ID to calculate storage for

    Returns:
        Total size in bytes
    """
    total_size = 0

    try:
        from app.utils.json_db import get_user_calendar_ids

        calendar_ids = get_user_calendar_ids(user_id)

        for calendar_id in calendar_ids:
            total_size += get_calendar_storage_size(calendar_id)

    except Exception as e:
        logger.error(f"Error calculating user storage: {e}")

    return total_size


def check_storage_quota(user_id: str, additional_bytes: int, quota_bytes: int = 1_073_741_824) -> Tuple[bool, int, str]:
    """
    Check if user has enough storage quota for additional upload.

    Args:
        user_id: User ID to check quota for
        additional_bytes: Size of new upload in bytes
        quota_bytes: Maximum storage quota in bytes (default: 1GB)

    Returns:
        Tuple of (has_space, remaining_bytes, error_message)
    """
    try:
        current_usage = get_user_total_storage(user_id)
        new_total = current_usage + additional_bytes
        remaining = quota_bytes - new_total

        if new_total > quota_bytes:
            current_mb = current_usage / (1024 * 1024)
            quota_mb = quota_bytes / (1024 * 1024)
            additional_mb = additional_bytes / (1024 * 1024)

            error_msg = (
                f"Storage quota exceeded. Current usage: {current_mb:.1f}MB, "
                f"Upload size: {additional_mb:.1f}MB, "
                f"Quota: {quota_mb:.0f}MB"
            )
            return False, remaining, error_msg

        return True, remaining, ""

    except Exception as e:
        logger.error(f"Error checking storage quota: {e}")
        return False, 0, f"Error checking storage quota: {str(e)}"


def ensure_upload_directories() -> None:
    """
    Ensure base calendar directories exist.

    This should be called on application startup to create
    the required directory structure.
    """
    CALENDARS_BASE_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Calendar directories initialized")
