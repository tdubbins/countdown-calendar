# Countdown Calendar App

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org)
[![Ionic](https://img.shields.io/badge/Ionic-7.0-blue.svg)](https://ionicframework.com)

A web-based Progressive Web App for creating custom countdown calendars with video content. Users can create personalized calendars with 1-31 doors, upload videos for each day, and share them via unique links with date-based unlocking for recipients.

**Academic Project** - IU International University of Applied Sciences
Course: Project: Software Engineering (DLMCSPSE01)

## Features

- **User Authentication** - Registration with email verification, JWT-based sessions
- **Flexible Calendars** - Create calendars with 1-31 days, custom date ranges
- **Video Management** - Upload videos (max 3 min, 1GB) with automatic compression and thumbnail generation
- **Private Sharing** - UUID-based links for sharing without requiring recipient accounts
- **Date-Based Unlocking** - Doors unlock daily for visitors; owners have full preview access
- **Calendar States** - Draft, upcoming, active, and completed status tracking
- **Responsive Design** - Mobile-first PWA with touch-friendly interface
- **Theme Support** - Multiple visual themes for calendar presentation

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Ionic Vue 7.0, TypeScript, Vue 3 Composition API |
| **Backend** | Python Flask 3.1, RESTful API |
| **Database** | JSON file-based storage (distributed per-calendar) |
| **Authentication** | JWT tokens, bcrypt password hashing |
| **Video Processing** | FFmpeg with background task queue |
| **Deployment** | Docker, Nginx reverse proxy |

## Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 16+** with npm
- **FFmpeg** installed and available in PATH

### Installation

```bash
# Clone the repository
git clone https://github.com/tdubbins/countdown-calendar-app.git
cd countdown-calendar-app

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration (see backend/README.md)

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.development
```

### Running Locally

```bash
# Terminal 1: Start backend (from backend/)
source venv/bin/activate
python run.py
# API runs at http://localhost:5001

# Terminal 2: Start frontend (from frontend/)
npm run serve
# App runs at http://localhost:8080
```

### Test Credentials

For development testing:
- **Email**: test@gmail.com
- **Password**: TestPass123

## Project Structure

```
countdown-calendar-app/
├── backend/                 # Flask REST API
│   ├── app/
│   │   ├── routes/         # API endpoints (auth, calendars, health)
│   │   ├── services/       # Business logic
│   │   ├── tasks/          # Background job processing
│   │   ├── utils/          # Helpers (auth, video, validation)
│   │   └── templates/      # Email templates
│   ├── data/               # JSON storage files
│   ├── config.py           # Configuration management
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Ionic Vue PWA
│   ├── src/
│   │   ├── views/          # Page components
│   │   ├── components/     # Reusable UI components
│   │   ├── composables/    # Vue composition functions
│   │   ├── router/         # Vue Router configuration
│   │   ├── theme/          # Theming system
│   │   └── utils/          # Helper functions
│   └── public/             # Static assets
│
├── docs/                   # Documentation
│   ├── CONCEPT_SPEC.md     # System architecture
│   └── calendar_schema.md  # Data model reference
│
└── docker-compose.yml      # Container orchestration
```

## Documentation

- **[Concept Specification](docs/CONCEPT_SPEC.md)** - Complete system architecture and design
- **[Calendar Schema](docs/calendar_schema.md)** - Data model documentation
- **[Backend README](backend/README.md)** - API setup and endpoints
- **[Frontend README](frontend/README.md)** - UI development guide

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User authentication |
| `/api/auth/verify-email` | GET | Email verification |
| `/api/calendars` | GET/POST | List/create calendars |
| `/api/calendars/<id>` | GET/PUT/DELETE | Calendar CRUD |
| `/api/calendars/<id>/videos` | POST | Upload video |
| `/api/calendars/<id>/days/<day>` | PUT | Assign video to day |
| `/api/calendars/shared/<id>` | GET | Public calendar access |
| `/api/health` | GET | Service health check |

See [backend/README.md](backend/README.md) for complete API documentation.

## Development

### Branch Workflow

```bash
git checkout main && git pull origin main
git checkout -b feature/description
# Make changes, commit
git push origin feature/description
# Create Pull Request on GitHub
```

### Code Quality

- Backend: Python with type hints, modular architecture
- Frontend: TypeScript strict mode, Vue Composition API
- Accessibility: WCAG 2.1 AA compliance target

## Deployment

### Docker (Recommended)

```bash
docker-compose up -d
```

See deployment documentation for production configuration with Nginx and SSL.

## Project Status

- **Phase 1** (Conception): Completed - October 2025
- **Phase 2** (Development): Completed - November 2025
- **Phase 3** (Finalization): In Progress - Due November 26, 2025

### Implemented Features (Epics 1-4)
- User management with email verification
- Calendar creation and management
- Video upload with compression
- Private sharing with date-based unlocking

### Planned Enhancements (Epics 5-7)
- Additional themes and customization
- Bulk video upload
- Password reset and profile management

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Tina Dubbins**
Master of Computer Science - IU International University of Applied Sciences
Student ID: IU14092559
