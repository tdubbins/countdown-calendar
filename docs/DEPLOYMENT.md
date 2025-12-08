# Production Deployment Guide

This guide covers deploying the Countdown Calendar App to a Linux server with Docker, systemd, and Caddy.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    calendar.hackcrew.de                      │
├─────────────────────────────────────────────────────────────┤
│  Caddy (Reverse Proxy)                                       │
│  - Automatic HTTPS via Let's Encrypt                         │
│  - Proxies to localhost:${PORT}                              │
├─────────────────────────────────────────────────────────────┤
│  systemd (countdown-app.service)                             │
│  - Manages Docker container lifecycle                        │
│  - Auto-restart on failure                                   │
│  - Starts on boot                                            │
├─────────────────────────────────────────────────────────────┤
│  Docker Container (ghcr.io/tdubbins/countdown-calendar-app)  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Flask + Gunicorn (Port 5001)                           │ │
│  │  ├── /api/*  → REST API                                 │ │
│  │  └── /*      → Static frontend (Ionic Vue)              │ │
│  └─────────────────────────────────────────────────────────┘ │
│  Volume: /opt/calendar-data → /app/data                      │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Linux server (Ubuntu 22.04+ recommended)
- Docker installed
- Caddy installed
- Domain pointed to server IP

## Server Configuration

| Setting | Value |
|---------|-------|
| Timezone | UTC (Europe/London) |
| SSH | Key-only (password disabled) |
| Firewall | Ports 22, 80, 443 open |

## Server Setup

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker
```

### 2. Install Caddy

```bash
apt install -y caddy
systemctl enable caddy
```

### 3. Create Data Directory

```bash
mkdir -p /opt/calendar-data
```

### 4. Create Environment File

```bash
cat > /root/.env << 'EOF'
# Email Configuration
SMTP_SERVER=smtp.yourprovider.com
SMTP_PORT=465
EMAIL_USER=noreply@yourdomain.com
EMAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
MAIL_USE_TLS=False
MAIL_USE_SSL=True

# Application Environment
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Application Port
PORT=5001

# Data Storage Path
DATA_PATH=/opt/calendar-data
EOF
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Create Systemd Service

```bash
cat > /etc/systemd/system/countdown-app.service << 'EOF'
[Unit]
Description=Countdown Calendar App
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=5

EnvironmentFile=/root/.env

ExecStartPre=-/usr/bin/docker stop countdown-app
ExecStartPre=-/usr/bin/docker rm countdown-app

ExecStart=/usr/bin/docker run --rm \
    --name countdown-app \
    -p 127.0.0.1:${PORT}:5001 \
    -v ${DATA_PATH}:/app/data \
    -e SECRET_KEY=${SECRET_KEY} \
    -e FLASK_ENV=${FLASK_ENV} \
    -e SMTP_SERVER=${SMTP_SERVER} \
    -e SMTP_PORT=${SMTP_PORT} \
    -e EMAIL_USER=${EMAIL_USER} \
    -e EMAIL_PASSWORD=${EMAIL_PASSWORD} \
    -e MAIL_DEFAULT_SENDER=${MAIL_DEFAULT_SENDER} \
    -e MAIL_USE_SSL=${MAIL_USE_SSL} \
    -e MAIL_USE_TLS=${MAIL_USE_TLS} \
    ghcr.io/tdubbins/countdown-calendar-app:latest

ExecStop=/usr/bin/docker stop countdown-app

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable countdown-app
```

### 6. Configure Caddy

Create systemd drop-in for Caddy to read PORT from .env:

```bash
mkdir -p /etc/systemd/system/caddy.service.d
cat > /etc/systemd/system/caddy.service.d/env.conf << 'EOF'
[Service]
EnvironmentFile=/root/.env
EOF
```

Configure Caddyfile:

```bash
cat > /etc/caddy/Caddyfile << 'EOF'
{
    email admin@yourdomain.com
}

calendar.yourdomain.com {
    reverse_proxy localhost:{$PORT}

    log {
        output file /var/log/caddy/access.log
    }
}
EOF

systemctl daemon-reload
systemctl restart caddy
```

### 7. Pull and Start

```bash
docker pull ghcr.io/tdubbins/countdown-calendar-app:latest
systemctl start countdown-app
```

## Management Scripts

### /root/calendar.sh

```bash
cat > /root/calendar.sh << 'EOF'
#!/bin/bash
SERVICE="countdown-app"

case "$1" in
    start)
        echo "Starting $SERVICE..."
        systemctl start $SERVICE
        systemctl status $SERVICE --no-pager | head -5
        ;;
    stop)
        echo "Stopping $SERVICE..."
        systemctl stop $SERVICE
        echo "Stopped."
        ;;
    restart)
        echo "Restarting $SERVICE..."
        systemctl restart $SERVICE
        sleep 2
        systemctl status $SERVICE --no-pager | head -5
        ;;
    status)
        systemctl status $SERVICE --no-pager
        ;;
    logs)
        journalctl -u $SERVICE -f
        ;;
    logs-tail)
        journalctl -u $SERVICE -n 50 --no-pager
        ;;
    config)
        ${EDITOR:-nano} /root/.env
        ;;
    edit)
        ${EDITOR:-nano} /etc/systemd/system/countdown-app.service
        echo "Run: systemctl daemon-reload && ./calendar.sh restart"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|logs-tail|config|edit}"
        exit 1
        ;;
esac
EOF
chmod +x /root/calendar.sh
```

### /root/caddy.sh

```bash
cat > /root/caddy.sh << 'EOF'
#!/bin/bash
SERVICE="caddy"

case "$1" in
    start)
        echo "Starting $SERVICE..."
        systemctl start $SERVICE
        systemctl status $SERVICE --no-pager | head -5
        ;;
    stop)
        echo "Stopping $SERVICE..."
        systemctl stop $SERVICE
        echo "Stopped."
        ;;
    restart)
        echo "Restarting $SERVICE..."
        systemctl restart $SERVICE
        sleep 2
        systemctl status $SERVICE --no-pager | head -5
        ;;
    reload)
        echo "Reloading $SERVICE config..."
        systemctl reload $SERVICE
        echo "Reloaded."
        ;;
    status)
        systemctl status $SERVICE --no-pager
        ;;
    logs)
        journalctl -u $SERVICE -f
        ;;
    logs-tail)
        journalctl -u $SERVICE -n 50 --no-pager
        ;;
    config)
        cat /etc/caddy/Caddyfile
        ;;
    edit)
        ${EDITOR:-nano} /etc/caddy/Caddyfile
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload|status|logs|logs-tail|config|edit}"
        exit 1
        ;;
esac
EOF
chmod +x /root/caddy.sh
```

## CI/CD Deployment

### Deployer User Setup

Create a restricted user for automated deployments:

```bash
# Create user
useradd -m -s /bin/bash deployer
usermod -aG docker deployer

# Create deploy directory
mkdir -p /opt/deploy
chown deployer:deployer /opt/deploy

# Configure sudo access (restricted to service management)
cat > /etc/sudoers.d/deployer << 'EOF'
deployer ALL=(root) NOPASSWD: /usr/bin/systemctl restart countdown-app
deployer ALL=(root) NOPASSWD: /usr/bin/systemctl status countdown-app *
deployer ALL=(root) NOPASSWD: /usr/bin/systemctl status countdown-app
deployer ALL=(root) NOPASSWD: /usr/bin/systemctl start countdown-app
deployer ALL=(root) NOPASSWD: /usr/bin/systemctl stop countdown-app
EOF
chmod 440 /etc/sudoers.d/deployer
```

### Deploy Script

```bash
cat > /opt/deploy/deploy.sh << 'EOF'
#!/bin/bash
set -euo pipefail

LOG_FILE="/var/log/countdown-deploy.log"
DOCKER_IMAGE="ghcr.io/tdubbins/countdown-calendar-app:latest"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Starting deployment ==="

log "Pulling Docker image: $DOCKER_IMAGE"
if ! docker pull "$DOCKER_IMAGE" 2>&1 | tee -a "$LOG_FILE"; then
    log "ERROR: Failed to pull Docker image"
    exit 1
fi

log "Restarting countdown-app service..."
if ! sudo systemctl restart countdown-app 2>&1 | tee -a "$LOG_FILE"; then
    log "ERROR: Failed to restart service"
    exit 1
fi

sleep 3
if systemctl is-active --quiet countdown-app; then
    log "Service is running"
else
    log "ERROR: Service failed to start"
    sudo systemctl status countdown-app --no-pager | tee -a "$LOG_FILE"
    exit 1
fi

log "Cleaning up old Docker images..."
docker image prune -f 2>&1 | tee -a "$LOG_FILE" || true

log "=== Deployment completed successfully ==="
EOF
chown deployer:deployer /opt/deploy/deploy.sh
chmod +x /opt/deploy/deploy.sh
```

### GitHub Actions Integration

Add SSH key for deployer user and create workflow:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: calendar.hackcrew.de
          username: deployer
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: /opt/deploy/deploy.sh
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | JWT signing key (min 32 chars) |
| `FLASK_ENV` | No | `production` | Environment mode |
| `PORT` | No | `5001` | Application port |
| `DATA_PATH` | No | `/opt/calendar-data` | Data storage path |
| `SMTP_SERVER` | Yes* | - | SMTP server hostname |
| `SMTP_PORT` | No | `465` | SMTP port |
| `EMAIL_USER` | Yes* | - | SMTP username |
| `EMAIL_PASSWORD` | Yes* | - | SMTP password |
| `MAIL_USE_SSL` | No | `True` | Enable SSL (port 465) |
| `MAIL_USE_TLS` | No | `False` | Enable TLS (port 587) |

*Required for email verification functionality

## Health Check

```bash
# Local check
curl http://localhost:5001/api/health

# Via domain
curl https://calendar.hackcrew.de/api/health

# Expected response
{"status":"healthy","environment":"production","message":"Countdown Calendar API","version":"1.0.0"}
```

## Troubleshooting

### Check Service Status
```bash
./calendar.sh status
./caddy.sh status
```

### View Logs
```bash
./calendar.sh logs      # Follow app logs
./caddy.sh logs         # Follow Caddy logs
```

### Container Issues
```bash
# Check if container is running
docker ps

# Check container logs directly
docker logs countdown-app

# Inspect container
docker inspect countdown-app
```

### Email Not Sending
- Verify SMTP credentials in `/root/.env`
- Test SMTP connectivity: `openssl s_client -connect smtp.server.com:465`
- Check application logs for email errors

### Permission Issues
```bash
# Fix data directory permissions
chown -R root:root /opt/calendar-data
chmod -R 755 /opt/calendar-data
```

## Security Notes

- SSH password authentication is disabled (key-only)
- Deployer user has restricted sudo access
- Application runs on localhost only (Caddy handles external traffic)
- Caddy provides automatic HTTPS via Let's Encrypt
- SECRET_KEY should be unique and never committed to git
