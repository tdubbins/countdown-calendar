# Countdown Calendar App - Concept Specification

## Overview

The Countdown Calendar App is a web-based platform that allows users to create custom countdown calendars with video content. Users can create calendars with 1-31 days, upload videos for specific days, customize the appearance and unlock behavior, and share their calendars publicly via direct links.

### Key Features

- User registration and authentication with email verification
- Multi-calendar management per user
- Video upload with automatic compression and thumbnail generation
- Flexible calendar duration (1-31 days)
- Date-based door unlocking mechanism
- Calendar publishing and sharing via direct UUID links (no share tokens)
- Permission-based access control (owner vs. visitor)
- Calendar state indicators (draft, upcoming, active, completed)
- Responsive design for mobile and desktop
- Progressive Web App capabilities

---

## User Roles

### Authenticated Users (Calendar Owners)
- Create multiple calendars
- Upload and manage videos
- Customize calendar settings (title, dates, theme, door order)
- Publish/unpublish calendars via chip-style toggle
- View calendar state indicators (draft, upcoming, active, completed)
- Access all doors regardless of date when viewing their own calendars
- Delete their own calendars

### Public Viewers (Visitors)
- View published calendars via direct UUID link
- Watch videos only when doors are unlocked (date-based)
- No account required
- Cannot modify calendars
- Read-only access with date restrictions

### Permission-Based Access Model
- **Owner access**: Full control, can open any door at any time
- **Visitor access**: Date-restricted, can only open doors when `current_date >= door_date`
- No share tokens required - access controlled by UUID and published status

---

## Data Architecture

### File System Structure

```
backend/
├── data/
│   ├── users.json                    # User accounts with calendar ownership
│   ├── email_tokens.json             # Email verification tokens
│   ├── tasks.json                    # Video processing task queue
│   └── calendars/                    # Per-calendar folders
│       ├── <calendar_uuid_1>/
│       │   ├── meta.json             # Calendar metadata
│       │   ├── videos/
│       │   │   ├── day_1.mp4
│       │   │   ├── day_2.mp4
│       │   │   └── ...
│       │   └── thumbnails/
│       │       ├── day_1_thumb.jpg
│       │       ├── day_2_thumb.jpg
│       │       └── ...
│       └── <calendar_uuid_2>/
│           ├── meta.json
│           ├── videos/
│           └── thumbnails/
```

### User Data Schema

**File:** `data/users.json`

```json
{
  "user_id": "uuid-v4",
  "email": "user@example.com",
  "password_hash": "bcrypt-hash",
  "email_verified": true,
  "calendar_ids": ["cal-uuid-1", "cal-uuid-2"],
  "created_at": "2025-11-13T10:00:00Z",
  "updated_at": "2025-11-13T10:00:00Z"
}
```

**Fields:**
- `user_id`: Unique UUID for user
- `email`: User's email address (unique)
- `password_hash`: Bcrypt hashed password
- `email_verified`: Boolean, true after email verification
- `calendar_ids`: Array of calendar UUIDs owned by this user
- `created_at`: ISO 8601 timestamp
- `updated_at`: ISO 8601 timestamp

### Calendar Metadata Schema

**File:** `data/calendars/<calendar_uuid>/meta.json`

```json
{
  "id": "calendar-uuid",
  "title": "My Advent Calendar",
  "duration": 24,
  "startDate": "2025-12-01",
  "endDate": "2025-12-24",
  "dateRange": "2025-12-01 to 2025-12-24",
  "status": "upcoming",
  "published": false,
  "doorOrder": "sequential",
  "doorPositions": null,
  "theme": "christmas",
  "timezone": "Europe/Berlin",
  "description": "A festive countdown to Christmas!",
  "videos": {
    "1": {
      "filename": "day_1.mp4",
      "thumbnail": "day_1_thumb.jpg",
      "size": 5242880,
      "duration": 45.2,
      "uploaded_at": "2025-11-13T10:00:00Z",
      "status": "completed"
    }
  },
  "videoCount": 1,
  "videoStorageUsed": 5242880,
  "createdAt": "2025-11-13T10:00:00Z",
  "updatedAt": "2025-11-13T10:00:00Z"
}
```

