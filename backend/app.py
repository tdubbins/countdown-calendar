# Basic Flask application for Advent Calendar backend
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import config
import os
import json
import bcrypt
import uuid
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
import re

# Create Flask application instance
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS for frontend communication
CORS(app)

# File path for user data storage
USERS_FILE = 'users.json'

# Helper functions for user management
def load_users():
    """Load users from JSON file, create empty file if it doesn't exist"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create empty users file if it doesn't exist
        users_data = {'users': []}
        save_users(users_data)
        return users_data
    except json.JSONDecodeError:
        # Handle corrupted JSON file
        print(f"Warning: {USERS_FILE} is corrupted, creating new file")
        users_data = {'users': []}
        save_users(users_data)
        return users_data

def save_users(users_data):
    """Save users data to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)

def validate_password(password):
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def hash_password(password):
    """Hash password using bcrypt for secure storage"""
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds for good security/performance balance
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def email_exists(email, users_data):
    """Check if email already exists in user database"""
    for user in users_data['users']:
        if user['email'].lower() == email.lower():
            return True
    return False

# Route: When someone visits this URL, run this function
@app.route('/health')
def health_check():
    """Health check endpoint - tells us the server is running"""
    return jsonify({
        'status': 'healthy',
        'message': app.config['APP_NAME'],
        'version': app.config['API_VERSION'],
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'debug': app.config['DEBUG']
    })

# Route: Root endpoint (home page)
@app.route('/')
def home():
    """Welcome message for the API"""
    return jsonify({
        'message': 'Welcome to Advent Calendar API',
        'endpoints': {
            'health': '/health',
            'docs': 'Coming soon...'
        }
    })

# Route: User registration endpoint
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user with email and password validation"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Check if required fields are present
        if not data or 'email' not in data or 'password' not in data or 'confirmPassword' not in data:
            return jsonify({
                'error': 'Missing required fields: email, password, confirmPassword'
            }), 400
        
        email = data['email'].strip()
        password = data['password']
        confirm_password = data['confirmPassword']
        
        # Validate email format
        try:
            valid_email = validate_email(email)
            email = valid_email.email  # Normalized email
        except EmailNotValidError:
            return jsonify({
                'error': 'Invalid email format'
            }), 400
        
        # Validate password confirmation
        if password != confirm_password:
            return jsonify({
                'error': 'Passwords do not match'
            }), 400
        
        # Validate password requirements
        is_valid, password_error = validate_password(password)
        if not is_valid:
            return jsonify({
                'error': password_error
            }), 400
        
        # Load existing users
        users_data = load_users()
        
        # Check if email already exists
        if email_exists(email, users_data):
            return jsonify({
                'error': 'Email address is already registered'
            }), 409
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        new_user = {
            'id': user_id,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat(),
            'email_verified': False
        }
        
        # Add user to database
        users_data['users'].append(new_user)
        save_users(users_data)
        
        # Return success response (no password in response)
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

# Run the app in development mode
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)