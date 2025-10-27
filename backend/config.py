# Configuration settings for Advent Calendar API
import os

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG') or True
    
    # Database settings (JSON file paths)
    USERS_DB = os.environ.get('USERS_DB') or 'data/users.json'
    CALENDARS_DB = os.environ.get('CALENDARS_DB') or 'data/calendars.json'
    TASKS_DB = os.environ.get('TASKS_DB') or 'data/tasks.json'
    EMAIL_TOKENS_DB = os.environ.get('EMAIL_TOKENS_DB') or 'data/email_tokens.json'
    
    # Video storage
    VIDEO_UPLOAD_FOLDER = os.environ.get('VIDEO_UPLOAD_FOLDER') or 'uploads/videos'
    MAX_VIDEO_SIZE = int(os.environ.get('MAX_VIDEO_SIZE') or 50 * 1024 * 1024)  # 50MB
    MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION') or 180)  # 3 minutes
    
    # Email settings (for verification)
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    
    # Flask-Mail configuration
    MAIL_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('SMTP_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_USER')
    
    # Application settings
    APP_NAME = 'Advent Calendar API'
    API_VERSION = '1.0.0'
    
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}