**Fields:**
- `id`: Calendar UUID (same as folder name)
- `title`: Calendar title (1-100 characters)
- `duration`: Number of days (1-31)
- `startDate`: Start date in YYYY-MM-DD format
- `endDate`: Calculated end date (startDate + duration - 1 days)
- `dateRange`: Human-readable date range string
- `status`: Calendar state - "draft", "upcoming", "active", or "completed"
- `published`: Boolean, controls public access via direct UUID link
- `doorOrder`: "sequential" or "random"
- `doorPositions`: Array of shuffled day numbers if doorOrder is "random"
- `theme`: Theme identifier (e.g., "christmas", "birthday")
- `timezone`: IANA timezone (e.g., "Europe/Berlin")
- `description`: Optional description text
- `videos`: Object mapping day numbers to video metadata
- `videoCount`: Total number of uploaded videos
- `videoStorageUsed`: Total bytes used by videos
- `createdAt`: ISO 8601 timestamp
- `updatedAt`: ISO 8601 timestamp

**Calendar Status States:**
- `draft`: Calendar not yet published, private to owner
- `upcoming`: Published calendar where start date is in the future
- `active`: Published calendar currently in progress (today is between start and end date)
- `completed`: Published calendar where end date has passed

---

## Authentication & Authorization

### Registration Flow

1. User submits email and password
2. Backend validates input and creates user account
3. Generates email verification token
4. Sends verification email
5. User clicks link to verify email
6. Account becomes active

### Login Flow

1. User submits email and password
2. Backend verifies credentials and email verification status
3. Generates JWT token with payload:
   ```json
   {
     "user_id": "uuid",
     "calendar_ids": ["cal-1", "cal-2"],
     "exp": 1234567890
   }
   ```
4. Frontend stores token in localStorage
5. Token included in Authorization header for authenticated requests

### Authorization Model

**Calendar Ownership:**
- User owns calendar if calendar_id is in user's `calendar_ids` array
- Ownership check performed by comparing JWT payload's `calendar_ids` with requested calendar_id

**Access Control:**
- **Published calendars:** Anyone can view (authentication optional)
- **Unpublished calendars:** Only owner can view
- **Modifications:** Only owner can modify (publish, upload, edit, delete)

---

## Calendar Management

### Creating a Calendar

1. Authenticated user submits calendar creation request
2. Backend generates calendar UUID
3. Creates folder: `data/calendars/<uuid>/`
4. Creates subfolders: `videos/`, `thumbnails/`
5. Creates `meta.json` with default values:
   - `published: false`
   - `status: "draft"`
   - `videoCount: 0`
   - `videos: {}`
6. Adds calendar UUID to user's `calendar_ids` array
7. Returns calendar data to frontend

### Updating a Calendar

**Editable fields:**
- `title`: Calendar title
- `duration`: Number of days (1-31)
- `startDate`: Start date
- `doorOrder`: "sequential" or "random"
- `doorPositions`: Shuffled positions for random order
- `theme`: Theme identifier
- `timezone`: IANA timezone
- `description`: Description text

**Restrictions:**
- Only owner can update
- Reducing duration does not delete videos, but they won't be visible

### Deleting a Calendar

1. Owner requests calendar deletion
2. Backend verifies ownership
3. Deletes entire folder: `data/calendars/<uuid>/`
4. Removes calendar UUID from user's `calendar_ids` array
5. All videos and thumbnails are permanently deleted

---

## Video Management

### Video Upload Flow

1. Owner selects video file and day number (1-31)
2. Frontend validates:
   - File type: MP4, WebM, MOV, AVI
   - File size: Max 50MB
   - Day number: Within calendar duration
3. Sends multipart/form-data to backend
4. Backend validates:
   - File type and size
   - Video duration: Max 3 minutes (using FFprobe)
   - Storage quota: 1GB per user
5. Saves temporary file
6. Creates background compression task
7. Returns immediately with status: "processing"
8. Background worker:
   - Compresses video using FFmpeg
   - Generates thumbnail at 2-second mark
   - Moves files to `data/calendars/<uuid>/videos/` and `/thumbnails/`
   - Updates `meta.json` with video metadata
   - Marks task as completed

### Video Deletion

1. Owner requests video deletion for specific day
2. Backend verifies ownership
3. Deletes video and thumbnail files
4. Removes entry from `meta.json` videos object
5. Updates `videoCount` and `videoStorageUsed`

