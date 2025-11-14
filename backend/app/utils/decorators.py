# Authentication Decorators
from functools import wraps
from flask import request, jsonify

from app.services.auth_service import AuthService

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer TOKEN"
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401

        if not token:
            return jsonify({'error': 'Access token is missing'}), 401

        # Verify token
        payload, error = AuthService.verify_jwt_token(token)
        if error:
            return jsonify({'error': error}), 401

        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)

    return decorated


def get_optional_user():
    """
    Extract user from JWT token if present (optional authentication)

    This function checks for an Authorization header and attempts to verify
    the JWT token. If a valid token is present, returns the user payload.
    If no token or invalid token, returns None (no error raised).

    Used for endpoints that support optional authentication (e.g., shared calendars
    where we want to detect if the viewer is the owner).

    Returns:
        dict | None: User payload if authenticated, None otherwise
    """
    try:
        # Check for Authorization header
        if 'Authorization' not in request.headers:
            return None

        auth_header = request.headers['Authorization']

        # Extract token from "Bearer TOKEN" format
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return None  # Invalid format, but don't raise error

        # Verify token
        payload, error = AuthService.verify_jwt_token(token)
        if error:
            return None  # Invalid token, but don't raise error

        return payload

    except Exception:
        # Any error in optional authentication returns None
        return None