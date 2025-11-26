# User Profile Routes
from flask import Blueprint, request, jsonify

from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.templates.email_templates import EmailTemplates
from app.utils.decorators import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/users/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile information (email and/or display name)"""
    try:
        user_id = request.current_user['user_id']

        # Get JSON data from request
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
        except Exception:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400

        # Validate at least one field is provided
        if 'email' not in data and 'display_name' not in data:
            return jsonify({
                'error': 'At least one field (email or display_name) must be provided'
            }), 400

        # Build update data - only include fields that are present in request
        # This allows distinguishing between "not sent" vs "sent as null to clear"
        update_fields = {}
        if 'email' in data:
            update_fields['email'] = data['email']
        if 'display_name' in data:
            update_fields['display_name'] = data['display_name']

        # Update user profile
        success, message, result_data = AuthService.update_user_profile(
            user_id=user_id,
            update_fields=update_fields
        )

        if not success:
            return jsonify({'error': message}), 400

        # Send email notification about profile changes
        updated_user = result_data['user']
        changes = result_data['changes']

        if changes:
            email_template = EmailTemplates.profile_updated(
                email=updated_user['email'],
                changes=changes
            )

            # Send notification email (don't fail the request if email fails)
            try:
                EmailService.send_email(
                    to_email=updated_user['email'],
                    subject=email_template['subject'],
                    body=email_template['body']
                )
            except Exception as e:
                print(f"Warning: Failed to send profile update notification: {e}")

        return jsonify({
            'success': True,
            'message': message,
            'user': updated_user
        }), 200

    except Exception as e:
        print(f"Profile update error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@user_bp.route('/users/password', methods=['PUT'])
@token_required
def change_password():
    """Change user's password with current password verification"""
    try:
        user_id = request.current_user['user_id']

        # Get JSON data from request
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
        except Exception:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400

        # Extract required fields
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        # Validate required fields
        if not current_password or not new_password or not confirm_password:
            return jsonify({
                'error': 'All password fields are required'
            }), 400

        # Change password
        success, message = AuthService.change_user_password(
            user_id=user_id,
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password
        )

        if not success:
            return jsonify({'error': message}), 400

        # Get user's email for notification
        user = AuthService.get_user_by_id(user_id)
        if user:
            # Send password change notification email
            email_template = EmailTemplates.password_changed(email=user['email'])

            try:
                EmailService.send_email(
                    to_email=user['email'],
                    subject=email_template['subject'],
                    body=email_template['body']
                )
            except Exception as e:
                print(f"Warning: Failed to send password change notification: {e}")

        return jsonify({
            'success': True,
            'message': message
        }), 200

    except Exception as e:
        print(f"Password change error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@user_bp.route('/users/account', methods=['DELETE'])
@token_required
def delete_account():
    """Permanently delete user's account and all associated data"""
    try:
        user_id = request.current_user['user_id']

        # Get JSON data from request
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
        except Exception:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400

        # Extract password (required for security)
        password = data.get('password', '')

        if not password:
            return jsonify({
                'error': 'Password is required to delete account'
            }), 400

        # Get user's email before deletion (for email notification)
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404

        user_email = user['email']

        # Delete account and all data
        success, message = AuthService.delete_user_account(
            user_id=user_id,
            password=password
        )

        if not success:
            return jsonify({'error': message}), 400

        # Send account deletion confirmation email
        email_template = EmailTemplates.account_deleted(email=user_email)

        try:
            EmailService.send_email(
                to_email=user_email,
                subject=email_template['subject'],
                body=email_template['body']
            )
        except Exception as e:
            print(f"Warning: Failed to send account deletion email: {e}")
            # Continue - account is already deleted

        return jsonify({
            'success': True,
            'message': message
        }), 200

    except Exception as e:
        print(f"Account deletion error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500