### Video Streaming

**For Owners:**
- Direct access via: `GET /api/calendars/<id>/videos/<day>/stream`
- Requires authentication
- Returns MP4 file

**For Public Viewers (Visitors):**
- Access via: `GET /api/calendars/<id>/videos/<day>/stream`
- No authentication required if calendar is published
- Only returns video if:
  - Calendar is published
  - Day is unlocked (current_date >= door_date)
- Owner permission bypasses date restrictions

---

## Calendar Publishing & Sharing

### Publishing a Calendar

1. Owner clicks publish chip-style toggle in CalendarDetailPage
2. Backend sets `published: true` in `meta.json`
3. Backend calculates calendar `status` based on dates:
   - `upcoming`: start date in future
   - `active`: currently in date range
   - `completed`: end date has passed
4. Calendar becomes publicly accessible via direct UUID link
5. Owner can copy shareable link: `https://app.com/calendar/<uuid>`

### Unpublishing a Calendar

1. Owner clicks unpublish chip-style toggle in CalendarDetailPage
2. Backend sets `published: false` in `meta.json`
3. Backend sets `status: "draft"`
4. Calendar is no longer accessible to public
5. Only owner can view it (with full access to all doors)

### Sharing Mechanism (No Share Tokens)

- **Direct UUID sharing:** Calendar UUID is used directly in URL
- **URL format:** `/calendar/<calendar_uuid>` (no separate `/shared` route)
- **Security:** UUIDs are unguessable (2^122 possible values)
- **Access control:** `published` flag gates public access
- **Permission model:** Owner vs. visitor permissions determine door access
- **Copy to clipboard:** Frontend provides button to copy direct link

---

## Public Calendar Viewing

### Access Flow

