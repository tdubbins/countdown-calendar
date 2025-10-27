# Basic Flask application for Advent Calendar backend
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mail import Mail, Message
from config import config
import os
import json
import bcrypt
import uuid
import jwt
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from functools import wraps
import re

# Create Flask application instance
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS for frontend communication
CORS(app)

# Initialize Flask-Mail
mail = Mail(app)

# File paths for data storage
USERS_FILE = 'users.json'
EMAIL_TOKENS_FILE = 'email_tokens.json'

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

# Email verification token management
def load_email_tokens():
    """Load email tokens from JSON file, create empty file if it doesn't exist"""
    try:
        with open(EMAIL_TOKENS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        tokens_data = {'tokens': []}
        save_email_tokens(tokens_data)
        return tokens_data
    except json.JSONDecodeError:
        print(f"Warning: {EMAIL_TOKENS_FILE} is corrupted, creating new file")
        tokens_data = {'tokens': []}
        save_email_tokens(tokens_data)
        return tokens_data

def save_email_tokens(tokens_data):
    """Save email tokens data to JSON file"""
    with open(EMAIL_TOKENS_FILE, 'w') as f:
        json.dump(tokens_data, f, indent=2)

def generate_verification_token(user_id, email):
    """Generate a unique verification token for email verification"""
    token = str(uuid.uuid4())
    expiry_time = datetime.now() + timedelta(hours=24)  # 24-hour expiration
    
    tokens_data = load_email_tokens()
    
    # Add new token
    new_token = {
        'token': token,
        'user_id': user_id,
        'email': email,
        'created_at': datetime.now().isoformat(),
        'expires_at': expiry_time.isoformat(),
        'used': False
    }
    
    tokens_data['tokens'].append(new_token)
    save_email_tokens(tokens_data)
    
    return token

def validate_verification_token(token):
    """Validate verification token and return user info if valid"""
    tokens_data = load_email_tokens()
    
    for token_info in tokens_data['tokens']:
        if token_info['token'] == token:
            # Check if token is already used
            if token_info['used']:
                return None, "Token has already been used"
            
            # Check if token is expired
            expiry_time = datetime.fromisoformat(token_info['expires_at'])
            if datetime.now() > expiry_time:
                return None, "Token has expired"
            
            # Token is valid
            return token_info, None
    
    return None, "Invalid token"

def mark_token_as_used(token):
    """Mark a verification token as used"""
    tokens_data = load_email_tokens()
    
    for token_info in tokens_data['tokens']:
        if token_info['token'] == token:
            token_info['used'] = True
            token_info['used_at'] = datetime.now().isoformat()
            save_email_tokens(tokens_data)
            return True
    
    return False

def cleanup_expired_tokens():
    """Remove expired tokens from storage (optional cleanup function)"""
    tokens_data = load_email_tokens()
    current_time = datetime.now()
    
    # Keep only non-expired tokens
    tokens_data['tokens'] = [
        token for token in tokens_data['tokens']
        if datetime.fromisoformat(token['expires_at']) > current_time
    ]
    
    save_email_tokens(tokens_data)

def send_verification_email(email, token):
    """Send verification email to user"""
    try:
        # Create verification URL (you'll need to adjust this for your frontend URL)
        verification_url = f"http://localhost:8100/verify-email/{token}"
        
        # Create email message
        msg = Message(
            subject="Verify Your Email - Countdown Calendar",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        
        # Email body (HTML)
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">📅 Countdown Calendar</h1>
                </div>
                
                <h2>Welcome! Please verify your email address</h2>
                
                <p>Thank you for registering with Countdown Calendar! To complete your registration and activate your account, please click the button below to verify your email address.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="display: inline-block; padding: 15px 30px; background-color: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Verify Email Address
                    </a>
                </div>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 14px; color: #666;">
                    <p><strong>Important:</strong> This verification link will expire in 24 hours.</p>
                    <p>If you didn't create this account, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version (fallback)
        msg.body = f"""
        Welcome to Countdown Calendar!
        
        Please verify your email address by clicking this link:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create this account, please ignore this email.
        """
        
        # Send email
        mail.send(msg)
        return True, "Verification email sent successfully"
        
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return False, f"Failed to send email: {str(e)}"

# JWT Authentication functions
def generate_jwt_token(user_id, email):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=24),  # 24-hour expiration
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

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
        payload, error = verify_jwt_token(token)
        if error:
            return jsonify({'error': error}), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

def verify_password(stored_password_hash, provided_password):
    """Verify password against stored hash"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash.encode('utf-8'))

def find_user_by_email(email):
    """Find user by email address"""
    users_data = load_users()
    for user in users_data['users']:
        if user['email'].lower() == email.lower():
            return user
    return None

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
        
        # Generate verification token and send email
        verification_token = generate_verification_token(user_id, email)
        email_sent, email_message = send_verification_email(email, verification_token)
        
        if not email_sent:
            print(f"Warning: Failed to send verification email: {email_message}")
            # Still return success for registration, but note email issue
            return jsonify({
                'success': True,
                'message': 'User registered successfully, but verification email could not be sent. Please contact support.',
                'user_id': user_id,
                'email_sent': False
            }), 201
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'User registered successfully. Please check your email to verify your account.',
            'user_id': user_id,
            'email_sent': True
        }), 201
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

# Route: Email verification endpoint
@app.route('/api/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email using verification token"""
    try:
        # Validate the token
        token_info, error_message = validate_verification_token(token)
        
        if not token_info:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        # Load users and find the user
        users_data = load_users()
        user_found = False
        
        for user in users_data['users']:
            if user['id'] == token_info['user_id']:
                # Update user's email verification status
                user['email_verified'] = True
                user['email_verified_at'] = datetime.now().isoformat()
                user_found = True
                break
        
        if not user_found:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Save updated user data
        save_users(users_data)
        
        # Mark token as used
        mark_token_as_used(token)
        
        # Clean up expired tokens (optional)
        cleanup_expired_tokens()
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully! Your account is now active.',
            'user_id': token_info['user_id']
        }), 200
        
    except Exception as e:
        print(f"Email verification error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

# Route: User login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Check if required fields are present
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'error': 'Missing required fields: email, password'
            }), 400
        
        email = data['email'].strip()
        password = data['password']
        
        # Validate email format
        try:
            valid_email = validate_email(email)
            email = valid_email.email  # Normalized email
        except EmailNotValidError:
            return jsonify({
                'error': 'Invalid email format'
            }), 400
        
        # Find user by email
        user = find_user_by_email(email)
        if not user:
            return jsonify({
                'error': 'Invalid email or password'
            }), 401
        
        # Check if user's email is verified
        if not user.get('email_verified', False):
            return jsonify({
                'error': 'Please verify your email before logging in'
            }), 403
        
        # Verify password
        if not verify_password(user['password_hash'], password):
            return jsonify({
                'error': 'Invalid email or password'
            }), 401
        
        # Generate JWT token
        token = generate_jwt_token(user['id'], user['email'])
        
        # Return success response with token
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'email_verified': user['email_verified'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

# Route: User logout endpoint
@app.route('/api/logout', methods=['POST'])
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
        print(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

# Route: Protected user profile endpoint (example of using token_required decorator)
@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile():
    """Get current user's profile information"""
    try:
        user_id = request.current_user['user_id']
        
        # Find user by ID
        users_data = load_users()
        user = None
        for u in users_data['users']:
            if u['id'] == user_id:
                user = u
                break
        
        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404
        
        # Return user profile (excluding password hash)
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'email_verified': user['email_verified'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

# Run the app in development mode
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)