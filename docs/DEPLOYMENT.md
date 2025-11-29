# Production Deployment Guide

This guide covers deploying the Countdown Calendar App using the integrated Docker image.

## Overview

The application uses a **single Docker image** that combines both frontend and backend:

```
┌─────────────────────────────────────────────┐
│           Integrated Container              │
│  ┌───────────────────────────────────────┐  │
│  │  Flask (Gunicorn)        Port 5001    │  │
│  │  ├── /api/*    → REST API routes      │  │
│  │  └── /*        → Static frontend      │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │  /app/static/  (built Ionic Vue app)  │  │
│  │  /app/data/    (JSON storage + videos)│  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Image Structure

```
/app/
├── app/                    # Flask application
│   ├── __init__.py         # App factory + static serving
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── tasks/              # Background worker
│   └── utils/              # Helpers
├── static/                 # Built frontend (from npm build)
│   ├── index.html          # SPA entry point
│   ├── js/                 # Compiled JavaScript
│   ├── css/                # Compiled styles
│   └── assets/             # Images, fonts
├── data/                   # Persistent storage (mount as volume!)
│   ├── users.json          # User accounts
│   ├── tasks.json          # Task queue
│   ├── email_tokens.json   # Verification tokens
│   └── calendars/          # Calendar data + videos
│       └── {uuid}/
│           ├── meta.json
│           ├── videos/
│           └── thumbnails/
├── config.py               # Flask configuration
├── run.py                  # Application entry point
└── requirements.txt        # Python dependencies
```

## Build

```bash
# From project root
docker build -t countdown-calendar .
```

Build stages:
1. **Stage 1 (node:18-alpine)**: Builds frontend with `npm run build`
2. **Stage 2 (python:3.11-slim)**: Sets up backend, copies built frontend to `/app/static`

## Configuration

### Step 1: Create Environment File

Create a `.env` file in your project root:

```bash
cp .env.example .env
```

### Step 2: Configure Variables

Edit `.env` with your settings:

```env
# =============================================================================
# Application Settings (REQUIRED)
# =============================================================================
SECRET_KEY=your-secure-random-string-min-32-chars
FLASK_ENV=production

# =============================================================================
# Email Configuration (REQUIRED for user verification)
# =============================================================================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
MAIL_USE_SSL=true
MAIL_USE_TLS=false
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Generating a Secure SECRET_KEY

```bash
# Option 1: Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Option 2: OpenSSL
openssl rand -hex 32
```

### Gmail App Password Setup

If using Gmail for email:
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate a new app password for "Mail"
4. Use this 16-character password as `EMAIL_PASSWORD`

### SSL vs TLS

| Port | Setting |
|------|---------|
| 465 | `MAIL_USE_SSL=true`, `MAIL_USE_TLS=false` |
| 587 | `MAIL_USE_SSL=false`, `MAIL_USE_TLS=true` |

## Run

```bash
docker run --rm \
  --name countdown-app \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  countdown-calendar
```

Access the application at `http://localhost:5001`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | JWT signing key (use strong random value) |
| `FLASK_ENV` | No | `production` | Environment mode |
| `SERVE_STATIC` | No | `true` | Enable frontend serving (set in Dockerfile) |
| `SMTP_SERVER` | Yes* | - | SMTP server hostname |
| `SMTP_PORT` | No | `465` | SMTP port |
| `EMAIL_USER` | Yes* | - | SMTP username |
| `EMAIL_PASSWORD` | Yes* | - | SMTP password |
| `MAIL_USE_SSL` | No | `true` | Enable SSL (use with port 465) |
| `MAIL_USE_TLS` | No | `false` | Enable TLS (use with port 587) |

*Required for email verification functionality

## Data Persistence

**Important**: Mount `/app/data` as a volume to persist:
- User accounts
- Calendar metadata
- Uploaded videos
- Thumbnails

```bash
# Create data directory on host
mkdir -p ./data

# Run with volume mount
docker run -v $(pwd)/data:/app/data ...
```

## Reverse Proxy (Nginx)

For production with SSL, use Nginx as reverse proxy:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 1100M;  # For video uploads (max 1GB + overhead)

    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts for large uploads
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }
}
```

## Docker Compose (Optional)

For easier management with Nginx:

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: countdown-app
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    expose:
      - "5001"

  nginx:
    image: nginx:alpine
    container_name: countdown-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - app
```

## Health Check

Verify the application is running:

```bash
# Health endpoint
curl http://localhost:5001/health

# Expected response
{"status": "healthy"}
```

## Logs

```bash
# View logs
docker logs countdown-app

# Follow logs
docker logs -f countdown-app
```

## Troubleshooting

### Container won't start
```bash
# Check logs for errors
docker logs countdown-app

# Common issues:
# - Missing required environment variables
# - Port 5001 already in use
# - Permission issues with data volume
```

### Videos not processing
- Ensure FFmpeg is available (included in image)
- Check `/app/data` has write permissions
- Monitor logs for task queue errors

### Frontend not loading
- Verify `SERVE_STATIC=true` is set
- Check that `/app/static/index.html` exists in container:
  ```bash
  docker exec countdown-app ls -la /app/static/
  ```

### Email not sending
- Verify SMTP credentials
- Check if SMTP port is not blocked
- For Gmail: use App Password, not regular password
