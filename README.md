# Countdown Calendar App

University Project for the course "Project: Software Engineering (DLMCSPSE01)" at IU International University of Applied Sciences.

## Overview

A web-based Progressive Web App where users can create custom countdown calendars with video content behind each door. Calendars can be shared publicly via direct links, with date-based unlocking for visitors and full access for calendar owners.

## Key Features

- 🔐 User authentication with email verification
- 📅 Create calendars with 1-31 days duration
- 🎥 Upload videos with automatic compression and thumbnail generation
- 🎨 Customizable themes and door ordering (sequential or random)
- 🔗 Direct UUID-based sharing (no share tokens needed)
- 🚪 Permission-based access control:
  - **Owners**: Full access to all doors at any time
  - **Visitors**: Date-restricted access (doors unlock daily)
- 📊 Calendar status indicators (draft, upcoming, active, completed)
- 📱 Responsive design with PWA support
- 🎯 Chip-style publish/unpublish toggle

## Technology Stack

### Backend
- Python Flask with modular architecture
- JSON file-based storage
- JWT authentication with bcrypt
- FFmpeg for video processing
- Custom background task queue

### Frontend
- Ionic Vue (Progressive Web App)
- TypeScript
- Vue Composition API
- HTML5 Video Player

## Documentation

- **[Concept Specification](docs/CONCEPT_SPEC.md)** - Complete system architecture and specifications
- **[Calendar Schema](docs/calendar_schema.md)** - Data model documentation

## Project Status

- **Phase 1**: ✅ Completed & Submitted (October 21, 2025)
- **Phase 2**: 🔄 In Progress (Due: November 14, 2025)
- **Current Epic**: Calendar Management & Video Upload

## Architecture Highlights

### Permission-Based Access Control
The system uses a clean permission model instead of feature flags:
- Calendar owners get unrestricted access to all doors
- Visitors can only access doors based on date conditions
- No separate "test mode" or "all doors open" toggles needed

### Direct UUID Sharing
- Calendars are shared via direct UUID links
- No share token system required
- Published calendars are publicly accessible via UUID
- Unpublished calendars return 404 to non-owners

### Calendar States
- **Draft**: Unpublished calendar, owner-only access
- **Upcoming**: Published, start date in future
- **Active**: Published, currently within date range
- **Completed**: Published, end date has passed

## License

Academic project for educational purposes.
