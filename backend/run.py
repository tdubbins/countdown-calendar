# Main Application Entry Point
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application
# Worker starts automatically via app/__init__.py:start_worker()
app = create_app()

if __name__ == '__main__':
    # Use environment-based debug setting (defaults to False for safety)
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=debug, host='0.0.0.0', port=port)