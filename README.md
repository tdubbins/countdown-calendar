# Countdown Calendar App

Create custom countdown calendars with video content. Upload videos for each day, share via unique links, and let recipients unlock doors daily.

**Note:** The hosted instance at calendar.hackcrew.de has been taken offline. Run it locally with Docker as shown below.

## Quick Start

```bash
# Clone and start with Docker
git clone https://github.com/tdubbins/countdown-calendar.git
cd countdown-calendar
cp .env.example .env
# Edit .env with your SMTP settings
docker-compose up -d
```

Open http://localhost

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and local development
- **[API Reference](docs/api.md)** - REST API endpoints

## Tech Stack

- **Frontend:** Ionic Vue, TypeScript
- **Backend:** Python Flask
- **Storage:** JSON files (per-calendar folders)
- **Video:** FFmpeg compression

## License

MIT
