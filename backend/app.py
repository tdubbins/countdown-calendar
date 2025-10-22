# Basic Flask application for Advent Calendar backend
from flask import Flask, jsonify
from config import config
import os

# Create Flask application instance
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

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

# Run the app in development mode
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)