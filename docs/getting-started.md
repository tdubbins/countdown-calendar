# Getting Started

## Prerequisites

- Docker Desktop, or:
- Python 3.9+, Node.js 18+, FFmpeg

## Setup

```bash
git clone https://github.com/tdubbins/countdown-calendar.git
cd countdown-calendar
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here

# Optional: SMTP for email verification (not required for dev)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=your-app-password
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Run with Docker (Recommended)

Start:
```bash
docker-compose up -d
```

Open http://localhost

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Runs at http://localhost:5001

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at http://localhost:8080

## Project Structure

```
countdown-calendar/
├── backend/           # Flask API
│   ├── app/
│   │   ├── routes/    # API endpoints
│   │   ├── services/  # Business logic
│   │   └── tasks/     # Video processing
│   └── data/          # JSON storage
├── frontend/          # Ionic Vue
│   └── src/
│       ├── views/     # Pages
│       ├── components/
│       └── composables/
└── docs/
```

## Common Tasks

### Email Verification (Dev)

Without SMTP configured, verification tokens are logged to the console.

View logs:
```bash
# Docker
docker-compose logs -f backend

# Local development
# Tokens appear in the terminal running the backend
```

Look for:
```
============================================================
[DEV] VERIFICATION EMAIL FOR: user@example.com
[DEV] TOKEN: abc123-...
[DEV] URL: http://localhost/verify-email/abc123-...
============================================================
```

Visit the URL to verify the account.

### Reset Database

```bash
rm -rf backend/data/*.json backend/data/calendars/
# Restart backend
```

### Run Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run test:unit
```
