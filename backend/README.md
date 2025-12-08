# Backend

Flask REST API.

## Setup

```bash
# Install FFmpeg first
brew install ffmpeg  # macOS
# or: sudo apt install ffmpeg

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
python run.py
# http://localhost:5001
```

## Test

```bash
pytest
pytest --cov=app
```

## Structure

```
app/
├── routes/      # API endpoints
├── services/    # Business logic
├── tasks/       # Video processing queue
└── utils/       # Helpers
data/
├── users.json
├── tasks.json
└── calendars/   # Per-calendar folders
```

See [API Reference](../docs/api.md) for endpoints.
