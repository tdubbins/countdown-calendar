# Countdown Calendar App - Documentation

This directory contains comprehensive documentation for the Countdown Calendar App project.

## Documentation Files

### [CONCEPT_SPEC.md](CONCEPT_SPEC.md)
Complete system specification including:
- System overview and architecture
- User roles and permissions
- Data schemas and file structure
- Authentication and authorization model
- Calendar management workflows
- Video upload and streaming
- Publishing and sharing mechanism
- API endpoints documentation
- Security model
- Non-functional requirements
- Technology stack details

**Version:** 2.0 (Updated November 13, 2025)

**Key Updates in v2.0:**
- Removed `allDoorsOpen` toggle feature
- Added permission-based access control (owner vs. visitor)
- Added calendar status states (draft, upcoming, active, completed)
- Simplified sharing (direct UUID, no share tokens)
- Unified calendar viewing route

### [calendar_schema.md](calendar_schema.md)
Detailed data model documentation for calendar metadata structure.

## Quick Links

- [Main README](../README.md)
- [Backend Code](../backend/)
- [Frontend Code](../frontend/advent-calendar-frontend/)

## Architecture Changes (Version 2.0)

### Removed Features
- ❌ `allDoorsOpen` toggle button and backend field
- ❌ Share token system
- ❌ Separate `/shared` route

### Added Features
- ✅ Permission-based access control
- ✅ Calendar status indicators
- ✅ Chip-style publish/unpublish toggle
- ✅ Unified calendar viewing route (`/calendar/:id`)

### Access Control Model

**Owner Access:**
- Full access to all doors regardless of date
- Determined by JWT authentication and calendar ownership
- Can test and preview calendar before sharing

**Visitor Access:**
- Date-restricted access to doors
- Doors unlock based on `current_date >= door_date`
- No authentication required for published calendars

## For Developers

When implementing new features:
1. Update CONCEPT_SPEC.md with architectural changes
2. Document data model changes in calendar_schema.md
3. Follow the permission-based access control pattern
4. Maintain separation between owner and visitor permissions