1. User (authenticated or not) visits `/calendar/<uuid>`
2. Frontend sends GET request to `/api/calendars/<uuid>`
3. Backend checks:
   - Does calendar exist? → 404 if not
   - Is calendar published?
     - If YES → Allow access
     - If NO → Check authentication
       - If authenticated AND owner → Allow access
       - Otherwise → 404 (don't reveal existence)
4. Backend response includes:
   - Calendar metadata
   - Array of days with unlock status
   - `isOwner` flag (true if authenticated user owns calendar)
5. Frontend renders calendar:
   - Shows title, description, duration
   - Renders door grid in specified order (sequential or random)
   - Shows locked/unlocked state for each door
   - If owner: Shows owner controls

### Door Unlock Logic (Permission-Based)

**Owner Permission:**
- Owners can access **all doors at any time** regardless of date
- Determined by checking if authenticated user's ID matches calendar owner
- No date restrictions for calendar creators
- Enables testing and preview without affecting visitor experience

**Visitor Permission (Date-Based):**
- Visitors can only access doors when date conditions are met
- Each day unlocks at midnight in the calendar's timezone
- Day 1 unlocks on `startDate`
- Day 2 unlocks on `startDate + 1 day`
- Day N unlocks on `startDate + (N-1) days`
- Past days remain accessible

**Algorithm:**
```
For each day D:
  IF isOwner is true:
    RETURN unlocked (owner has full access)
  ELSE:
    unlock_date = startDate + (D-1) days
    current_date = now() in calendar.timezone
    RETURN current_date >= unlock_date (visitor date-restricted)
```

### Video Playback

1. Viewer clicks unlocked door
2. Frontend checks unlock status
3. If unlocked:
   - Fetches video from `/api/calendars/<id>/videos/<day>/stream`
   - Opens video modal with HTML5 player
   - Displays video with controls
4. If locked:
   - Shows "This door will unlock on [date]" message
5. Tracks opened state in localStorage (frontend only)

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | No | Register new user |
| GET | `/api/auth/verify-email/<token>` | No | Verify email address |
| POST | `/api/auth/login` | No | Login and get JWT token |
| POST | `/api/auth/logout` | Yes | Logout (client-side) |
| GET | `/api/auth/profile` | Yes | Get user profile |

### Calendar Management Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/calendars` | Yes | List user's calendars |
| POST | `/api/calendars` | Yes | Create new calendar |
| GET | `/api/calendars/<id>` | Optional | Get calendar by ID (public if published) |
| PUT | `/api/calendars/<id>` | Yes | Update calendar (owner only) |
| DELETE | `/api/calendars/<id>` | Yes | Delete calendar (owner only) |
| POST | `/api/calendars/<id>/publish` | Yes | Publish calendar (owner only) |
| POST | `/api/calendars/<id>/unpublish` | Yes | Unpublish calendar (owner only) |

### Video Management Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/calendars/<id>/videos` | Yes | List all videos (owner only) |
| POST | `/api/calendars/<id>/videos` | Yes | Upload video (owner only) |
| GET | `/api/calendars/<id>/videos/<day>` | Yes | Get video metadata (owner only) |
| GET | `/api/calendars/<id>/videos/<day>/status` | Yes | Get processing status (owner only) |
| GET | `/api/calendars/<id>/videos/<day>/stream` | Optional | Stream video (public if published & unlocked) |
| GET | `/api/calendars/<id>/videos/<day>/thumbnail` | Optional | Get thumbnail (public if published & unlocked) |
| DELETE | `/api/calendars/<id>/videos/<day>` | Yes | Delete video (owner only) |

---

## Frontend Routes

| Path | Component | Auth Required | Description |
|------|-----------|---------------|-------------|
| `/` | HomePage | No | Landing page with login/register |
| `/register` | RegisterPage | No | User registration form |
| `/login` | LoginPage | No | User login form |
| `/verify-email/:token` | EmailVerificationPage | No | Email verification handler |
| `/dashboard` | DashboardPage | Yes | User dashboard with calendar list |
| `/calendar/create` | CalendarCreatePage | Yes | Create new calendar form |
| `/calendar/:id/detail` | CalendarDetailPage | Yes | Calendar management (owner view) |
| `/calendar/:id` | SharedCalendarPage | No | Public calendar viewer (unified route for all access) |

---

## Security Model

### Access Control Summary

**Calendars:**
- Published calendar + Valid UUID → Public access
- Unpublished calendar + Owner authenticated → Owner access
- Unpublished calendar + Not owner → 404 (no information leakage)
- Invalid UUID → 404

**Videos:**
- Published calendar + Unlocked day → Public access
- Published calendar + Locked day → 403 Forbidden
- Unpublished calendar → Owner-only access (authentication required)

### UUID Security

- Calendar IDs are UUID v4 (128-bit random)
- Probability of guessing: 1 in 2^122 ≈ 5.3 × 10^36
- Effectively impossible to enumerate calendars
- No sequential IDs that could be guessed

### Authentication Security

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with expiration
- Email verification required before login
- HTTPS enforced in production
- Rate limiting on public endpoints (20-30 req/min)

### Privacy Considerations

- Unpublished calendars return 404 (not 403) to prevent information disclosure
- Calendar existence should not be revealed to non-owners
- User email addresses not exposed in API responses
- Video files only accessible if calendar is published and day is unlocked

---

## User Workflows

### Workflow 1: Create and Share Calendar

1. User registers account and verifies email
2. Logs in to dashboard
3. Clicks "Create Calendar"
4. Fills form: title, duration, start date, theme
5. Submits → Calendar created (unpublished)
6. Redirected to calendar detail page
7. Uploads videos for various days
8. Waits for video processing to complete
9. Customizes door order (sequential or random)
10. Clicks "Publish Calendar"
11. Clicks "Copy Share Link"
12. Shares link with friends/family via email, social media, etc.

### Workflow 2: View Published Calendar

1. Viewer receives link: `https://app.com/calendar/<uuid>`
2. Clicks link (no login required)
3. Sees calendar with door grid
4. Locked doors show countdown timer
5. Unlocked doors show thumbnail
6. Clicks unlocked door → Video plays in modal
7. Can watch all unlocked videos
8. Returns each day to see new unlocked content

### Workflow 3: Owner Testing Calendar

1. Owner creates and uploads videos to calendar
2. Publishes calendar via chip-style toggle
3. Visits public calendar URL (`/calendar/:id`)
4. Automatically has owner permissions - all doors unlocked
5. Tests each video works correctly
6. Visitor viewing same calendar only sees date-unlocked doors
7. Owner shares link with viewers (visitors get date-restricted access)

### Workflow 4: Unpublish Calendar

1. Owner realizes they need to fix something
2. Visits calendar detail page (`/calendar/:id/detail`)
3. Clicks unpublish chip-style toggle
4. Calendar status changes to "draft"
5. Calendar becomes private (only owner can access)
6. Public viewers get 404 if they try to access
7. Owner can still view and edit with full permissions
8. Makes changes (uploads new videos, edits title, etc.)
9. Clicks publish chip-style toggle again when ready

---

## Non-Functional Requirements

### Performance
- Application load time: < 5 seconds
- Calendar rendering: < 3 seconds
- Video upload processing: Background (returns immediately)
- Video streaming: Progressive download (no full buffering required)

### Scalability
- Support 10-20 simultaneous users (Phase 2 scope)
- 1GB storage quota per user
- Max 50MB per video file
- Max 3 minutes per video

### Usability
- Responsive design: 320px+ screen width
- Touch-friendly: 44px+ touch targets
- WCAG 2.1 AA accessibility compliance
- PWA installable on mobile devices

### Reliability
- Graceful error handling with user-friendly messages
- Video processing failures logged and reported
- Automatic retry for transient failures
- Data persistence with JSON file storage

### Security
- HTTPS in production
- Password hashing with bcrypt
- JWT token expiration
- Input validation and sanitization
- Rate limiting on public endpoints
- XSS and SQL injection prevention

---

## Technology Stack

### Backend
- **Framework:** Python Flask
- **Authentication:** JWT with bcrypt
- **Database:** JSON file-based storage
- **Video Processing:** FFmpeg (compression, thumbnail generation)
- **Task Queue:** Custom JSON-based task queue
- **Rate Limiting:** Flask-Limiter

### Frontend
- **Framework:** Ionic Vue (Progressive Web App)
- **Language:** TypeScript
- **State Management:** Vue Composition API
- **HTTP Client:** Fetch API
- **Icons:** Ionicons
- **Video Player:** HTML5 Video Element

### Infrastructure
- **Development:** Local Flask server + Vite dev server
- **Production:** Docker containers with Nginx reverse proxy
- **Hosting:** Self-hosted (Hetzner Cloud planned)
- **Storage:** Filesystem-based (per-calendar folders)

---

## Future Enhancements (Out of Scope)

- Real-time notifications when doors unlock
- Social features (comments, reactions)
- Multiple themes with custom styling
- Audio-only calendars
- Collaboration (multiple owners per calendar)
- Analytics (view counts, engagement metrics)
- Email reminders for door unlocks
- Custom domain support
- Database migration (PostgreSQL/MongoDB)
- CDN integration for video delivery
- Mobile native apps (iOS/Android)

---

## Glossary

**Calendar:** A collection of days (1-31) with optional video content that unlocks progressively based on dates.

**Door:** Visual representation of a single day in the calendar. Can be locked or unlocked.

**Unlock Logic:** Date-based algorithm that determines when each door becomes accessible.

**Published:** State where a calendar is publicly accessible via its UUID link.

**Owner:** Authenticated user who created and owns a calendar.

**Viewer:** Anyone accessing a published calendar (may or may not be authenticated).

**meta.json:** JSON file containing all metadata for a specific calendar.

**Door Order:** Display arrangement of doors (sequential 1,2,3... or random shuffled positions).

**UUID:** Universally Unique Identifier (128-bit random value used for calendar IDs).

**Permission-Based Access:** Access control model where owners get full access and visitors get date-restricted access.

---

## Document Version

**Version:** 2.0
**Date:** November 13, 2025
**Status:** Updated Specification (Removed allDoorsOpen, added permission-based access)
**Author:** Project Team

## Changelog

### Version 2.0 (November 13, 2025)
- **Removed:** `allDoorsOpen` toggle feature and backend field
- **Added:** Permission-based access control (owner vs. visitor)
- **Added:** Calendar status states (draft, upcoming, active, completed)
- **Added:** Chip-style publish/unpublish toggle in UI
- **Changed:** Simplified sharing mechanism (no share tokens, direct UUID access)
- **Changed:** Unified calendar viewing route (`/calendar/:id` for all access)
- **Removed:** Separate `/shared` route (consolidated into single route)
- **Updated:** Door unlock logic to use owner permission checks instead of flags
