# Flask Application Factory
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os


def rate_limit_error_handler(e):
    """Custom error handler for rate limiting - hide exact rate details"""
    return jsonify({'error': 'Too many requests. Please try again later.'}), 429


# Initialize rate limiter globally (will be bound to app in create_app)
limiter = Limiter(
    get_remote_address,
    default_limits=["500 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=False,
    on_breach=rate_limit_error_handler
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

    # Serve static frontend in production (single container deployment)
    if os.environ.get('SERVE_STATIC', 'false').lower() == 'true':
        static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            """Serve frontend SPA - static files or index.html for client routing"""
            if path and os.path.exists(os.path.join(static_folder, path)):
                return send_from_directory(static_folder, path)
            return send_from_directory(static_folder, 'index.html')

    return app