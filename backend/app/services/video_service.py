# Video Processing Service - Business Logic for Video Operations
import ffmpeg
import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

def get_video_metadata(video_path: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Extract video metadata using ffprobe

    NFR Compliance:
        - [P2] Fast metadata extraction: <2 seconds per video
        - [SC3] Modular architecture: Separate video processing service

    Args:
        video_path: Path to the video file

    Returns:
        Tuple of (success, metadata_dict, error_message)
        metadata_dict contains: duration, width, height, codec, size
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
        print(f"FFprobe error for {video_path}: {error_msg}")
        return False, None, f"Failed to read video metadata: {error_msg}"

    except Exception as e:
        print(f"Unexpected error reading metadata for {video_path}: {str(e)}")
        return False, None, f"Error reading video metadata: {str(e)}"

def compress_video(
    input_path: str,
    output_path: str,
    target_bitrate: str = '1000k',
    max_resolution: Tuple[int, int] = (1920, 1080)
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Compress video for web streaming using H.264 codec

    NFR Compliance:
        - [P2] Video compression: <30 seconds per video
        - [R1] Compressed videos <50% of original size while maintaining quality
        - [SC3] Modular architecture: Service layer separation

    Args:
        input_path: Path to original video file
        output_path: Path where compressed video will be saved
        target_bitrate: Target video bitrate (default: 1000k for web streaming)
        max_resolution: Maximum resolution as (width, height) tuple (default: 1080p)

    Returns:
        Tuple of (success, compression_stats, error_message)
        compression_stats contains: original_size, compressed_size, reduction_percent
    """
    if not os.path.exists(input_path):
        return False, None, "Input video file not found"

    try:
        # Get original file size
        original_size = os.path.getsize(input_path)

        # Compress video with H.264 and optimize for web streaming
        stream = ffmpeg.input(input_path)

        # Scale if resolution exceeds maximum (maintain aspect ratio)
        stream = ffmpeg.filter(stream, 'scale', max_resolution[0], max_resolution[1], force_original_aspect_ratio='decrease')

        # Output with optimized settings
        stream = ffmpeg.output(
            stream,
            output_path,
            vcodec='libx264',              # H.264 codec for wide compatibility
            video_bitrate=target_bitrate,  # Target bitrate
            maxrate='1500k',               # Maximum bitrate
            bufsize='2000k',               # Buffer size
            acodec='aac',                  # AAC audio codec
            audio_bitrate='128k',          # Audio bitrate
            preset='medium',               # Encoding speed/compression tradeoff
            movflags='faststart'           # Enable progressive download for web
        )

        # Execute compression
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        # Get compressed file size
        compressed_size = os.path.getsize(output_path)
        reduction_percent = ((original_size - compressed_size) / original_size) * 100

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
        print(f"FFmpeg compression error: {error_msg}")
        # Clean up partial output file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, None, f"Video compression failed: {error_msg}"

    except Exception as e:
        print(f"Unexpected compression error: {str(e)}")
        # Clean up partial output file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, None, f"Error during video compression: {str(e)}"

def generate_thumbnail(
    video_path: str,
    thumbnail_path: str,
    time_offset: float = 1.0,
    width: int = 320
) -> Tuple[bool, str]:
    """
    Generate thumbnail image from video at specified time offset

    NFR Compliance:
        - [P2] Fast thumbnail generation: <2 seconds
        - [SC3] Modular architecture: Separate thumbnail generation

    Args:
        video_path: Path to video file
        thumbnail_path: Path where thumbnail will be saved
        time_offset: Time in seconds to extract frame (default: 1.0 second)
        width: Thumbnail width in pixels (default: 320px, height auto-calculated)

    Returns:
        Tuple of (success, error_message)
    """
    if not os.path.exists(video_path):
        return False, "Video file not found"

    try:
        # Extract frame at specified time and resize
        stream = ffmpeg.input(video_path, ss=time_offset)
        stream = ffmpeg.filter(stream, 'scale', width, -1)  # -1 maintains aspect ratio
        stream = ffmpeg.output(stream, thumbnail_path, vframes=1)

        # Execute thumbnail generation
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return True, ""

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"FFmpeg thumbnail error: {error_msg}")
        # Clean up partial thumbnail if it exists
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        return False, f"Thumbnail generation failed: {error_msg}"

    except Exception as e:
        print(f"Unexpected thumbnail error: {str(e)}")
        # Clean up partial thumbnail if it exists
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        return False, f"Error generating thumbnail: {str(e)}"

def process_uploaded_video(
    original_path: str,
    compressed_path: str,
    thumbnail_path: str,
    delete_original: bool = True
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Complete video processing workflow: compress video and generate thumbnail

    This is a convenience function that combines compression and thumbnail generation
    into a single atomic operation.

    NFR Compliance:
        - [P2] Complete processing: <35 seconds per video
        - [R1] Achieve <50% size reduction
        - [SC3] Service layer orchestration

    Args:
        original_path: Path to original uploaded video
        compressed_path: Path for compressed output video
        thumbnail_path: Path for thumbnail output image
        delete_original: Whether to delete original after successful compression (default: True)

    Returns:
        Tuple of (success, processing_stats, error_message)
        processing_stats contains compression stats plus thumbnail confirmation
    """
    # Step 1: Compress video
    success, stats, error = compress_video(original_path, compressed_path)
    if not success:
        return False, None, error

    # Step 2: Generate thumbnail from compressed video
    success, error = generate_thumbnail(compressed_path, thumbnail_path)
    if not success:
        # Clean up compressed video if thumbnail generation fails
        if os.path.exists(compressed_path):
            os.remove(compressed_path)
        return False, None, error

    # Step 3: Delete original if requested and everything succeeded
    if delete_original and os.path.exists(original_path):
        try:
            os.remove(original_path)
        except Exception as e:
            print(f"Failed to delete original video {original_path}: {str(e)}")
            # Not a critical error, continue

    # Add thumbnail confirmation to stats
    stats['thumbnail_generated'] = True

    return True, stats, ""
