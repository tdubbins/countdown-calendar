# Configuration settings for Advent Calendar API
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database settings (JSON file paths)
    USERS_DB = os.environ.get('USERS_DB') or 'data/users.json'
    CALENDARS_DB = os.environ.get('CALENDARS_DB') or 'data/calendars.json'
    TASKS_DB = os.environ.get('TASKS_DB') or 'data/tasks.json'
    EMAIL_TOKENS_DB = os.environ.get('EMAIL_TOKENS_DB') or 'data/email_tokens.json'
    
    # Video settings (storage paths now in StoragePaths constants)
    MAX_VIDEO_SIZE = int(os.environ.get('MAX_VIDEO_SIZE') or 50 * 1024 * 1024)  # 50MB
    MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION') or 180)  # 3 minutes
    
    # Email configuration - Consolidated and cleaned
    EMAIL_CONFIG = {
        'server': os.environ.get('SMTP_SERVER'),
        'port': int(os.environ.get('SMTP_PORT', 465)),
        'username': os.environ.get('EMAIL_USER'),
        'password': os.environ.get('EMAIL_PASSWORD'),
        'sender': os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('EMAIL_USER'),
        'use_ssl': os.environ.get('MAIL_USE_SSL', 'True').lower() == 'true',
        'use_tls': os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true',
        'timeout': 30
    }
    
    # Application URLs - No fallbacks, must be explicitly set
    FRONTEND_URL = (
        os.environ.get('FRONTEND_URL') or
        ('https://yourdomain.com' if os.environ.get('FLASK_ENV') == 'production' 
         else 'http://localhost:8080')
    )
    BACKEND_URL = os.environ.get('BACKEND_URL')
    
    # Application settings
    APP_NAME = 'Advent Calendar API'
    API_VERSION = '1.0.0'
    
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    def __init__(self):
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY environment variable must be set in production")

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}