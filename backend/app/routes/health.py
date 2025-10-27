# Health Check Routes
from flask import Blueprint, jsonify
from flask import current_app
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check endpoint - tells us the server is running"""
    return jsonify({
        'status': 'healthy',
        'message': current_app.config['APP_NAME'],
        'version': current_app.config['API_VERSION'],
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'debug': current_app.config['DEBUG']
    })

@health_bp.route('/')
def home():
    """Welcome message for the API"""
    return jsonify({
        'message': 'Welcome to Advent Calendar API',
        'endpoints': {
            'health': '/health',
            'auth': '/api/auth/*',
            'docs': 'Coming soon...'
        }
    })