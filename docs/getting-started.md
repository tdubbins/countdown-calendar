# Getting Started

## Prerequisites

- Docker Desktop, or:
- Python 3.9+, Node.js 18+, FFmpeg

## Docker (Recommended)

```bash
git clone https://github.com/tdubbins/countdown-calendar-app.git
cd countdown-calendar-app
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=your-app-password
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

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
cp .env.example .env
# Edit .env
python run.py
```

Runs at http://localhost:5001

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.development
npm run serve
```

Runs at http://localhost:8080

## Test Account

- **Email:** test@gmail.com
- **Password:** TestPass123

## Project Structure

```
countdown-calendar-app/
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
