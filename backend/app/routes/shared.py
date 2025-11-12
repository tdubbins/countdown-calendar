# Public Shared Calendar Routes
"""
Public API endpoints for viewing shared calendars without authentication.

These endpoints enable public access to calendars via their unique share tokens.
No authentication is required, but endpoints will have rate limiting added in Issue #77.

NFR Compliance:
    - [S4] Input Validation: All inputs validated before processing
    - [SC3] RESTful API Design: Follows REST conventions for public resources
    - [P3] Performance: Optimized for <3 second calendar rendering
    - Privacy: Does not expose user information or sensitive data

Endpoints:
    - GET /api/shared/<share_token> - Get calendar data with unlock status
    - GET /api/shared/<share_token>/day/<day_number> - Get day's video (if unlocked)
    - GET /api/shared/<share_token>/day/<day_number>/thumbnail - Get day's thumbnail
    - GET /api/shared/<share_token>/day/<day_number>/stream - Stream video file
"""

from flask import Blueprint, request, jsonify, send_file

from app.services.calendar_service import get_calendar_by_share_token, get_shared_calendar_data
from app.utils.unlock_logic import is_day_unlocked
from app.utils.storage import get_video_path, get_thumbnail_path

shared_bp = Blueprint('shared', __name__)


@shared_bp.route('/shared/<share_token>', methods=['GET'])
def get_shared_calendar(share_token):
    """
    Get shared calendar data with unlock status for all days (public access)

    This is the main endpoint for viewing shared calendars. It returns calendar
    metadata and unlock status for all days, allowing the frontend to render
    the door grid appropriately.

    NFR Compliance:
        - [P3] Performance: <3 second response time for calendar data
        - [S4] Input Validation: Share token format validated
        - [SC3] RESTful Design: Public GET endpoint, idempotent
        - Privacy: No user data exposed

    URL: GET /api/shared/<share_token>

    Query Parameters: None

    Response 200:
        {
            "success": true,
            "calendar": {
                "title": "My Advent Calendar",
                "duration": 24,
                "doorOrder": "random",
                "doorPositions": [3, 1, 24, ...],
                "theme": "christmas",
                "days": [
                    {
                        "dayNumber": 1,
                        "isUnlocked": true,
                        "thumbnailUrl": "/api/shared/<token>/day/1/thumbnail"
                    },
                    {
                        "dayNumber": 2,
                        "isUnlocked": false,
                        "thumbnailUrl": null
                    },
                    ...
                ]
            }
        }

    Response 404: Calendar not found or no longer shared
    Response 500: Internal server error

    Rate Limiting: Will be added in Issue #77
        - 20 requests/minute per IP
    """
    try:
        # Get formatted shared calendar data using service layer
        success, calendar_data, error_message = get_shared_calendar_data(share_token)

        if not success:
            # Determine appropriate status code
            if "not found" in error_message.lower():
                status_code = 404
            else:
                status_code = 500

            return jsonify({
                'error': error_message
            }), status_code

        # Return success response with calendar data
        return jsonify({
            'success': True,
            'calendar': calendar_data
        }), 200

    except Exception as e:
        print(f"Get shared calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@shared_bp.route('/shared/<share_token>/day/<int:day_number>', methods=['GET'])
def get_shared_day(share_token, day_number):
    """
    Get video metadata for a specific day (public access, requires unlock)

    This endpoint returns video information for a specific day, including
    URLs for streaming the video and thumbnail. It checks unlock status
    before returning data.

    NFR Compliance:
        - [S4] Input Validation: Token and day number validated
        - [SC3] RESTful Design: Public GET endpoint for sub-resource
        - Privacy: Only returns data if day is unlocked

    URL: GET /api/shared/<share_token>/day/<day_number>

    Response 200:
        {
            "success": true,
            "dayNumber": 1,
            "isUnlocked": true,
            "videoUrl": "/api/shared/<token>/day/1/stream",
            "thumbnailUrl": "/api/shared/<token>/day/1/thumbnail"
        }

    Response 403: Day is locked (not yet unlocked based on date)
    Response 404: Calendar or day not found
    Response 500: Internal server error

    Rate Limiting: Will be added in Issue #77
        - 30 requests/minute per IP
    """
    try:
        # Find calendar by share token
        calendar_found, calendar, error_msg = get_calendar_by_share_token(share_token)

        if not calendar_found:
            return jsonify({
                'error': 'Calendar not found or no longer shared'
            }), 404

        # Validate day number is within calendar duration
        if day_number < 1 or day_number > calendar['duration']:
            return jsonify({
                'error': f'Invalid day number. Must be between 1 and {calendar["duration"]}'
            }), 400

        # Check if day is unlocked (NFR [SC3]: Use unlock logic utility)
        day_is_unlocked = is_day_unlocked(calendar, day_number)

        if not day_is_unlocked:
            # Day is locked - do not return video information
            return jsonify({
                'error': f'Day {day_number} is locked. This day will unlock soon.',
                'dayNumber': day_number,
                'isUnlocked': False
            }), 403  # 403 Forbidden

        # Check if video exists for this day
        videos_dict = calendar.get('videos', {})
        video_info = videos_dict.get(str(day_number))

        if not video_info:
            return jsonify({
                'error': f'No video uploaded for day {day_number} yet'
            }), 404

        # Construct URLs for video and thumbnail
        video_url = f"/api/shared/{share_token}/day/{day_number}/stream"
        thumbnail_url = f"/api/shared/{share_token}/day/{day_number}/thumbnail"

        # Return success response with video metadata
        return jsonify({
            'success': True,
            'dayNumber': day_number,
            'isUnlocked': True,
            'videoUrl': video_url,
            'thumbnailUrl': thumbnail_url
        }), 200

    except Exception as e:
        print(f"Get shared day error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@shared_bp.route('/shared/<share_token>/day/<int:day_number>/thumbnail', methods=['GET'])
def get_shared_thumbnail(share_token, day_number):
    """
    Get thumbnail image for a shared calendar day (public access, requires unlock)

    Returns the actual thumbnail image file for display in the door grid.
    Only returns the file if the day is unlocked.

    NFR Compliance:
        - [P3] Performance: Fast thumbnail delivery for door grid rendering
        - [S4] Input Validation: Token and day validated
        - Privacy: Only accessible if day is unlocked

    URL: GET /api/shared/<share_token>/day/<day_number>/thumbnail

    Response 200: Thumbnail image file (image/jpeg)
    Response 403: Day is locked
    Response 404: Calendar or thumbnail not found
    Response 500: Internal server error

    Rate Limiting: Will be added in Issue #77
        - 30 requests/minute per IP
    """
    try:
        # Find calendar by share token
        calendar_found, calendar, error_msg = get_calendar_by_share_token(share_token)

        if not calendar_found:
            return jsonify({
                'error': 'Calendar not found or no longer shared'
            }), 404

        # Validate day number
        if day_number < 1 or day_number > calendar['duration']:
            return jsonify({
                'error': f'Invalid day number. Must be between 1 and {calendar["duration"]}'
            }), 400

        # Check if day is unlocked
        day_is_unlocked = is_day_unlocked(calendar, day_number)

        if not day_is_unlocked:
            # Day is locked - do not return thumbnail
            return jsonify({
                'error': f'Day {day_number} is locked'
            }), 403

        # Get user ID and calendar ID from calendar data
        user_id = calendar['userId']
        calendar_id = calendar['id']

        # Get thumbnail path
        thumbnail_path = get_thumbnail_path(user_id, calendar_id, day_number)

        if not thumbnail_path.exists():
            return jsonify({
                'error': f'Thumbnail not found for day {day_number}'
            }), 404

        # Send thumbnail file
        return send_file(
            str(thumbnail_path),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f'day_{day_number}_thumbnail.jpg'
        )

    except ValueError as e:
        # Path validation error
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Get shared thumbnail error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@shared_bp.route('/shared/<share_token>/day/<int:day_number>/stream', methods=['GET'])
def stream_shared_video(share_token, day_number):
    """
    Stream video file for a shared calendar day (public access, requires unlock)

    Returns the actual video file for HTML5 video playback.
    Only returns the file if the day is unlocked.

    NFR Compliance:
        - [P3] Performance: Efficient video delivery
        - [S4] Input Validation: Token and day validated
        - Privacy: Only accessible if day is unlocked
        - Video Protection: controlsList attribute set in frontend

    URL: GET /api/shared/<share_token>/day/<day_number>/stream

    Response 200: Video file (video/mp4)
    Response 403: Day is locked
    Response 404: Calendar or video not found
    Response 500: Internal server error

    Rate Limiting: Will be added in Issue #77
        - 30 requests/minute per IP
    """
    try:
        # Find calendar by share token
        calendar_found, calendar, error_msg = get_calendar_by_share_token(share_token)

        if not calendar_found:
            return jsonify({
                'error': 'Calendar not found or no longer shared'
            }), 404

        # Validate day number
        if day_number < 1 or day_number > calendar['duration']:
            return jsonify({
                'error': f'Invalid day number. Must be between 1 and {calendar["duration"]}'
            }), 400

        # Check if day is unlocked
        day_is_unlocked = is_day_unlocked(calendar, day_number)

        if not day_is_unlocked:
            # Day is locked - do not return video
            return jsonify({
                'error': f'Day {day_number} is locked'
            }), 403

        # Check if video exists for this day
        videos_dict = calendar.get('videos', {})
        if str(day_number) not in videos_dict:
            return jsonify({
                'error': f'No video uploaded for day {day_number}'
            }), 404

        # Get user ID and calendar ID from calendar data
        user_id = calendar['userId']
        calendar_id = calendar['id']

        # Get video path
        video_path = get_video_path(user_id, calendar_id, day_number)

        if not video_path.exists():
            return jsonify({
                'error': f'Video file not found for day {day_number}'
            }), 404

        # Send video file
        return send_file(
            str(video_path),
            mimetype='video/mp4',
            as_attachment=False,
            download_name=f'day_{day_number}_video.mp4'
        )

    except ValueError as e:
        # Path validation error
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Stream shared video error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
