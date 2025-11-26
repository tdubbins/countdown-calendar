# Backend - Flask REST API

Python Flask backend providing RESTful API endpoints for the Countdown Calendar App.

## Prerequisites

- **Python 3.9+**
- **FFmpeg** - Required for video processing
  ```bash
  # macOS
  brew install ffmpeg

  # Ubuntu/Debian
  sudo apt install ffmpeg

  # Windows
  # Download from https://ffmpeg.org/download.html and add to PATH
  ```

## Installation

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
```

## Configuration

Edit `.env` with your settings:

```env
# Flask
SECRET_KEY=your-secure-secret-key
DEBUG=True
FLASK_ENV=development

# Email (SMTP)
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
EMAIL_USER=noreply@yourdomain.com
EMAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=Calendar App <noreply@yourdomain.com>
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# URLs (auto-detected in development)
# FRONTEND_URL=http://localhost:8080
# BACKEND_URL=http://localhost:5001
```

See `.env.example` for all available options.

## Running the Server

```bash
# Development mode
python run.py

# Server runs at http://localhost:5001
```

## Test Credentials

Pre-configured test account for development:
- **Email**: test@gmail.com
- **Password**: TestPass123
- **Status**: Verified

## Project Structure

```
backend/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   ├── calendar.py     # Calendar & video routes
│   │   ├── user.py         # User profile routes
│   │   └── health.py       # Health check routes
│   ├── services/           # Business logic
│   │   ├── calendar_service.py
│   │   ├── user_service.py
│   │   └── video_service.py
│   ├── tasks/              # Background processing
│   │   ├── queue.py        # Task queue manager
│   │   └── video_tasks.py  # Video compression tasks
│   ├── utils/              # Helper modules
│   │   ├── auth.py         # JWT utilities
│   │   ├── video.py        # FFmpeg operations
│   │   ├── validation.py   # Input validation
│   │   └── constants.py    # Application constants
│   └── templates/          # Email templates
├── data/                   # JSON storage
│   ├── users.json          # User accounts
│   ├── tasks.json          # Background task queue
│   ├── email_tokens.json   # Verification tokens
│   └── calendars/          # Per-calendar folders
│       └── {id}/
│           ├── meta.json   # Calendar metadata
│           ├── videos/     # Video files
│           └── thumbnails/ # Generated thumbnails
├── tests/                  # Test suites
├── config.py               # Configuration management
├── run.py                  # Application entry point
└── requirements.txt        # Python dependencies
```

## API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Register new user | No |
| GET | `/api/auth/verify-email/<token>` | Verify email address | No |
| POST | `/api/auth/resend-verification` | Resend verification email | No |
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/logout` | User logout | Yes |
| GET | `/api/auth/profile` | Get current user profile | Yes |

### User Management

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| PUT | `/api/users/profile` | Update user profile | Yes |
| PUT | `/api/users/password` | Change password | Yes |
| DELETE | `/api/users/account` | Delete account | Yes |

### Calendars

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/calendars` | List user's calendars | Yes |
| POST | `/api/calendars` | Create new calendar | Yes |
| GET | `/api/calendars/<id>` | Get calendar details | Yes* |
| PUT | `/api/calendars/<id>` | Update calendar | Yes |
| DELETE | `/api/calendars/<id>` | Delete calendar | Yes |
| POST | `/api/calendars/<id>/publish` | Publish calendar | Yes |
| POST | `/api/calendars/<id>/unpublish` | Unpublish calendar | Yes |

*Public calendars accessible without auth via shared link

### Videos

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/calendars/<id>/videos` | Upload video | Yes |
| GET | `/api/calendars/<id>/videos` | List all videos | Yes* |
| GET | `/api/calendars/<id>/videos/<day>` | Get video for day | Yes* |
| GET | `/api/calendars/<id>/videos/<day>/status` | Get processing status | Yes |
| GET | `/api/calendars/<id>/videos/<day>/thumbnail` | Get thumbnail | Yes* |
| GET | `/api/calendars/<id>/videos/<day>/stream` | Stream video | Yes* |
| DELETE | `/api/calendars/<id>/videos/<day>` | Delete video | Yes |
| POST | `/api/calendars/<id>/videos/reassign` | Reassign video to day | Yes |

*Public access for published calendars (date-restricted for visitors)

### Health

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/health` | Service health check | No |
| GET | `/api/` | API root | No |

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Request Header
```
Authorization: Bearer <token>
```

### Token Lifecycle
- Tokens are returned on successful login
- Include token in Authorization header for protected routes
- Tokens expire after configured duration

## Error Responses

Standard error format:
```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `413` - Payload Too Large (file size exceeded)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Video Processing

Videos are processed asynchronously:

1. **Upload** - Video saved to temporary location
2. **Queue** - Compression task added to queue
3. **Process** - FFmpeg compresses video (target: 720p, H.264)
4. **Thumbnail** - First frame extracted as thumbnail
5. **Complete** - Video moved to permanent storage

Check processing status via `/api/calendars/<id>/videos/<day>/status`

## Rate Limiting

Public endpoints are rate-limited:
- Shared calendar access: 60 requests/minute
- Video streaming: 30 requests/minute

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_auth.py
```

## Development Tips

### Debug Mode
Set `DEBUG=True` in `.env` for:
- Detailed error messages
- Auto-reload on code changes
- Debug toolbar

### Logging
Logs are written to stdout with structured format:
```
[2025-11-14 10:30:00] INFO: Request received: POST /api/auth/login
```

### Database Reset
To reset JSON databases:
```bash
rm -rf data/*.json data/calendars/
# Restart server to recreate empty databases
```
