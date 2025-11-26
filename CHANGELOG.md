# Changelog

All notable changes to the Countdown Calendar App are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Comprehensive dark mode support for all UI components (#112)
- Drag-and-drop video reassignment between calendar days (#110)
- User profile management with display name editing (#109)
- Resend verification email functionality (#108)
- Help page with feature documentation (#106, #111)

### Changed
- Updated documentation for new features and account management

## [1.0.0] - 2025-11-14

Phase 2 Development Complete - Full feature implementation.

### Added
- **Theming System**
  - Birthday theme with balloons and confetti effects (#105)
  - Christmas theme with snowflakes and festive design (#104)
  - Theme selector on calendar detail page (#96)

- **Video Playback**
  - 3D door opening animation with video modal (#101)
  - Autoplay on video playback
  - Friendly message with gift icon for days without video (#107)

- **Calendar Management**
  - Calendar description field (#99)
  - Door ordering toggle (sequential/random) (#95)
  - Calendar status indicators (draft, upcoming, active, completed)
  - Permission-based access control for owners vs visitors (#97)

- **Sharing System**
  - UUID-based direct sharing links
  - Public shared calendar viewer with responsive grid (#93)
  - Rate limiting on public endpoints (#90)
  - Share modal with auto-generated links (#91)

- **Infrastructure**
  - Dynamic API config with mobile support (#102)
  - Structured logging for frontend and backend
  - Centralized constants files

### Changed
- Simplified architecture: Removed allDoorsOpen toggle in favor of permission-based access (#97)
- Improved calendar header with European date format
- Enhanced UX with native Ionic components (#100)
- Optimized CalendarCard performance (#99)

### Removed
- Share token system (replaced with direct UUID sharing)
- Separate `/shared` route (unified calendar viewing)

## [0.2.0] - 2025-10-21

Phase 1 Conception Complete - Core functionality.

### Added
- **User Management**
  - User registration with email validation
  - Email verification system with token-based confirmation
  - Login/logout with JWT authentication
  - Password hashing with bcrypt

- **Calendar Creation**
  - Calendar creation form (title, duration 1-31 days, dates)
  - Calendar storage in distributed JSON structure
  - Calendar management dashboard
  - Day-by-day calendar interface
  - Calendar editing capabilities

- **Video Upload**
  - Video upload with FFmpeg compression
  - Background task queue for asynchronous processing
  - Video assignment to calendar days
  - Upload progress indicators
  - Thumbnail generation

### Technical
- Flask backend with modular blueprint architecture
- Ionic Vue frontend with TypeScript
- JWT authentication middleware
- CORS configuration for cross-origin requests

## [0.1.0] - 2025-10-01

Project initialization.

### Added
- Initial project structure
- Backend Flask application skeleton
- Frontend Ionic Vue application skeleton
- Development environment configuration
- Git repository setup with GitHub integration
