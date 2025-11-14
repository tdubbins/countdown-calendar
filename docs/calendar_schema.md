# Calendar Database Schema Documentation

This document defines the calendar data structure for the Advent Calendar App database.

## Database File
- **Location**: `backend/data/calendars.json`
- **Collection Name**: `calendars`
- **Database Instance**: `calendars_db` (from `app.utils.json_db`)

## Schema Structure

### Calendar Object
```json
{
  "calendars": {
    "calendar-uuid-here": {
      "id": "string (UUID)",
      "title": "string (required, 1-100 chars)",
      "startDate": "string (ISO date: YYYY-MM-DD)",
      "duration": "number (1-31 days)",
      "endDate": "string (calculated: startDate + duration)",
      "dateRange": "string (display: 'YYYY-MM-DD to YYYY-MM-DD')",
      "videoCount": "number (0-duration, count of uploaded videos)",
      "status": "string (draft|active|completed)",
      "shareToken": "string (UUID for sharing links)",
      "createdAt": "string (ISO datetime)",
      "updatedAt": "string (ISO datetime)",
      "userId": "string (UUID, references users.json)",
      "videoStorageUsed": "number (bytes, for NFR [SC2] tracking)",
      "videos": {
        "1": {
          "day": 1,
          "fileName": "string",
          "filePath": "string",
          "uploadedAt": "string (ISO datetime)",
          "processed": "boolean",
          "fileSize": "number (bytes)"
        }
      }
    }
  }
}
```

## Field Definitions

### Core Fields
- **id**: Unique identifier (UUID v4)
- **title**: Calendar display name (user-defined)
- **startDate**: First day of calendar (YYYY-MM-DD format)
- **duration**: Number of days (1-31, user-selected)
- **endDate**: Last day (auto-calculated: startDate + duration - 1)

### Status Management
- **status**: 
  - `draft` - Being created/edited
  - `active` - Published and shareable
  - `completed` - Past end date (automatically determined)

### Sharing & Security
- **shareToken**: Unique UUID for private sharing links
- **userId**: Associates calendar with owner (references users collection)

### Video Management (Epic 3 Support)
- **videoCount**: Current number of uploaded videos
- **videoStorageUsed**: Total bytes used (NFR [SC2]: 1GB limit per user)
- **videos**: Object mapping day numbers to video metadata

### Audit Trail
- **createdAt**: Calendar creation timestamp
- **updatedAt**: Last modification timestamp

## Non-Functional Requirements Compliance

### [SC1] User Database Capacity
- **Structure**: Object-based storage with UUID keys
- **Scalability**: Supports 100+ calendars efficiently
- **Indexing**: Fast user-based queries via `list_by_field()`

### [SC2] Video Storage Tracking
- **Field**: `videoStorageUsed` tracks total bytes per calendar
- **Aggregation**: Sum per user across all calendars for 1GB limit
- **Granularity**: Individual video file sizes in `videos` object

### [SC3] Modular Architecture
- **Separation**: Calendar data isolated from users/email_tokens
- **File**: Dedicated `calendars.json` file
- **Instance**: Separate `calendars_db` database instance

## Database Operations

### Supported Operations
```python
# Create calendar
calendars_db.create("calendars", calendar_id, calendar_data)

# Find by ID
calendars_db.find_by_id("calendars", calendar_id)

# List user's calendars
calendars_db.list_by_field("calendars", "userId", user_id)

# Update calendar
calendars_db.update("calendars", calendar_id, updates)

# Delete calendar
calendars_db.delete("calendars", calendar_id)
```

### Query Patterns
- **User Calendars**: `list_by_field("calendars", "userId", user_id)`
- **Active Calendars**: `list_by_field("calendars", "status", "active")`
- **Share Token Lookup**: `find_by_field("calendars", "shareToken", token)`

## Example Calendar Record
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Christmas Countdown 2025",
  "startDate": "2025-12-01",
  "duration": 25,
  "endDate": "2025-12-25",
  "dateRange": "2025-12-01 to 2025-12-25",
  "videoCount": 12,
  "status": "active",
  "shareToken": "share-token-uuid-here",
  "createdAt": "2025-10-28T16:30:00.000Z",
  "updatedAt": "2025-11-15T14:22:00.000Z",
  "userId": "d0739ad6-fa0a-4720-972a-8c754a85bd91",
  "videoStorageUsed": 524288000,
  "videos": {
    "1": {
      "day": 1,
      "fileName": "day1_intro.mp4",
      "filePath": "uploads/videos/user_id/calendar_id/day1_intro.mp4",
      "uploadedAt": "2025-11-01T10:00:00.000Z",
      "processed": true,
      "fileSize": 45678900
    }
  }
}
```

## Integration Notes

### Frontend TypeScript Interface
- Matches `Calendar` interface in `src/types/calendar.ts`
- Compatible with `CalendarCreateData` for form submission
- Supports `CalendarSummary` for dashboard display

### API Endpoints
- POST `/api/calendars` - Create calendar
- GET `/api/calendars` - List user calendars  
- GET `/api/calendars/:id` - Get calendar details
- PUT `/api/calendars/:id` - Update calendar
- DELETE `/api/calendars/:id` - Delete calendar

---

**Created for Issue #22**: Calendar JSON database file and model  
**NFR Compliance**: [SC1], [SC2], [SC3]  
**Last Updated**: 2025-10-28