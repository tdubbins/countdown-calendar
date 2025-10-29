# Calendar Routes
from flask import Blueprint, request, jsonify

from app.utils.decorators import token_required
from app.services.calendar_service import create_calendar as create_calendar_service, get_user_calendars, get_calendar_by_id, update_calendar as update_calendar_service, delete_calendar as delete_calendar_service

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