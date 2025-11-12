"""
Structured Logging Utility

Provides consistent, structured logging across the backend application.
Replaces scattered print() calls with a centralized logging system.

Benefits:
- Consistent log format across the app
- Log levels for filtering (DEBUG, INFO, WARNING, ERROR)
- Structured data for easier debugging
- Can be configured per environment
- Easy to integrate with log aggregation services
- Performance insights with timestamps
- Context-rich error reporting

Usage:
    from app.utils.logger import logger

    logger.info("User logged in", extra={"user_id": user_id, "email": email})
    logger.error("API call failed", extra={"endpoint": "/api/calendars", "error": str(error)})
    logger.debug("Processing video", extra={"video_id": video_id, "size": file_size})
"""

import logging
import sys
from typing import Any, Optional
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.
    Makes it easier to parse and analyze logs programmatically.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, 'extra') and record.extra:
            log_data['data'] = record.extra

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors for console output.
    Makes logs easier to read during development.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Build log message
        log_parts = [
            f"{timestamp}",
            f"{color}{record.levelname:8}{reset}",
            f"{record.module}.{record.funcName}:{record.lineno}",
            f"{record.getMessage()}"
        ]

        message = " | ".join(log_parts)

        # Add extra data if present
        if hasattr(record, 'extra') and record.extra:
            message += f"\n  Data: {json.dumps(record.extra, indent=2)}"

        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class CustomAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that allows passing structured data.
    Makes it easy to add context to log messages.
    """

    def process(self, msg: str, kwargs: dict) -> tuple:
        """Process log message and extract extra data"""
        extra = kwargs.pop('extra', {})
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra']['extra'] = extra
        return msg, kwargs


def setup_logger(
    name: str = 'advent_calendar',
    level: int = logging.INFO,
    use_json: bool = False
) -> logging.Logger:
    """
    Set up and configure logger with appropriate handlers.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (useful for production)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Set formatter based on environment
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = ColoredFormatter()

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


# Create default logger instance
# Use INFO level by default, can be configured via environment variable
import os
log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_str, logging.INFO)
use_json_logs = os.getenv('LOG_FORMAT', 'colored').lower() == 'json'

_logger = setup_logger(level=log_level, use_json=use_json_logs)
logger = CustomAdapter(_logger, {})


# Convenience functions for common logging patterns

def log_request(method: str, endpoint: str, status_code: int, duration_ms: float):
    """Log HTTP request with structured data"""
    logger.info(
        f"{method} {endpoint} - {status_code}",
        extra={
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration_ms': duration_ms
        }
    )


def log_error(error: Exception, context: Optional[dict] = None):
    """Log error with exception details"""
    logger.error(
        f"Error occurred: {str(error)}",
        exc_info=True,
        extra=context or {}
    )


def log_api_call(endpoint: str, method: str, success: bool, duration_ms: float = 0):
    """Log API call with details"""
    level = logger.info if success else logger.error
    level(
        f"API call: {method} {endpoint}",
        extra={
            'endpoint': endpoint,
            'method': method,
            'success': success,
            'duration_ms': duration_ms
        }
    )


def log_video_processing(video_id: str, action: str, status: str, details: Optional[dict] = None):
    """Log video processing events"""
    logger.info(
        f"Video {action}: {video_id} - {status}",
        extra={
            'video_id': video_id,
            'action': action,
            'status': status,
            **(details or {})
        }
    )


def log_auth_event(event: str, user_id: Optional[str] = None, email: Optional[str] = None, success: bool = True):
    """Log authentication events"""
    level = logger.info if success else logger.warning
    level(
        f"Auth event: {event}",
        extra={
            'event': event,
            'user_id': user_id,
            'email': email,
            'success': success
        }
    )
