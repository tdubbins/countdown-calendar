# Flask Application Factory
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os

# Initialize rate limiter globally (will be bound to app in create_app)
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True
)

def create_app(config_name=None):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # Configure CORS with allowed origins from environment
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8080').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })

    # Bind rate limiter to this application instance
    limiter.init_app(app)

    # Initialize upload directories for video storage
    from app.utils.storage import ensure_upload_directories
    ensure_upload_directories()

    # Start background worker for task processing
    from app.tasks import start_worker
    start_worker()

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp
    from app.routes.calendar import calendar_bp
    from app.routes.user import user_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(calendar_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')

    return app