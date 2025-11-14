"""
Video and thumbnail storage utilities for per-calendar file management.

This module provides secure file path resolution, directory management,
and cleanup utilities for user-uploaded videos and generated thumbnails.

Storage Structure (NEW):
- Videos: /backend/data/calendars/{calendar_id}/videos/day_{day}.mp4
- Thumbnails: /backend/data/calendars/{calendar_id}/thumbnails/day_{day}_thumb.jpg

Security:
- Path validation to prevent directory traversal attacks
- Per-calendar isolation
- Atomic cleanup operations for GDPR compliance
"""

import os
import shutil
from pathlib import Path
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

# Base directories (relative to backend root)
BACKEND_ROOT = Path(__file__).parent.parent.parent  # Go up from app/utils/ to backend/
CALENDARS_BASE_DIR = BACKEND_ROOT / "data" / "calendars"


def _sanitize_path_component(component: str) -> str:
    """
    Sanitize a path component to prevent directory traversal attacks.

    Args:
        component: Path component to sanitize (calendar_id or day)

    Returns:
        Sanitized component safe for file system use

    Raises:
        ValueError: If component contains invalid characters
    """
    # Remove any path separators or parent directory references
    sanitized = str(component).replace("/", "").replace("\\", "").replace("..", "")

    if not sanitized or sanitized != str(component):
        raise ValueError(f"Invalid path component: {component}")

    return sanitized


def get_video_path(calendar_id: str, day: int) -> Path:
    """
    Get the file path for a video file.

    Args:
        calendar_id: Calendar ID
        day: Day number (1-31)

    Returns:
        Path object for the video file

    Raises:
        ValueError: If any parameter contains invalid characters
    """
    calendar_id = _sanitize_path_component(calendar_id)

    if not 1 <= day <= 31:
        raise ValueError(f"Day must be between 1 and 31, got {day}")

    return CALENDARS_BASE_DIR / calendar_id / "videos" / f"day_{day}.mp4"


def get_thumbnail_path(calendar_id: str, day: int) -> Path:
    """
    Get the file path for a video thumbnail.

    Args:
        calendar_id: Calendar ID
        day: Day number (1-31)

    Returns:
        Path object for the thumbnail file

    Raises:
        ValueError: If any parameter contains invalid characters
    """
    calendar_id = _sanitize_path_component(calendar_id)

    if not 1 <= day <= 31:
        raise ValueError(f"Day must be between 1 and 31, got {day}")

    return CALENDARS_BASE_DIR / calendar_id / "thumbnails" / f"day_{day}_thumb.jpg"


def get_calendar_video_dir(calendar_id: str) -> Path:
    """
    Get the directory containing all videos for a calendar.

    Args:
        calendar_id: Calendar ID

    Returns:
        Path object for the calendar's video directory
    """
    calendar_id = _sanitize_path_component(calendar_id)
    return CALENDARS_BASE_DIR / calendar_id / "videos"


def get_calendar_thumbnail_dir(calendar_id: str) -> Path:
    """
    Get the directory containing all thumbnails for a calendar.

    Args:
        calendar_id: Calendar ID

    Returns:
        Path object for the calendar's thumbnail directory
    """
    calendar_id = _sanitize_path_component(calendar_id)
    return CALENDARS_BASE_DIR / calendar_id / "thumbnails"


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

    Reads user's calendar_ids and sums storage for each calendar.

    NFR Compliance:
        - [SC2] Video storage: 1GB per user capacity check

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

    NFR Compliance:
        - [SC2] Video storage: 1GB (1,073,741,824 bytes) per user limit

    Args:
        user_id: User ID to check quota for
        additional_bytes: Size of new upload in bytes
        quota_bytes: Maximum storage quota in bytes (default: 1GB)

    Returns:
        Tuple of (has_space, remaining_bytes, error_message)
        - has_space: True if upload would fit within quota
        - remaining_bytes: Bytes remaining after this upload (negative if over quota)
        - error_message: Error message if quota exceeded, empty string otherwise
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
