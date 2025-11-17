# Calendar Routes
import os
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from app.utils.decorators import token_required
from app.services.calendar_service import (
    create_calendar as create_calendar_service,
    get_user_calendars,
    get_calendar_by_id,
    update_calendar as update_calendar_service,
    delete_calendar as delete_calendar_service,
    publish_calendar,
    unpublish_calendar,
    get_public_calendar
)
from app.services.auth_service import AuthService
from app.utils.validators import validate_video_file_type, validate_video_file_size, validate_video_day_number, validate_video_duration
from app.utils.storage import check_storage_quota, get_video_path, get_thumbnail_path, delete_video_file
from app.utils.json_db import calendars_db, get_user_calendar_ids
from app.tasks import VideoCompressionTask, TaskQueue

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendars', methods=['GET'])
@token_required
def get_calendars():
    """Get all calendars for the authenticated user"""
    try:
        # Get user's calendars using service layer
        success, calendars, error_message = get_user_calendars(request.current_user['user_id'])
        
        if not success:
            return jsonify({
                'error': error_message
            }), 500
        
        # Return calendars list
        return jsonify({
            'success': True,
            'message': f'Found {len(calendars)} calendar(s)',
            'calendars': calendars
        }), 200
        
    except Exception as e:
        print(f"Get calendars error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@calendar_bp.route('/calendars', methods=['POST'])
@token_required
def create_calendar():
    """Create a new calendar for the authenticated user"""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400
        
        # Extract calendar data
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        start_date = data.get('startDate', '').strip()
        duration = data.get('duration')

        # Create calendar using service layer
        success, calendar_data, error_message = create_calendar_service(
            user_id=request.current_user['user_id'],
            title=title,
            description=description,
            start_date=start_date,
            duration=duration
        )
        
        if not success:
            return jsonify({
                'error': error_message
            }), 400
        
        # Return created calendar data
        return jsonify({
            'success': True,
            'message': 'Calendar created successfully',
            'calendar': calendar_data
        }), 201
        
    except Exception as e:
        print(f"Create calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@calendar_bp.route('/calendars/<calendar_id>', methods=['GET'])
def get_calendar(calendar_id):
    """
    Get a specific calendar by ID (public endpoint with optional authentication)

    Access control:
    - If calendar is published: Anyone can view
    - If calendar is not published: Only owner can view
    - Returns isOwner flag if viewer owns calendar
    """
    try:
        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400

        # Get optional authentication - extract user_id from JWT
        viewer_user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload, error = AuthService.verify_jwt_token(token)
                if not error and payload:
                    viewer_user_id = payload.get('user_id')
            except Exception:
                pass  # Invalid auth is okay, just treat as unauthenticated

        # Get calendar using public access service layer
        success, calendar_data, error_message = get_public_calendar(
            calendar_id.strip(),
            viewer_user_id
        )
        
        if not success:
            # Determine appropriate HTTP status code based on error
            if "not found" in error_message.lower():
                status_code = 404
            else:
                status_code = 500
                
            return jsonify({
                'error': error_message
            }), status_code
        
        # Return calendar data
        return jsonify({
            'success': True,
            'message': 'Calendar retrieved successfully',
            'calendar': calendar_data
        }), 200
        
    except Exception as e:
        print(f"Get calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@calendar_bp.route('/calendars/<calendar_id>', methods=['PUT'])
@token_required
def update_calendar(calendar_id):
    """
    Update a specific calendar for the authenticated user

    Issue #81: Extended to support door ordering customization for shared calendars

    Accepts optional fields:
        - title: str - Calendar title
        - startDate: str - Start date (YYYY-MM-DD)
        - duration: int - Number of days (1-31)
        - doorOrder: str - "sequential" or "random" (Issue #81)
        - doorPositions: list - Shuffled day positions for random order (Issue #81)
        - theme: str - Theme identifier like "christmas" (Issue #81)
        - timezone: str - IANA timezone like "Europe/Berlin" (Issue #81)

    NFR Compliance:
        - [S4] Input validation via service layer
        - [SC3] Modular architecture with service separation
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400
        
        # Extract update fields (only process allowed fields)
        title = data.get('title')
        description = data.get('description')        # Optional calendar description
        start_date = data.get('startDate')
        duration = data.get('duration')
        # Issue #81: Add door ordering fields for shared calendar customization
        door_order = data.get('doorOrder')           # "sequential" or "random"
        door_positions = data.get('doorPositions')   # Array of shuffled positions
        theme = data.get('theme')                    # Theme identifier (e.g., "christmas")
        timezone = data.get('timezone')              # IANA timezone (e.g., "Europe/Berlin")

        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400

        # Update calendar using service layer
        # Service layer handles validation for all fields including door ordering
        success, calendar_data, error_message = update_calendar_service(
            calendar_id=calendar_id.strip(),
            user_id=request.current_user['user_id'],
            title=title,
            description=description,         # Optional calendar description
            start_date=start_date,
            duration=duration,
            door_order=door_order,           # Issue #81: Pass door ordering
            door_positions=door_positions,   # Issue #81: Pass door positions
            theme=theme,                     # Issue #81: Pass theme
            tz=timezone                      # Issue #81: Pass timezone
        )
        
        if not success:
            # Determine appropriate HTTP status code based on error
            if "not found" in error_message.lower():
                status_code = 404
            elif "validation" in error_message.lower() or "invalid" in error_message.lower() or "required" in error_message.lower():
                status_code = 400
            else:
                status_code = 500
                
            return jsonify({
                'error': error_message
            }), status_code
        
        # Return updated calendar data
        return jsonify({
            'success': True,
            'message': 'Calendar updated successfully',
            'calendar': calendar_data
        }), 200
        
    except Exception as e:
        print(f"Update calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@calendar_bp.route('/calendars/<calendar_id>', methods=['DELETE'])
@token_required
def delete_calendar(calendar_id):
    """Delete a specific calendar for the authenticated user"""
    try:
        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400

        # Delete calendar using service layer
        success, error_message = delete_calendar_service(
            calendar_id.strip(),
            request.current_user['user_id']
        )

        if not success:
            # Determine appropriate HTTP status code based on error
            if "not found" in error_message.lower():
                status_code = 404
            else:
                status_code = 500

            return jsonify({
                'error': error_message
            }), status_code

        # Return 204 No Content for successful deletion (RESTful convention)
        return '', 204

    except Exception as e:
        print(f"Delete calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@calendar_bp.route('/calendars/<calendar_id>/publish', methods=['POST'])
@token_required
def publish_calendar_route(calendar_id):
    """
    Publish calendar (make it publicly accessible)

    Sets published: true in calendar meta.json, making it accessible via
    direct link /calendar/<calendar_id>

    NFR Compliance:
        - [S2] JWT authentication required
        - [S3] Multi-tenant isolation - ownership verified
        - [S4] Input validation - calendar ID validated
        - [SC3] RESTful API design

    Request:
        POST /api/calendars/<calendar_id>/publish
        Headers: Authorization: Bearer <jwt_token>

    Returns:
        200: Calendar published successfully
        {
            "success": true,
            "message": "Calendar published successfully"
        }

        400: Invalid calendar ID
        403: User doesn't own calendar
        404: Calendar not found
        500: Internal server error
    """
    try:
        user_id = request.current_user['user_id']

        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400

        # Publish calendar using service layer
        success, error_message = publish_calendar(
            calendar_id.strip(),
            user_id
        )

        if not success:
            # Determine appropriate HTTP status code
            if "not found" in error_message.lower():
                status_code = 404
            else:
                status_code = 403

            return jsonify({
                'error': error_message
            }), status_code

        return jsonify({
            'success': True,
            'message': 'Calendar published successfully'
        }), 200

    except Exception as e:
        print(f"Publish calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@calendar_bp.route('/calendars/<calendar_id>/unpublish', methods=['POST'])
@token_required
def unpublish_calendar_route(calendar_id):
    """
    Unpublish calendar (make it private again)

    Sets published: false in calendar meta.json, removing public access

    NFR Compliance:
        - [S2] JWT authentication required
        - [S3] Multi-tenant isolation - ownership verified
        - [S4] Input validation - calendar ID validated
        - [SC3] RESTful API design

    Request:
        POST /api/calendars/<calendar_id>/unpublish
        Headers: Authorization: Bearer <jwt_token>

    Returns:
        200: Calendar unpublished successfully
        {
            "success": true,
            "message": "Calendar unpublished successfully"
        }

        400: Invalid calendar ID
        403: User doesn't own calendar
        404: Calendar not found
        500: Internal server error
    """
    try:
        user_id = request.current_user['user_id']

        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400

        # Unpublish calendar using service layer
        success, error_message = unpublish_calendar(
            calendar_id.strip(),
            user_id
        )

        if not success:
            # Determine appropriate HTTP status code
            if "not found" in error_message.lower():
                status_code = 404
            else:
                status_code = 403

            return jsonify({
                'error': error_message
            }), status_code

        return jsonify({
            'success': True,
            'message': 'Calendar unpublished successfully'
        }), 200

    except Exception as e:
        print(f"Unpublish calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@calendar_bp.route('/calendars/<calendar_id>/videos', methods=['POST'])
@token_required
def upload_video(calendar_id):
    """
    Upload video for a specific day in the calendar (RESTful nested endpoint)

    NFR Compliance:
        - [R1] Video size limit: 50MB, duration: 3 minutes max
        - [S1] HTTPS for secure file uploads (configured in production)
        - [S2] JWT authentication required - user_id implicit from token
        - [S4] Input validation and sanitization
        - [SC2] Storage quota: 1GB per user limit
        - [P1] Upload processing <5 seconds before returning response
        - [U5] Clear error messages for accessibility

    Request:
        - multipart/form-data with 'video' file and 'day' integer
        - Authorization: Bearer <jwt_token>

    Returns:
        201: Video upload started successfully
        400: Invalid request (missing file, invalid day, validation errors)
        403: User doesn't own calendar
        404: Calendar not found
        413: Storage quota exceeded
        500: Internal server error
    """
    try:
        # Extract user ID from JWT token (NFR [S2]: Implicit authentication)
        user_id = request.current_user['user_id']

        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400

        # Get calendar and verify ownership (NFR [S2]: Multi-tenant security)
        success, calendar_data, error_message = get_calendar_by_id(
            calendar_id.strip(),
            user_id
        )

        if not success:
            # Return 404 for not found or ownership issues (don't reveal existence)
            return jsonify({
                'error': 'Calendar not found or access denied'
            }), 404 if "not found" in error_message.lower() else 403

        # Validate video file is present in request
        if 'video' not in request.files:
            return jsonify({
                'error': 'No video file provided. Please include a video file in the upload.'
            }), 400

        video_file = request.files['video']

        # Validate file was actually selected
        if video_file.filename == '':
            return jsonify({
                'error': 'No video file selected. Please select a video file to upload.'
            }), 400

        # Validate day number is present
        if 'day' not in request.form:
            return jsonify({
                'error': 'Day number is required. Please specify which day this video is for.'
            }), 400

        try:
            day = int(request.form['day'])
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid day number. Day must be a number between 1 and 31.'
            }), 400

        # Validate day number is within calendar duration (NFR [S4]: Input validation)
        day_valid, day_error = validate_video_day_number(day, calendar_data['duration'])
        if not day_valid:
            return jsonify({
                'error': day_error
            }), 400

        # Validate file type (NFR [S4]: Input validation)
        filename = secure_filename(video_file.filename)
        filetype_valid, filetype_error = validate_video_file_type(filename)
        if not filetype_valid:
            return jsonify({
                'error': filetype_error
            }), 400

        # Get file size (NFR [R1]: 50MB limit)
        video_file.seek(0, os.SEEK_END)
        file_size = video_file.tell()
        video_file.seek(0)  # Reset file pointer

        # Validate file size (NFR [R1]: 50MB max)
        filesize_valid, filesize_error = validate_video_file_size(file_size)
        if not filesize_valid:
            return jsonify({
                'error': filesize_error
            }), 400

        # Check storage quota (NFR [SC2]: 1GB per user)
        has_space, remaining_bytes, quota_error = check_storage_quota(user_id, file_size)
        if not has_space:
            return jsonify({
                'error': quota_error
            }), 413  # 413 Payload Too Large

        # Create temp directory within calendar folder (NFR [P1]: Fast upload processing)
        from app.utils.constants import StoragePaths
        temp_dir = os.path.join(StoragePaths.CALENDARS_DIR, calendar_id, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # Save to temporary storage
        # Path format: data/calendars/{calendar_id}/temp/{day}.mp4
        temp_filename = f"{day}.mp4"
        temp_path = os.path.join(temp_dir, temp_filename)

        video_file.save(temp_path)

        # Validate video duration using FFprobe (NFR [R1]: 3 minutes max)
        duration_valid, duration_seconds, duration_error = validate_video_duration(temp_path)
        if not duration_valid:
            # Clean up temp file on validation failure
            try:
                os.remove(temp_path)
            except Exception:
                pass

            return jsonify({
                'error': duration_error
            }), 400

        # Create background compression task (NFR [P1]: Returns quickly, processing in background)
        task_success, task_id, task_error = VideoCompressionTask.create_video_task(
            user_id=user_id,
            calendar_id=calendar_id,
            day=day,
            original_path=temp_path
        )

        if not task_success:
            # Clean up temp file if task creation fails
            try:
                os.remove(temp_path)
            except Exception:
                pass

            return jsonify({
                'error': f'Failed to create processing task: {task_error}'
            }), 500

        # Return success response with task information
        # Status "processing" indicates background work in progress
        return jsonify({
            'success': True,
            'message': 'Video upload started successfully. Processing in background.',
            'video': {
                'day': day,
                'status': 'processing',
                'uploaded_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'task_id': task_id,
                'duration': duration_seconds if duration_seconds else None
            }
        }), 201  # 201 Created

    except Exception as e:
        print(f"Video upload error: {str(e)}")
        return jsonify({
            'error': 'Internal server error during video upload'
        }), 500


@calendar_bp.route('/calendars/<calendar_id>/videos', methods=['GET'])
@token_required
def list_videos(calendar_id):
    """
    List all videos for a calendar (RESTful nested endpoint)

    NFR Compliance:
        - [S2] JWT authentication required
        - [S3] Multi-tenant isolation - ownership validation
        - [P3] Video listing response <3 seconds
        - [SC3] RESTful API design - videos as calendar sub-resources

    Returns:
        200: List of videos with metadata
        404: Calendar not found or access denied
        500: Internal server error
    """
    try:
        user_id = request.current_user['user_id']

        # Validate calendar ID
        if not calendar_id or not calendar_id.strip():
            return jsonify({'error': 'Invalid calendar ID'}), 400

        # Get calendar and verify ownership
        success, calendar_data, error_message = get_calendar_by_id(
            calendar_id.strip(),
            user_id
        )

        if not success:
            return jsonify({'error': 'Calendar not found or access denied'}), 404

        # Get videos from calendar data
        videos_dict = calendar_data.get('videos', {})
        calendar_duration = calendar_data.get('duration', 31)

        # Convert to list format with metadata
        # BUG FIX: Only include videos within current calendar duration
        # When duration is reduced (e.g., 5 days → 4 days), exclude videos beyond new duration
        videos_list = []
        for day_str, video_info in videos_dict.items():
            day_number = int(day_str)

            # Skip videos that exceed current calendar duration
            if day_number > calendar_duration:
                continue

            video_metadata = {
                'day': day_number,
                'filename': video_info.get('filename'),
                'thumbnail': video_info.get('thumbnail'),
                'size': video_info.get('size', 0),
                'duration': video_info.get('duration', 0),
                'uploaded_at': video_info.get('uploaded_at'),
                'status': video_info.get('status', 'completed')
            }
            videos_list.append(video_metadata)

        # Sort by day number
        videos_list.sort(key=lambda x: x['day'])

        return jsonify({
            'success': True,
            'message': f'Found {len(videos_list)} video(s)',
            'videos': videos_list,
            'videoCount': len(videos_list)
        }), 200

    except Exception as e:
        print(f"List videos error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@calendar_bp.route('/calendars/<calendar_id>/videos/<int:day>', methods=['GET'])
@token_required
def get_video_metadata(calendar_id, day):
    """
    Get metadata for a specific day's video (RESTful nested endpoint)

    NFR Compliance:
        - [S2] JWT authentication required
        - [S3] Multi-tenant isolation - ownership validation
        - [SC3] RESTful API design

    Returns:
        200: Video metadata with streaming URLs
        404: Video not found
        500: Internal server error
    """
    try:
        user_id = request.current_user['user_id']

        # Validate calendar ID
        if not calendar_id or not calendar_id.strip():
            return jsonify({'error': 'Invalid calendar ID'}), 400

        # Get calendar and verify ownership
        success, calendar_data, error_message = get_calendar_by_id(
            calendar_id.strip(),
            user_id
        )

        if not success:
            return jsonify({'error': 'Calendar not found or access denied'}), 404

        # Get video info for this day
        videos_dict = calendar_data.get('videos', {})
        video_info = videos_dict.get(str(day))

        if not video_info:
            return jsonify({'error': f'No video found for day {day}'}), 404

        # Construct streaming URLs
        video_url = f"/api/calendars/{calendar_id}/videos/{day}/stream"
        thumbnail_url = f"/api/calendars/{calendar_id}/videos/{day}/thumbnail"

        video_metadata = {
            'day': day,
            'filename': video_info.get('filename'),
            'thumbnail': video_info.get('thumbnail'),
            'size': video_info.get('size', 0),
            'duration': video_info.get('duration', 0),
            'uploaded_at': video_info.get('uploaded_at'),
            'status': video_info.get('status', 'completed'),
            'stream_url': video_url,
            'thumbnail_url': thumbnail_url
        }

        return jsonify({
            'success': True,
            'video': video_metadata
        }), 200

    except Exception as e:
        print(f"Get video metadata error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@calendar_bp.route('/calendars/<calendar_id>/videos/<int:day>/status', methods=['GET'])
@token_required
def get_video_status(calendar_id, day):
    """
    Get processing status for a video upload (RESTful nested endpoint)

    This endpoint allows the frontend to poll for video processing status
    after upload. Returns task status and progress.

    NFR Compliance:
        - [S2] JWT authentication required
        - [S3] Multi-tenant isolation - ownership validation
        - [P2] Fast status check

    Returns:
        200: Status information (pending, processing, completed, failed)
        404: No task found for this video
        500: Internal server error
    """
    try:
        user_id = request.current_user['user_id']

        # Validate calendar ID
        if not calendar_id or not calendar_id.strip():
            return jsonify({'error': 'Invalid calendar ID'}), 400

        # Get calendar and verify ownership
        success, calendar_data, error_message = get_calendar_by_id(
            calendar_id.strip(),
            user_id
        )

        if not success:
            return jsonify({'error': 'Calendar not found or access denied'}), 404

        # Check if video exists in calendar (completed)
        videos_dict = calendar_data.get('videos', {})
        video_info = videos_dict.get(str(day))

        if video_info and video_info.get('status') == 'completed':
            # Video is completed
            return jsonify({
                'success': True,
                'status': 'completed',
                'progress': 100,
                'message': 'Video processing completed',
                'video': {
                    'day': day,
                    'filename': video_info.get('filename'),
                    'size': video_info.get('size', 0),
                    'duration': video_info.get('duration', 0)
                }
            }), 200

        # Check for active/pending task
        task_success, task_data, task_error = TaskQueue.get_task_by_video(
            user_id,
            calendar_id,
            day
        )

        if task_success:
            # Task found - return status
            status = task_data.get('status')
            progress = task_data.get('progress', 0)
            error = task_data.get('error')

            response = {
                'success': status != 'failed',
                'status': status,
                'progress': progress
            }

            if status == 'processing':
                response['message'] = 'Video is being processed'
            elif status == 'pending':
                response['message'] = 'Video is waiting to be processed'
            elif status == 'failed':
                response['message'] = 'Video processing failed'
                response['error'] = error
            elif status == 'completed':
                response['message'] = 'Video processing completed'

            return jsonify(response), 200
        else:
            # No task found
            return jsonify({
                'error': f'No processing task found for day {day}'
            }), 404

    except Exception as e:
        print(f"Get video status error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@calendar_bp.route('/calendars/<calendar_id>/videos/<int:day>/thumbnail', methods=['GET'])
def get_video_thumbnail(calendar_id, day):
    """
    Get thumbnail image for a video (RESTful nested endpoint)

    Returns the actual image file for display.

    Access Control (NEW):
        - If authenticated and owner: Access all thumbnails regardless of lock state
        - If not owner (or not authenticated): Only access unlocked days (403 for locked)

    NFR Compliance:
        - [S2] Optional JWT authentication (owner gets full access)
        - [S3] Multi-tenant isolation - ownership validation
        - [P3] Fast thumbnail delivery

    Returns:
        200: Thumbnail image file (image/jpeg)
        403: Day is locked (for non-owners)
        404: Thumbnail not found or calendar not published
        500: Internal server error
    """
    try:
        # Validate calendar ID
        if not calendar_id or not calendar_id.strip():
            return jsonify({'error': 'Invalid calendar ID'}), 400

        # Get optional authentication to check ownership
        viewer_user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload, error = AuthService.verify_jwt_token(token)
                if not error and payload:
                    viewer_user_id = payload.get('user_id')
            except Exception:
                pass  # Invalid auth is okay, just treat as non-owner

        # Get calendar using public access (checks published status and ownership)
        success, calendar_data, error_message = get_public_calendar(
            calendar_id.strip(),
            viewer_user_id
        )

        # Extract isOwner flag from calendar_data
        is_owner = calendar_data.get('isOwner', False) if success else False

        if not success:
            return jsonify({'error': 'Calendar not found or not accessible'}), 404

        # Check access permission for this specific day
        # Owners can access all days regardless of lock state
        if not is_owner:
            # Non-owners must respect unlock logic
            from app.utils.unlock_logic import is_day_unlocked

            if not is_day_unlocked(calendar_data, day):
                return jsonify({'error': f'Day {day} is locked'}), 403

        # Get thumbnail path
        thumbnail_path = get_thumbnail_path(calendar_id, day)

        if not thumbnail_path.exists():
            return jsonify({'error': f'Thumbnail not found for day {day}'}), 404

        # Send file with proper MIME type
        return send_file(
            str(thumbnail_path),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f'day_{day}_thumbnail.jpg'
        )

    except ValueError as e:
        # Path validation error
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Get thumbnail error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@calendar_bp.route('/calendars/<calendar_id>/videos/<int:day>/stream', methods=['GET'])
def stream_video(calendar_id, day):
    """
    Stream video file for playback (RESTful nested endpoint)

    Returns the actual video file for HTML5 video player.

    Access Control (NEW):
        - If authenticated and owner: Access all videos regardless of lock state
        - If not owner (or not authenticated): Only access unlocked days (403 for locked)

    NFR Compliance:
        - [S2] Optional JWT authentication (owner gets full access)
        - [S3] Multi-tenant isolation - ownership validation
        - [P3] Fast video delivery

    Returns:
        200: Video file (video/mp4)
        403: Day is locked (for non-owners)
        404: Video not found or calendar not published
        500: Internal server error
    """
    try:
        # Validate calendar ID
        if not calendar_id or not calendar_id.strip():
            return jsonify({'error': 'Invalid calendar ID'}), 400

        # Get optional authentication to check ownership
        viewer_user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload, error = AuthService.verify_jwt_token(token)
                if not error and payload:
                    viewer_user_id = payload.get('user_id')
            except Exception:
                pass  # Invalid auth is okay, just treat as non-owner

        # Get calendar using public access (checks published status and ownership)
        success, calendar_data, error_message = get_public_calendar(
            calendar_id.strip(),
            viewer_user_id
        )

        if not success:
            return jsonify({'error': 'Calendar not found or not accessible'}), 404

        # Extract isOwner flag from calendar_data
        is_owner = calendar_data.get('isOwner', False)

        # Check access permission for this specific day
        # Owners can access all days regardless of lock state
        if not is_owner:
            # Non-owners must respect unlock logic
            from app.utils.unlock_logic import is_day_unlocked

            if not is_day_unlocked(calendar_data, day):
                return jsonify({'error': f'Day {day} is locked'}), 403

        # Get video path
        video_path = get_video_path(calendar_id, day)

        if not video_path.exists():
            return jsonify({'error': f'Video not found for day {day}'}), 404

        # Send file with proper MIME type
        return send_file(
            str(video_path),
            mimetype='video/mp4',
            as_attachment=False,
            download_name=f'day_{day}_video.mp4'
        )

    except ValueError as e:
        # Path validation error
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Stream video error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@calendar_bp.route('/calendars/<calendar_id>/videos/<int:day>', methods=['DELETE'])
@token_required
def delete_video(calendar_id, day):
    """
    Delete video and thumbnail for a specific day (RESTful nested endpoint)

    Performs atomic cleanup:
    - Deletes video file
    - Deletes thumbnail file
    - Updates calendar.videos array
    - Updates calendar.videoCount
    - Updates calendar.videoStorageUsed

    NFR Compliance:
        - [S2] JWT authentication required
        - [S3] Multi-tenant isolation - ownership validation
        - [SC3] RESTful API design
        - GDPR: Complete data removal

    Returns:
        204: Video deleted successfully (No Content)
        404: Video or calendar not found
        500: Internal server error
    """
    try:
        user_id = request.current_user['user_id']

        # Validate calendar ID
        if not calendar_id or not calendar_id.strip():
            return jsonify({'error': 'Invalid calendar ID'}), 400

        # Get calendar and verify ownership
        success, calendar_data, error_message = get_calendar_by_id(
            calendar_id.strip(),
            user_id
        )

        if not success:
            return jsonify({'error': 'Calendar not found or access denied'}), 404

        # Check if video exists
        videos_dict = calendar_data.get('videos', {})
        if str(day) not in videos_dict:
            return jsonify({'error': f'No video found for day {day}'}), 404

        # Get video size before deletion (for storage calculation)
        video_size = videos_dict[str(day)].get('size', 0)

        # Delete video and thumbnail files
        files_deleted = delete_video_file(calendar_id, day)

        if not files_deleted:
            print(f"Warning: No files deleted for calendar {calendar_id}, day {day}")

        # Remove from calendar.videos dict
        del videos_dict[str(day)]

        # Update calendar metadata
        new_video_count = len(videos_dict)
        new_storage_used = calendar_data.get('videoStorageUsed', 0) - video_size

        # Ensure storage doesn't go negative
        if new_storage_used < 0:
            new_storage_used = 0

        updates = {
            'videos': videos_dict,
            'videoCount': new_video_count,
            'videoStorageUsed': new_storage_used,
            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        # Update calendar metadata in distributed structure
        calendars_db.update_calendar_meta(calendar_id, updates)

        # Return 204 No Content (RESTful convention for successful DELETE)
        return '', 204

    except ValueError as e:
        # Path validation error
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Delete video error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500