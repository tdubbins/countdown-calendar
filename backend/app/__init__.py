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
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp
    from app.routes.calendar import calendar_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(calendar_bp, url_prefix='/api')
    
    return app