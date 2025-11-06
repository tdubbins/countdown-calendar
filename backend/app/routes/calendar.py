# Calendar Routes
import os
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from app.utils.decorators import token_required
from app.services.calendar_service import create_calendar as create_calendar_service, get_user_calendars, get_calendar_by_id, update_calendar as update_calendar_service, delete_calendar as delete_calendar_service
from app.utils.validators import validate_video_file_type, validate_video_file_size, validate_video_day_number, validate_video_duration
from app.utils.storage import check_storage_quota
from app.tasks import VideoCompressionTask

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
        start_date = data.get('startDate', '').strip()
        duration = data.get('duration')
        
        # Create calendar using service layer
        success, calendar_data, error_message = create_calendar_service(
            user_id=request.current_user['user_id'],
            title=title,
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
@token_required
def get_calendar(calendar_id):
    """Get a specific calendar by ID for the authenticated user"""
    try:
        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400
        
        # Get calendar using service layer
        success, calendar_data, error_message = get_calendar_by_id(
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
    """Update a specific calendar for the authenticated user"""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400
        
        # Extract update fields (only process allowed fields)
        title = data.get('title')
        start_date = data.get('startDate')
        duration = data.get('duration')
        
        # Validate calendar ID format
        if not calendar_id or not calendar_id.strip():
            return jsonify({
                'error': 'Invalid calendar ID'
            }), 400
        
        # Update calendar using service layer
        success, calendar_data, error_message = update_calendar_service(
            calendar_id=calendar_id.strip(),
            user_id=request.current_user['user_id'],
            title=title,
            start_date=start_date,
            duration=duration
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

        # Create temp directory if it doesn't exist
        temp_dir = 'uploads/temp'
        os.makedirs(temp_dir, exist_ok=True)

        # Save to temporary storage (NFR [P1]: Fast upload processing)
        # Path format: uploads/temp/{user_id}_{calendar_id}_{day}.mp4
        temp_filename = f"{user_id}_{calendar_id}_{day}.mp4"
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