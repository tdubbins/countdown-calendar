# Flask Application Factory
from flask import Flask
from flask_cors import CORS
from config import config
import os

def create_app(config_name=None):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # Initialize extensions
    CORS(app)

    # Initialize upload directories for video storage
    from app.utils.storage import ensure_upload_directories
    ensure_upload_directories()

    # Start background worker for task processing (NFR [P2]: Processing starts within 5 seconds)
    from app.tasks import start_worker
    start_worker()

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp
    from app.routes.calendar import calendar_bp
    from app.routes.shared import shared_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(calendar_bp, url_prefix='/api')
    app.register_blueprint(shared_bp, url_prefix='/api')  # Public endpoints for shared calendars

    return app