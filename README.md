# Countdown Calendar App

Create custom countdown calendars with video content. Upload videos for each day, share via unique links, and let recipients unlock doors daily.

**Live:** https://calendar.hackcrew.de

## Quick Start

```bash
# Clone and start with Docker
git clone https://github.com/tdubbins/countdown-calendar-app.git
cd countdown-calendar-app
cp .env.example .env
# Edit .env with your SMTP settings
docker-compose up -d
```

Open http://localhost

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and local development
- **[API Reference](docs/api.md)** - REST API endpoints
- **[Deployment](docs/deployment.md)** - Production setup with Docker & Caddy

## Tech Stack

- **Frontend:** Ionic Vue, TypeScript
- **Backend:** Python Flask
- **Storage:** JSON files (per-calendar folders)
- **Video:** FFmpeg compression

## License

MIT
