# Calendar Routes
from flask import Blueprint, request, jsonify

from app.utils.decorators import token_required
from app.services.calendar_service import create_calendar as create_calendar_service, get_user_calendars, get_calendar_by_id

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendars', methods=['GET'])
@token_required
def get_calendars(current_user):
    """Get all calendars for the authenticated user"""
    try:
        # Get user's calendars using service layer (NFR [SC3]: Modular architecture)
        success, calendars, error_message = get_user_calendars(current_user['id'])
        
        if not success:
            return jsonify({
                'error': error_message
            }), 500
        
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
def create_calendar(current_user):
    """Create a new calendar for the authenticated user"""
    try:
        # Get JSON data from request (NFR [S4]: Input validation)
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400
        
        # Extract calendar data
        title = data.get('title', '').strip()
        start_date = data.get('startDate', '').strip()
        duration = data.get('duration')
        
        # Create calendar using service layer (NFR [SC3]: Modular architecture)
        success, calendar_data, error_message = create_calendar_service(
            user_id=current_user['id'],
            title=title,
            start_date=start_date,
            duration=duration
        )
        
        if not success:
            return jsonify({
                'error': error_message
            }), 400
        
        # Return created calendar data (NFR [P3]: Calendar creation under 3 seconds)
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
        # Placeholder response for Issue 1
        return jsonify({
            'success': True,
            'message': f'Calendar {calendar_id} endpoint working',
            'calendar': {
                'id': calendar_id,
                'title': 'Test Calendar',
                'status': 'active'
            }
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
        # Placeholder response for Issue 1
        return jsonify({
            'success': True,
            'message': f'Calendar {calendar_id} update endpoint working',
            'calendar': {
                'id': calendar_id,
                'status': 'updated'
            }
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
        # Placeholder response for Issue 1
        return jsonify({
            'success': True,
            'message': f'Calendar {calendar_id} delete endpoint working'
        }), 200
        
    except Exception as e:
        print(f"Delete calendar error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500