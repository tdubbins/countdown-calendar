# Video Processing Service - Business Logic for Video Operations
import ffmpeg
import logging
import os
import time
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

# Configure logger (no timestamp - journalctl provides it)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[VIDEO-SVC] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_video_metadata(video_path: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Extract video metadata using ffprobe.

    Args:
        video_path: Path to the video file

    Returns:
        Tuple of (success, metadata_dict, error_message)
    """
    if not os.path.exists(video_path):
        return False, None, "Video file not found"

    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
            None
        )

        if not video_stream:
            return False, None, "No video stream found in file"

        metadata = {
            'duration': float(probe['format'].get('duration', 0)),
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'codec': video_stream.get('codec_name', 'unknown'),
            'size': int(probe['format'].get('size', 0))
        }

        return True, metadata, ""

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"FFprobe error for {video_path}: {error_msg}")
        return False, None, f"Failed to read video metadata: {error_msg}"

    except Exception as e:
        logger.error(f"Unexpected error reading metadata for {video_path}: {str(e)}")
        return False, None, f"Error reading video metadata: {str(e)}"

def compress_video(
    input_path: str,
    output_path: str,
    target_bitrate: str = '1000k',
    max_resolution: Tuple[int, int] = (1920, 1080)
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Compress video for web streaming using H.264 codec.

    Args:
        input_path: Path to original video file
        output_path: Path where compressed video will be saved
        target_bitrate: Target video bitrate (default: 1000k)
        max_resolution: Maximum resolution tuple (default: 1080p)

    Returns:
        Tuple of (success, compression_stats, error_message)
    """
    if not os.path.exists(input_path):
        return False, None, "Input video file not found"

    try:
        # Get original file size
        original_size = os.path.getsize(input_path)
        original_mb = round(original_size / (1024 * 1024), 2)
        logger.info(f"Compression starting | size={original_mb}MB | preset=fast")
        compress_start = time.time()

        # Set up input stream and check for audio
        input_stream = ffmpeg.input(input_path)
        probe = ffmpeg.probe(input_path)
        has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])

        # Apply video scaling filter (maintain aspect ratio)
        video = input_stream.video.filter('scale', max_resolution[0], max_resolution[1], force_original_aspect_ratio='decrease')

        if has_audio:
            audio = input_stream['a:0']  # Select first audio stream only
            stream = ffmpeg.output(
                video, audio, output_path,
                vcodec='libx264',
                video_bitrate=target_bitrate,
                maxrate='1500k',
                bufsize='2000k',
                acodec='aac',
                audio_bitrate='128k',
                preset='fast',
                movflags='faststart',
                map_metadata=-1
            )
        else:
            stream = ffmpeg.output(
                video, output_path,
                vcodec='libx264',
                video_bitrate=target_bitrate,
                maxrate='1500k',
                bufsize='2000k',
                preset='fast',
                movflags='faststart',
                map_metadata=-1
            )

        # Execute compression
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        compress_duration = time.time() - compress_start

        # Get compressed file size
        compressed_size = os.path.getsize(output_path)
        reduction_percent = ((original_size - compressed_size) / original_size) * 100
        compressed_mb = round(compressed_size / (1024 * 1024), 2)

        logger.info(f"Compression complete | time={compress_duration:.1f}s | {original_mb}MB → {compressed_mb}MB | reduction={round(reduction_percent, 1)}%")

        stats = {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'reduction_percent': round(reduction_percent, 2),
            'original_size_mb': round(original_size / (1024 * 1024), 2),
            'compressed_size_mb': round(compressed_size / (1024 * 1024), 2)
        }

        return True, stats, ""

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"FFmpeg compression error: {error_msg}")
        # Clean up partial output file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, None, f"Video compression failed: {error_msg}"

    except Exception as e:
        logger.error(f"Unexpected compression error: {str(e)}")
        # Clean up partial output file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, None, f"Error during video compression: {str(e)}"

def generate_thumbnail(
    video_path: str,
    thumbnail_path: str,
    time_offset: float = 0.0,
    width: int = 320
) -> Tuple[bool, str]:
    """
    Generate thumbnail image from video at specified time offset.

    Args:
        video_path: Path to video file
        thumbnail_path: Path where thumbnail will be saved
        time_offset: Time in seconds to extract frame (default: 0.0 = first frame)
        width: Thumbnail width in pixels (default: 320)

    Returns:
        Tuple of (success, error_message)
    """
    if not os.path.exists(video_path):
        return False, "Video file not found"

    try:
        logger.info(f"Thumbnail generation starting | width={width}px")
        thumb_start = time.time()

        # Extract frame at specified time and resize
        stream = ffmpeg.input(video_path, ss=time_offset)
        stream = ffmpeg.filter(stream, 'scale', width, -1)  # -1 maintains aspect ratio
        stream = ffmpeg.output(stream, thumbnail_path, vframes=1)

        # Execute thumbnail generation
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        thumb_duration = time.time() - thumb_start
        thumb_size = os.path.getsize(thumbnail_path) if os.path.exists(thumbnail_path) else 0
        thumb_kb = round(thumb_size / 1024, 1)
        logger.info(f"Thumbnail complete | time={thumb_duration:.2f}s | size={thumb_kb}KB")

        return True, ""

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"FFmpeg thumbnail error: {error_msg}")
        # Clean up partial thumbnail if it exists
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        return False, f"Thumbnail generation failed: {error_msg}"

    except Exception as e:
        logger.error(f"Unexpected thumbnail error: {str(e)}")
        # Clean up partial thumbnail if it exists
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        return False, f"Error generating thumbnail: {str(e)}"

def process_uploaded_video(
    original_path: str,
    compressed_path: str,
    thumbnail_path: str,
    delete_original: bool = True,
    on_thumbnail_ready: callable = None
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Complete video processing workflow: generate thumbnail first, then compress.

    Thumbnail is generated first from original video so frontend can display it
    quickly while compression continues in background.

    Args:
        original_path: Path to original uploaded video
        compressed_path: Path for compressed output video
        thumbnail_path: Path for thumbnail output image
        delete_original: Whether to delete original after compression (default: True)
        on_thumbnail_ready: Optional callback when thumbnail is ready

    Returns:
        Tuple of (success, processing_stats, error_message)
    """
    # Step 1: Generate thumbnail from original video (fast - allows early display)
    success, error = generate_thumbnail(original_path, thumbnail_path)
    if not success:
        return False, None, f"Thumbnail generation failed: {error}"

    # Notify that thumbnail is ready (for status updates)
    if on_thumbnail_ready:
        try:
            on_thumbnail_ready()
        except Exception as e:
            logger.warning(f"Thumbnail ready callback failed: {str(e)}")

    # Step 2: Compress video (slow)
    success, stats, error = compress_video(original_path, compressed_path)
    if not success:
        # Clean up thumbnail if compression fails
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        return False, None, error

    # Step 3: Delete original if requested and everything succeeded
    if delete_original and os.path.exists(original_path):
        try:
            os.remove(original_path)
        except Exception as e:
            logger.warning(f"Failed to delete original video: {str(e)}")
            # Not a critical error, continue

    # Add thumbnail confirmation to stats
    stats['thumbnail_generated'] = True

    return True, stats, ""
