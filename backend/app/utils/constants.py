"""
Application Constants

Centralized constants for the Advent Calendar backend to ensure consistency
and make maintenance easier across the entire codebase.

Benefits:
- Single source of truth for configuration values
- Easy to update across the entire app
- Self-documenting code (names explain purpose)
- Prevents typos in repeated strings
- Easier testing with consistent values
"""

# HTTP Status Codes
class HTTPStatus:
    """Common HTTP status codes for API responses"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# Error Messages
class ErrorMessages:
    """Standardized error messages for consistency"""
    # Generic errors
    INTERNAL_ERROR = 'Internal server error'
    VALIDATION_ERROR = 'Validation failed'
    UNAUTHORIZED = 'Unauthorized access'
    NOT_FOUND = 'Resource not found'

    # Authentication errors
    INVALID_CREDENTIALS = 'Invalid email or password'
    EMAIL_EXISTS = 'Email already registered'
    WEAK_PASSWORD = 'Password does not meet requirements'
    PASSWORDS_DONT_MATCH = 'Passwords do not match'
    EMAIL_VERIFICATION_REQUIRED = 'Please verify your email first'
    INVALID_TOKEN = 'Invalid or expired token'

    # Calendar errors
    CALENDAR_NOT_FOUND = 'Calendar not found'
    CALENDAR_ACCESS_DENIED = 'You do not have access to this calendar'
    CALENDAR_ALREADY_SHARED = 'Calendar is already shared'
    INVALID_DATE_RANGE = 'Invalid date range'

    # Video errors
    VIDEO_NOT_FOUND = 'Video not found'
    VIDEO_TOO_LARGE = 'Video file is too large (max 50MB)'
    VIDEO_TOO_LONG = 'Video is too long (max 3 minutes)'
    INVALID_VIDEO_FORMAT = 'Invalid video format'
    VIDEO_UPLOAD_FAILED = 'Failed to upload video'

    # File storage errors
    FILE_NOT_FOUND = 'File not found'
    STORAGE_ERROR = 'Failed to store file'


# Success Messages
class SuccessMessages:
    """Standardized success messages"""
    # Authentication
    LOGIN_SUCCESS = 'Login successful'
    REGISTRATION_SUCCESS = 'Registration successful. Please check your email to verify your account.'
    EMAIL_VERIFIED = 'Email verified successfully'
    LOGOUT_SUCCESS = 'Logout successful'

    # Calendar operations
    CALENDAR_CREATED = 'Calendar created successfully'
    CALENDAR_UPDATED = 'Calendar updated successfully'
    CALENDAR_DELETED = 'Calendar deleted successfully'
    CALENDAR_SHARED = 'Calendar shared successfully'

    # Video operations
    VIDEO_UPLOADED = 'Video uploaded successfully'
    VIDEO_DELETED = 'Video deleted successfully'


# Validation Constants
class ValidationLimits:
    """Validation limits for various fields"""
    # Calendar
    MIN_CALENDAR_DAYS = 1
    MAX_CALENDAR_DAYS = 31
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 100

    # Video
    MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
    MAX_VIDEO_DURATION_SECONDS = 180  # 3 minutes
    ALLOWED_VIDEO_FORMATS = ['mp4', 'mov', 'avi', 'webm']
    ALLOWED_VIDEO_MIMES = [
        'video/mp4',
        'video/quicktime',
        'video/x-msvideo',
        'video/webm'
    ]

    # Authentication
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    EMAIL_MAX_LENGTH = 254

    # Rate limiting (NFR [S5])
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15


# File Storage Paths
class StoragePaths:
    """Centralized file storage paths"""
    DATA_DIR = 'data'
    CALENDARS_DIR = 'data/calendars'  # Per-calendar folder structure
    USERS_FILE = 'users.json'
    CALENDARS_FILE = 'calendars.json'
    TASKS_FILE = 'tasks.json'
    EMAIL_TOKENS_FILE = 'email_tokens.json'
    VIDEOS_DIR = 'videos'
    THUMBNAILS_DIR = 'thumbnails'


# Token Configuration
class TokenConfig:
    """JWT and email token configuration"""
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DAYS = 30
    EMAIL_TOKEN_EXPIRATION_HOURS = 24
    SHARE_TOKEN_LENGTH = 32


# Performance Constants (NFR [P1], [P2])
class Performance:
    """Performance-related constants"""
    MAX_CONCURRENT_USERS = 20
    MAX_VIDEO_PROCESSING_TIME = 300  # 5 minutes
    VIDEO_COMPRESSION_TARGET = 0.4  # Reduce to 40% of original
    BACKGROUND_TASK_POLL_INTERVAL = 2  # seconds


# Email Configuration
class EmailConfig:
    """Email sending configuration"""
    SENDER_EMAIL = 'noreply@adventcalendar.app'
    VERIFICATION_SUBJECT = 'Verify your email - Advent Calendar App'
    VERIFICATION_TEMPLATE = 'email_verification.html'


# Database/Storage Configuration
class StorageConfig:
    """JSON file storage configuration"""
    PRETTY_PRINT = True
    INDENT_SPACES = 2
    ENSURE_ASCII = False
    BACKUP_ENABLED = True
    MAX_BACKUP_COUNT = 5
