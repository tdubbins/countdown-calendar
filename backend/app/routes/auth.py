# Authentication Routes
from flask import Blueprint, request, jsonify

from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.utils.decorators import token_required
from app.utils.logger import logger

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with email and password validation"""
    try:
        # Get JSON data from request
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
        except Exception:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400
        
        email = data.get('email', '')
        password = data.get('password', '')
        confirm_password = data.get('confirmPassword', '')

        # Get frontend URL from request (sent by frontend) or fall back to Origin header
        frontend_url = data.get('frontendUrl') or request.headers.get('Origin')

        # Register user
        success, message, user_data = AuthService.register_user(email, password, confirm_password)

        if not success:
            return jsonify({'error': message}), 400

        # Generate verification token and send email
        verification_token = EmailService.generate_verification_token(
            user_data['user_id'],
            user_data['email']
        )
        email_sent, email_message = EmailService.send_verification_email(
            user_data['email'],
            verification_token,
            frontend_url=frontend_url
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email: {email_message}")
            return jsonify({
                'success': True,
                'message': 'User registered successfully, but verification email could not be sent. Please contact support.',
                'user_id': user_data['user_id'],
                'email_sent': False
            }), 201
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'User registered successfully. Please check your email to verify your account.',
            'user_id': user_data['user_id'],
            'email_sent': True
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/auth/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email using verification token"""
    try:
        success, message, user_data = EmailService.verify_email_token(token)

        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 400

        return jsonify({
            'success': True,
            'message': message,
            'user_id': user_data['user_id'] if user_data else None
        }), 200

    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/auth/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email to unverified user"""
    try:
        # Get JSON data from request
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
        except Exception:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400

        email = data.get('email', '')

        # Get frontend URL from request (sent by frontend) or fall back to Origin header
        frontend_url = data.get('frontendUrl') or request.headers.get('Origin')

        # Resend verification email
        success, message = AuthService.resend_verification_email(email, frontend_url=frontend_url)

        if not success:
            return jsonify({'error': message}), 429  # 429 Too Many Requests for rate limiting

        return jsonify({
            'success': True,
            'message': message
        }), 200

    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        # Get JSON data from request
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
        except Exception:
            return jsonify({
                'error': 'Request must contain JSON data'
            }), 400
        
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Authenticate user
        success, message, auth_data = AuthService.login_user(email, password)
        
        if not success:
            status_code = 403 if "verify your email" in message else 401
            return jsonify({'error': message}), status_code
        
        return jsonify({
            'success': True,
            'message': message,
            'token': auth_data['token'],
            'user': auth_data['user']
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (token invalidation handled client-side)"""
    try:
        # For JWT tokens, logout is typically handled client-side by removing the token
        # We can add server-side token blacklisting in the future if needed
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/auth/profile', methods=['GET'])
@token_required
def get_user_profile():
    """Get current user's profile information"""
    try:
        user_id = request.current_user['user_id']
        
        # Get user profile
        user = AuthService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500