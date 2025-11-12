# Sharing Feature Design Documentation

**Epic 4 & Epic 5: Calendar Sharing Feature**
**Date**: November 11, 2025
**Phase**: Phase 2 - Development/Reflection Phase
**Author**: Design discussions with Tina

---

## Table of Contents
1. [Overview](#overview)
2. [Epic Structure](#epic-structure)
3. [Design Decisions Summary](#design-decisions-summary)
4. [Data Model Changes](#data-model-changes)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [User Flows](#user-flows)
8. [Visual Design Specifications](#visual-design-specifications)
9. [Technical Implementation Details](#technical-implementation-details)
10. [Non-Functional Requirements](#non-functional-requirements)
11. [Implementation Workflow](#implementation-workflow)
12. [Future Enhancements](#future-enhancements)

---

## Overview

The Calendar Sharing feature enables users to share their countdown calendars via secure, unique links. Recipients can view shared calendars without creating an account, with days unlocking based on the calendar's start date and timezone.

### Key Features
- **Secure share link generation** with UUID tokens
- **Public calendar viewer** (no authentication required)
- **Daily unlock mechanism** based on calendar start date (Berlin timezone)
- **Customizable door ordering** (sequential or random)
- **Theme selection** (Christmas theme for Phase 2)
- **Video playback** with autoplay and fullscreen
- **Rate limiting** to prevent abuse
- **Festive Christmas theme** with images and decorations

---

## Epic Structure

### Epic 4: Core Sharing Functionality (Must-Have)
**Goal**: Deliver working share functionality with basic viewer

**Scope**:
- Share token generation and management
- Public API endpoints with rate limiting
- Share modal with copy-to-clipboard
- Public viewer with responsive door grid
- Basic door states (locked, unlocked, opened)
- Daily unlock logic (Berlin timezone)
- Error handling for invalid/deleted calendars
- LocalStorage tracking for opened doors

### Epic 5: Advanced Sharing Features (Polish & Enhancement)
**Goal**: Enhanced user experience with customization and visual polish

**Scope**:
- Random door ordering with preview
- Theme selection UI (single Christmas theme)
- Preview functionality (opens in new tab)
- Door opening animations
- Festive Christmas styling with images
- Video modal with autoplay and fullscreen

---

## Design Decisions Summary

### 1. Share Token Generation
- **Decision**: Generate token when user clicks "Share" button (lazy generation)
- **Token Format**: UUID v4 (e.g., `a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6`)
- **Storage**: `share_token` field in `calendars.json`
- **Privacy**: Token can be null (calendar not shared yet)
- **Rationale**: Privacy by default, only create tokens when needed

### 2. Unshare Mechanism
- **Decision**: Delete calendar is the only way to stop sharing (Phase 2)
- **Future**: Add "Revoke Link" feature in Phase 3
- **Rationale**: Simple scope, intuitive user understanding

### 3. Creator Information
- **Decision**: Shared calendars are anonymous (no creator info shown)
- **Rationale**: No user profile system yet, better privacy

### 4. Rate Limiting
- **Decision**: Include basic IP-based rate limiting in Epic 4
- **Implementation**: Flask-Limiter library
- **Limits**:
  - `GET /api/shared/<token>`: 20 requests/minute per IP
  - `GET /api/shared/<token>/day/<day>`: 30 requests/minute per IP
  - Default limit: 200 requests/hour per IP
- **Future**: Advanced rate limiting (token-based throttling) in separate issue
- **Rationale**: Minimal effort, prevents basic abuse, protects public endpoints

### 5. Timezone Handling
- **Decision**: Hardcode Europe/Berlin timezone for unlock logic (Phase 2)
- **Unlock Logic**: Days unlock at midnight Berlin time
- **Future**: Viewer-based timezone unlocking in separate issue
- **Rationale**: Simple, consistent experience for all viewers

### 6. Daily Unlock Logic
- **Formula**: `current_date >= start_date + (day_number - 1)`
- **Example**:
  - Calendar starts Dec 1, 2025
  - Day 1 unlocks: Dec 1, 00:00 Berlin time
  - Day 2 unlocks: Dec 2, 00:00 Berlin time
  - Day 24 unlocks: Dec 24, 00:00 Berlin time
- **Future Days**: Show as locked (visible but not clickable)
- **Past Days**: All remain accessible (can rewatch)

### 7. Shared Calendar Data Privacy
- **Show**: Calendar title, all door numbers, total duration
- **Hide**: Creator info, start date (privacy concern)
- **Future**: Add optional calendar description field (separate issue)

### 8. Door Numbering & Ordering
- **Decision**: Support both sequential and random ordering
- **Configuration**: Set during calendar creation
- **Sequential**: Doors numbered 1-N in order
- **Random**: Doors shuffled using stored `door_positions` array
- **Shuffle Control**: User can click "Shuffle Again" to regenerate
- **Storage**: `door_order` (enum) and `door_positions` (array) in calendar data
- **Rationale**: Mimics real advent calendars, adds playfulness

### 9. Theme Selection
- **Decision**: Theme selected during calendar creation
- **Phase 2**: Single "Christmas" theme (hardcoded)
- **UI**: Dropdown menu (for future expandability)
- **Storage**: `theme` field in calendar data
- **Future**: Multiple themes (birthday, holiday, custom) in Phase 3
- **Rationale**: Prepares architecture for future themes

### 10. Preview Functionality
- **Decision**: Preview opens shared view in new tab
- **URL**: `/shared/<share_token>?preview=true` (optional parameter)
- **Behavior**: Shows actual rendered calendar as recipients see it
- **Location**: Preview button in share modal
- **Rationale**: User sees real experience, no duplicate components needed

### 11. Video Thumbnails
- **Decision**: Reuse existing thumbnail generation code
- **Implementation**: Auto-generate during video upload with FFmpeg
- **Storage**: Same pattern as existing video thumbnails
- **Rationale**: Consistent with existing architecture

### 12. Mobile Navigation
- **Decision**: No home button for shared calendar viewers
- **Rationale**: Viewers are not logged in, no homepage exists for them

### 13. Video Download Protection
- **Decision**: Block download with HTML5 `controlsList` attribute
- **Implementation**: `<video controlsList="nodownload">`
- **Rationale**: Discourages casual downloading, simple to implement

### 14. Error Handling
- **Scenarios**: Invalid token, deleted calendar, backend down
- **UI**: Friendly error page with message and CTA
- **Include in**: Issue #32 (public viewer implementation)

### 15. Opened Doors Tracking
- **Decision**: LocalStorage per browser
- **Key Format**: `calendar_${shareToken}_opened`
- **Data**: Array of opened day numbers `[1, 2, 3]`
- **Behavior**: Not synced across devices, respects privacy
- **Rationale**: Simple, works offline, no backend tracking needed

### 16. Loading States
- **Decision**: Implement in future issue (not Epic 4/5)
- **Rationale**: Nice-to-have, can be added after core functionality

### 17. Share URL Format
- **Decision**: `/shared/:token` (simple, RESTful)
- **Example**: `https://advent-app.com/shared/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6`
- **Rationale**: Clear it's a shared view, consistent with API naming

### 18. Christmas Theme
- **Decision**: Go festive with images (no emojis)
- **Colors**: Red (#c41e3a), Green (#165b33), Gold (#ffd700)
- **Images**: Separate issue for sourcing/implementing decorative images
- **Rationale**: Professional, accessible, festive feel

---

## Data Model Changes

### Updated Calendar Schema

```json
{
  "id": "cal_abc123",
  "user_id": "user_xyz789",
  "title": "My Advent Calendar 2025",
  "start_date": "2025-12-01",
  "duration": 24,
  "timezone": "Europe/Berlin",
  "created_at": "2025-11-10T10:30:00Z",

  // NEW FIELDS FOR SHARING
  "share_token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",  // null if not shared
  "door_order": "random",                                  // "sequential" | "random"
  "door_positions": [3, 1, 24, 2, 15, ...],               // shuffled array if random
  "theme": "christmas",                                    // "christmas" for Phase 2

  "days": [
    {
      "day_number": 1,
      "video_path": "/uploads/user_xyz789/cal_abc123/day_1.mp4",
      "thumbnail_path": "/uploads/user_xyz789/cal_abc123/day_1_thumb.jpg"
    }
    // ... more days
  ]
}
```

### Field Specifications

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `share_token` | string (UUID) | No | `null` | Unique share token, generated on demand |
| `door_order` | enum | Yes | `"sequential"` | Door ordering: "sequential" or "random" |
| `door_positions` | array[int] | No | `null` | Shuffled door positions if random, null if sequential |
| `theme` | string | Yes | `"christmas"` | Theme identifier for styling |
| `timezone` | string | Yes | `"Europe/Berlin"` | IANA timezone for unlock logic |

---

## Backend Architecture

### New API Endpoints

#### 1. Generate Share Token (Authenticated)
```
POST /api/calendars/<calendar_id>/generate-share-token
Headers: Authorization: Bearer <jwt_token>

Response 200:
{
  "success": true,
  "share_token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "share_url": "https://advent-app.com/shared/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
}

Response 404: Calendar not found
Response 403: Not calendar owner
```

#### 2. Get Shared Calendar (Public, Rate Limited)
```
GET /api/shared/<share_token>
Rate Limit: 20 requests/minute per IP

Response 200:
{
  "success": true,
  "calendar": {
    "title": "My Advent Calendar",
    "duration": 24,
    "door_order": "random",
    "door_positions": [3, 1, 24, ...],
    "theme": "christmas",
    "days": [
      {
        "day_number": 1,
        "is_unlocked": true,
        "thumbnail_url": "/uploads/.../day_1_thumb.jpg"
      },
      {
        "day_number": 2,
        "is_unlocked": false,
        "thumbnail_url": null
      }
      // ... all days with unlock status
    ]
  }
}

Response 404: Invalid share token
Response 429: Rate limit exceeded
```

#### 3. Get Shared Calendar Day Video (Public, Rate Limited)
```
GET /api/shared/<share_token>/day/<day_number>
Rate Limit: 30 requests/minute per IP

Response 200:
{
  "success": true,
  "day_number": 1,
  "is_unlocked": true,
  "video_url": "/uploads/.../day_1.mp4",
  "thumbnail_url": "/uploads/.../day_1_thumb.jpg"
}

Response 403: Day is locked
Response 404: Day not found or invalid token
Response 429: Rate limit exceeded
```

### Backend Unlock Logic

```python
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def is_day_unlocked(calendar: dict, day_number: int) -> bool:
    """
    Determine if a specific day is unlocked based on current time.

    Args:
        calendar: Calendar dict with start_date and timezone
        day_number: Day number to check (1-indexed)

    Returns:
        bool: True if day is unlocked, False otherwise
    """
    # Get timezone (hardcoded Berlin for Phase 2)
    tz = ZoneInfo(calendar.get('timezone', 'Europe/Berlin'))

    # Parse start date
    start_date = datetime.fromisoformat(calendar['start_date']).date()

    # Get current date in calendar's timezone
    current_datetime = datetime.now(tz)
    current_date = current_datetime.date()

    # Calculate unlock date for this day
    # Day 1 unlocks on start_date, Day 2 on start_date + 1, etc.
    day_unlock_date = start_date + timedelta(days=day_number - 1)

    # Day is unlocked if current date >= unlock date
    return current_date >= day_unlock_date
```

### Rate Limiting Implementation

```python
# app.py or similar
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://"  # Use Redis in production
)

# Apply to public endpoints
@app.route('/api/shared/<share_token>', methods=['GET'])
@limiter.limit("20 per minute")
def get_shared_calendar(share_token):
    # Implementation
    pass

@app.route('/api/shared/<share_token>/day/<int:day_number>', methods=['GET'])
@limiter.limit("30 per minute")
def get_shared_day(share_token, day_number):
    # Implementation
    pass
```

---

## Frontend Architecture

### New Routes

```typescript
// router/index.ts

const routes = [
  // ... existing routes

  // Public shared calendar viewer (no auth guard)
  {
    path: '/shared/:token',
    name: 'SharedCalendar',
    component: () => import('@/views/SharedCalendar.vue'),
    meta: { requiresAuth: false }
  }
]
```

### Component Structure

```
frontend/
├── views/
│   ├── SharedCalendar.vue          # Main public viewer page (Epic 4)
│   └── CalendarDetail.vue          # Add share button here (Epic 4)
├── components/
│   ├── sharing/
│   │   ├── ShareModal.vue          # Share modal with copy link (Epic 4)
│   │   ├── DoorGrid.vue            # Responsive door grid layout (Epic 4)
│   │   ├── DoorCard.vue            # Individual door component (Epic 4)
│   │   └── VideoModal.vue          # Video playback modal (Epic 5)
│   └── calendar/
│       ├── DoorOrderToggle.vue     # Sequential/Random toggle (Epic 5)
│       └── ThemeSelector.vue       # Theme dropdown (Epic 5)
├── composables/
│   ├── useSharedCalendar.ts        # Fetch shared calendar data (Epic 4)
│   ├── useDoorState.ts             # Calculate door states (Epic 4)
│   └── useOpenedTracking.ts        # LocalStorage tracking (Epic 4)
└── assets/
    └── christmas/
        ├── locked-door.svg         # Images for theme (separate issue)
        ├── unlocked-door.svg
        └── decorations/
```

---

## User Flows

### Flow 1: Creating a Shareable Calendar

```
1. User navigates to "Create Calendar" page
   ↓
2. Fills in calendar details:
   - Title: "My Advent Calendar 2025"
   - Start Date: December 1, 2025
   - Duration: 24 days
   ↓
3. [EPIC 5] Selects door order:
   - Toggle: Sequential / Random
   - If random: Click "Shuffle Again" to regenerate
   ↓
4. [EPIC 5] Selects theme:
   - Dropdown: "Christmas" (only option in Phase 2)
   ↓
5. Clicks "Create Calendar"
   ↓
6. System generates calendar with:
   - door_order: "random"
   - door_positions: [shuffled array]
   - theme: "christmas"
   - share_token: null (not shared yet)
   ↓
7. User uploads videos for each day
   ↓
8. Calendar is ready to share
```

### Flow 2: Sharing a Calendar

```
1. User opens their calendar from dashboard
   ↓
2. Clicks "Share Calendar" button
   ↓
3. Share modal opens with two states:

   State A (Not Shared Yet):
   ┌─────────────────────────────────┐
   │ This calendar is not shared yet │
   │ [Generate Share Link]           │
   └─────────────────────────────────┘

   State B (Already Shared):
   ┌─────────────────────────────────┐
   │ Share Link: https://...         │
   │ [Copy Link] [Preview]           │
   └─────────────────────────────────┘
   ↓
4. User clicks "Generate Share Link"
   ↓
5. Backend generates UUID token, stores in calendar
   ↓
6. Modal updates to State B, shows share URL
   ↓
7. User clicks "Copy Link"
   ↓
8. Toast notification: "Link copied to clipboard!"
   ↓
9. [EPIC 5] User clicks "Preview"
   ↓
10. New tab opens showing /shared/<token>
   ↓
11. User sees calendar as recipients will see it
```

### Flow 3: Viewing a Shared Calendar

```
1. Recipient receives share link (via email, message, etc.)
   ↓
2. Clicks link → Browser opens /shared/<token>
   ↓
3. Frontend fetches calendar data from public API
   ↓
4. System calculates which doors are unlocked:
   - Current time in Berlin timezone
   - Compare against start_date + day offsets
   ↓
5. Renders door grid:
   - Locked doors: Grey with 🔒, not clickable
   - Unlocked doors: Colorful, clickable
   - Opened doors: Thumbnail visible, checkmark
   ↓
6. Recipient clicks on unlocked door (e.g., Day 2)
   ↓
7. [EPIC 5] Door opening animation plays (0.6s swing)
   ↓
8. [EPIC 5] Video modal opens:
   - Large video player
   - Autoplay with sound
   - Fullscreen button available
   ↓
9. System marks door as "opened" in LocalStorage
   ↓
10. Door card updates to show "opened" state
   ↓
11. Recipient can click other unlocked doors
   ↓
12. Recipient closes browser tab when done
```

### Flow 4: Daily Unlock Experience

```
Timeline for calendar starting Dec 1, 2025:

November 30, 11:59 PM (Berlin):
- Recipient visits shared link
- All 24 doors are locked 🔒
- Message: "First door unlocks in 1 minute!"

December 1, 12:00 AM (Berlin):
- Page auto-refreshes or recipient reloads
- Door 1 is now unlocked (colorful, clickable)
- Doors 2-24 still locked
- Recipient clicks Door 1, watches video

December 2, 12:00 AM (Berlin):
- Recipient visits again
- Doors 1-2 are unlocked
- Door 1 shows "opened" state (thumbnail + checkmark)
- Door 2 shows "unlocked" state (ready to open)
- Doors 3-24 still locked

... pattern continues daily ...

December 24, 12:00 AM (Berlin):
- All 24 doors unlocked
- Recipient can open Door 24

December 25+ (after calendar ends):
- All 24 doors remain accessible
- Recipient can rewatch any video
- No new doors to unlock
```

---

## Visual Design Specifications

### Door States - Detailed Specifications

#### State 1: Locked Door 🔒

**Visual Characteristics:**
```css
.door-card.locked {
  /* Background */
  background: linear-gradient(135deg, #4a5568, #2d3748);
  border: 2px solid #2d3748;
  opacity: 0.6;

  /* Interaction */
  cursor: not-allowed;
  pointer-events: none;

  /* No hover effects */
}

.door-card.locked .lock-icon {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 2rem;
  color: #a0aec0;
}

.door-card.locked .day-number {
  font-size: 3rem;
  font-weight: bold;
  color: #718096;
  opacity: 0.7;
}

.door-card.locked .state-label {
  font-size: 0.875rem;
  color: #a0aec0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

**Accessibility:**
```html
<div
  class="door-card locked"
  role="button"
  aria-label="Day 3 - Unlocks December 3rd"
  aria-disabled="true"
  tabindex="-1"
>
```

---

#### State 2: Unlocked Door (Ready to Open)

**Visual Characteristics:**
```css
.door-card.unlocked {
  /* Christmas gradient */
  background: linear-gradient(135deg, #c41e3a 0%, #165b33 100%);
  border: 2px solid #ffd700;

  /* Shadow and glow */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);

  /* Interaction */
  cursor: pointer;
  transition: all 0.3s ease;
}

.door-card.unlocked:hover {
  transform: scale(1.05);
  box-shadow:
    0 8px 24px rgba(255, 215, 0, 0.4),
    0 0 20px rgba(255, 215, 0, 0.3);
  border-color: #fff;
}

.door-card.unlocked:active {
  transform: scale(0.98);
}

.door-card.unlocked .day-number {
  font-size: 3rem;
  font-weight: bold;
  color: #ffffff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.door-card.unlocked .state-label {
  font-size: 0.875rem;
  color: #ffd700;
  font-weight: 600;
  text-transform: uppercase;
}
```

**Accessibility:**
```html
<div
  class="door-card unlocked"
  role="button"
  aria-label="Day 2 - Click to open"
  tabindex="0"
  @keydown.enter="openDoor(2)"
  @keydown.space="openDoor(2)"
>
```

---

#### State 3: Opened Door (Already Watched)

**Visual Characteristics:**
```css
.door-card.opened {
  /* Darker green background */
  background: #2c5f2d;
  border: 2px solid #ffd700;

  /* Reduced opacity vs unlocked */
  opacity: 0.85;

  /* Still clickable */
  cursor: pointer;
  transition: all 0.3s ease;
}

.door-card.opened:hover {
  opacity: 1;
  transform: scale(1.02);
}

.door-card.opened .thumbnail-container {
  position: absolute;
  inset: 0;
  border-radius: 10px;
  overflow: hidden;
  z-index: 1;
}

.door-card.opened .thumbnail-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.7;
}

.door-card.opened .thumbnail-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.5) 100%
  );
  z-index: 2;
}

.door-card.opened .day-number {
  position: relative;
  z-index: 3;
  font-size: 2rem;
  color: white;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
}

.door-card.opened .watched-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 3;
  font-size: 2rem;
  color: #10b981; /* Green checkmark */
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}
```

**Accessibility:**
```html
<div
  class="door-card opened"
  role="button"
  aria-label="Day 1 - Watched - Click to rewatch"
  tabindex="0"
>
```

---

### Responsive Door Grid Layout

```css
.door-grid {
  display: grid;
  gap: 16px;
  padding: 16px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* Mobile: 2 columns */
@media (max-width: 640px) {
  .door-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    padding: 12px;
  }

  .door-card {
    min-height: 140px; /* Touch-friendly: 44px+ */
  }
}

/* Tablet: 3 columns */
@media (min-width: 641px) and (max-width: 1024px) {
  .door-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }

  .door-card {
    min-height: 150px;
  }
}

/* Desktop: 4 columns */
@media (min-width: 1025px) {
  .door-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }

  .door-card {
    min-height: 160px;
  }
}

/* Large desktop: 5-6 columns for large calendars */
@media (min-width: 1440px) {
  .door-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}
```

---

### Door Opening Animation (Epic 5)

```css
/* Animation triggered on click */
@keyframes doorSwing {
  0% {
    transform: perspective(1000px) rotateY(0deg);
    transform-origin: left center;
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    transform: perspective(1000px) rotateY(-90deg);
    transform-origin: left center;
    opacity: 0;
  }
}

.door-card.opening {
  animation: doorSwing 0.6s ease-out forwards;
}

/* Optional: Shimmer effect for unlocked doors */
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.door-card.unlocked::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 3s infinite;
  pointer-events: none;
}
```

---

### Video Modal Design (Epic 5)

```vue
<template>
  <ion-modal
    :is-open="isOpen"
    @didDismiss="closeModal"
    class="video-modal"
    :initial-breakpoint="1"
    :breakpoints="[0, 1]"
  >
    <div class="modal-content">
      <!-- Header -->
      <ion-header class="modal-header">
        <ion-toolbar>
          <ion-title>Day {{ dayNumber }}</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="closeModal">
              <ion-icon :icon="close"></ion-icon>
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>

      <!-- Video Player -->
      <div class="video-container">
        <video
          ref="videoPlayer"
          :src="videoUrl"
          controls
          autoplay
          controlsList="nodownload"
          class="video-player"
          @loadedmetadata="onVideoLoaded"
        >
          Your browser doesn't support video playback.
        </video>

        <!-- Fullscreen Button -->
        <ion-button
          @click="toggleFullscreen"
          class="fullscreen-btn"
          fill="clear"
        >
          <ion-icon
            :icon="isFullscreen ? contract : expand"
            slot="icon-only"
          />
        </ion-button>
      </div>
    </div>
  </ion-modal>
</template>

<style scoped>
.video-modal {
  --width: 90%;
  --height: 80%;
  --border-radius: 16px;
  --background: rgba(0, 0, 0, 0.95);
}

.modal-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #000;
}

.modal-header {
  flex-shrink: 0;
}

.video-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  overflow: hidden;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.fullscreen-btn {
  position: absolute;
  bottom: 80px; /* Above video controls */
  right: 20px;
  z-index: 10;
  --background: rgba(0, 0, 0, 0.6);
  --color: white;
}

/* Mobile: fullscreen modal */
@media (max-width: 768px) {
  .video-modal {
    --width: 100%;
    --height: 100%;
    --border-radius: 0;
  }
}
</style>
```

---

### Christmas Theme - Color Palette

```css
:root {
  /* Primary Christmas Colors */
  --christmas-red: #c41e3a;
  --christmas-green: #165b33;
  --christmas-gold: #ffd700;
  --christmas-white: #f8f9fa;

  /* Secondary Colors */
  --dark-green: #2c5f2d;
  --light-red: #e74c3c;
  --cream: #fff8dc;

  /* Neutral Colors */
  --dark-grey: #2d3748;
  --medium-grey: #4a5568;
  --light-grey: #718096;

  /* Accent Colors */
  --snow-white: #ffffff;
  --ice-blue: #e0f2fe;
  --warm-orange: #ff6b35;

  /* Gradients */
  --gradient-festive: linear-gradient(135deg, var(--christmas-red) 0%, var(--christmas-green) 100%);
  --gradient-gold: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  --gradient-locked: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
}
```

---

### Typography

```css
/* Christmas-themed typography */
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.calendar-title {
  font-family: 'Georgia', serif; /* Elegant, readable */
  font-size: 2rem;
  font-weight: 700;
  color: var(--christmas-red);
  text-align: center;
  margin: 1rem 0;
}

.door-number {
  font-family: 'Inter', sans-serif;
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
}

.state-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Accessibility: Minimum font sizes */
@media (max-width: 640px) {
  .calendar-title {
    font-size: 1.5rem;
  }

  .door-number {
    font-size: 2.5rem;
  }
}
```

---

## Technical Implementation Details

### Share Token Generation

```typescript
// backend/services/sharing.ts (pseudocode)

import { v4 as uuidv4 } from 'uuid';

function generateShareToken(calendarId: string, userId: string): string {
  // Verify calendar ownership
  const calendar = getCalendar(calendarId);
  if (calendar.user_id !== userId) {
    throw new Error('Unauthorized');
  }

  // Check if token already exists
  if (calendar.share_token) {
    return calendar.share_token;
  }

  // Generate new UUID token
  const shareToken = uuidv4();

  // Update calendar
  calendar.share_token = shareToken;
  saveCalendar(calendar);

  return shareToken;
}
```

---

### Door Position Shuffling

```typescript
// frontend/composables/useDoorPositions.ts

export function generateDoorPositions(duration: number): number[] {
  // Create sequential array [1, 2, 3, ..., duration]
  const positions = Array.from({ length: duration }, (_, i) => i + 1);

  // Fisher-Yates shuffle algorithm
  for (let i = positions.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [positions[i], positions[j]] = [positions[j], positions[i]];
  }

  return positions;
}

export function getDoorAtPosition(
  doorPositions: number[] | null,
  index: number
): number {
  // If sequential order (no positions array)
  if (!doorPositions) {
    return index + 1; // 1-indexed
  }

  // Return shuffled position
  return doorPositions[index];
}
```

---

### Unlock Status Calculation

```typescript
// frontend/composables/useDoorState.ts

import { ref, computed } from 'vue';

export type DoorState = 'locked' | 'unlocked' | 'opened';

export function useDoorState(calendar: any, openedDays: number[]) {
  const getDoorState = (dayNumber: number): DoorState => {
    // Check if already opened (from LocalStorage)
    if (openedDays.includes(dayNumber)) {
      return 'opened';
    }

    // Check if unlocked based on date
    if (isDayUnlocked(calendar, dayNumber)) {
      return 'unlocked';
    }

    // Default: locked
    return 'locked';
  };

  const isDayUnlocked = (calendar: any, dayNumber: number): boolean => {
    const startDate = new Date(calendar.start_date);
    const currentDate = new Date();

    // Calculate unlock date for this day
    // Note: Backend handles timezone, frontend uses response
    const unlockDate = new Date(startDate);
    unlockDate.setDate(unlockDate.getDate() + (dayNumber - 1));

    // Day is unlocked if current date >= unlock date
    return currentDate >= unlockDate;
  };

  return {
    getDoorState,
    isDayUnlocked
  };
}
```

---

### LocalStorage Tracking

```typescript
// frontend/composables/useOpenedTracking.ts

import { ref, watch } from 'vue';

export function useOpenedTracking(shareToken: string) {
  const storageKey = `calendar_${shareToken}_opened`;

  // Load from LocalStorage
  const openedDays = ref<number[]>(
    JSON.parse(localStorage.getItem(storageKey) || '[]')
  );

  // Save to LocalStorage when changed
  watch(openedDays, (newValue) => {
    localStorage.setItem(storageKey, JSON.stringify(newValue));
  }, { deep: true });

  // Mark day as opened
  const markAsOpened = (dayNumber: number) => {
    if (!openedDays.value.includes(dayNumber)) {
      openedDays.value.push(dayNumber);
    }
  };

  // Check if day is opened
  const isOpened = (dayNumber: number): boolean => {
    return openedDays.value.includes(dayNumber);
  };

  // Clear tracking (for testing)
  const clearTracking = () => {
    openedDays.value = [];
    localStorage.removeItem(storageKey);
  };

  return {
    openedDays,
    markAsOpened,
    isOpened,
    clearTracking
  };
}
```

---

### Copy to Clipboard

```typescript
// frontend/composables/useClipboard.ts

import { useToast } from '@/composables/useToast';

export function useClipboard() {
  const toast = useToast();

  const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
      // Modern Clipboard API
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        toast.show('Link copied to clipboard!', 'success');
        return true;
      }

      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();

      const success = document.execCommand('copy');
      document.body.removeChild(textarea);

      if (success) {
        toast.show('Link copied to clipboard!', 'success');
        return true;
      } else {
        throw new Error('Copy command failed');
      }
    } catch (error) {
      console.error('Failed to copy:', error);
      toast.show('Failed to copy link. Please copy manually.', 'error');
      return false;
    }
  };

  return {
    copyToClipboard
  };
}
```

---

### Video Fullscreen Control

```typescript
// frontend/components/sharing/VideoModal.vue (script)

const videoPlayer = ref<HTMLVideoElement | null>(null);
const isFullscreen = ref(false);

const toggleFullscreen = async () => {
  if (!videoPlayer.value) return;

  try {
    if (!document.fullscreenElement) {
      // Enter fullscreen
      await videoPlayer.value.requestFullscreen();
      isFullscreen.value = true;
    } else {
      // Exit fullscreen
      await document.exitFullscreen();
      isFullscreen.value = false;
    }
  } catch (error) {
    console.error('Fullscreen error:', error);
  }
};

// Listen for fullscreen changes
onMounted(() => {
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement;
  });
});

// Auto-play with sound
const playVideo = () => {
  if (videoPlayer.value) {
    videoPlayer.value.muted = false;
    videoPlayer.value.play().catch(err => {
      console.warn('Autoplay failed:', err);
      // Browser blocked autoplay with sound
      // Video controls will show play button
    });
  }
};
```

---

## Non-Functional Requirements

### Performance (NFR-P)
- **[P1]** Application load time: Under 5 seconds
- **[P3]** Calendar rendering: Under 3 seconds
- **Door grid rendering**: Optimize for 31 doors maximum
- **Video loading**: Progressive loading with buffering indicator
- **Image optimization**: Compress thumbnails to <100KB

### Security (NFR-S)
- **[S4]** Input validation: Sanitize share tokens (UUID format only)
- **Share tokens**: UUIDs (128-bit, cryptographically secure)
- **Video download**: Block with `controlsList="nodownload"`
- **Rate limiting**: Protect public endpoints from abuse
- **HTTPS only**: Enforce in production

### Usability (NFR-U)
- **[U1]** Mobile responsiveness: Support 320px+ screens
- **[U2]** Touch-friendly: 44px+ touch targets for all doors
- **[U5]** Accessibility: WCAG 2.1 AA compliance
  - Keyboard navigation: Tab through doors, Enter/Space to open
  - Screen readers: Proper ARIA labels on all interactive elements
  - Color contrast: Minimum 4.5:1 ratio for text
  - Focus indicators: Visible focus rings on all interactive elements

### Scalability (NFR-SC)
- **[SC3]** Modular architecture: Reusable components
- **Support**: 10-20 simultaneous viewers per shared calendar
- **Data storage**: JSON file-based (acceptable for Phase 2 scale)

### Browser Compatibility
- **Modern browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile browsers**: iOS Safari 14+, Chrome Mobile 90+
- **Features**: HTML5 video, CSS Grid, Flexbox, ES6+

---

## Implementation Workflow

This section provides detailed guidance on how to implement the 13 GitHub issues for Epic 4 and Epic 5.

### Implementation Strategy

**Approach**: Staged Implementation with Dependency Management

Implement issues in logical groups rather than strictly one-by-one, because some issues have dependencies while others can be done in parallel.

---

### Phase 1: Backend Foundation (Issues #74-#77)

#### Stage 1A: Data Model (Issue #74) - COMPLETED
Status: Merged to main via PR #87
- Added shareToken, doorOrder, doorPositions, theme, timezone fields
- Created validation functions with code quality improvements
- Backward compatibility maintained

---

#### Stage 1B: Share Token Generation (Issue #75) - COMPLETED
```
Issue #75: Backend - Share token generation endpoint
Duration: 1-2 hours
Dependencies: #74 COMPLETE
Status: MERGED via PR #88
```

**Completed** - Lazy share token generation endpoint working and tested.

---

#### Stage 1C: Public API (Issue #76) - COMPLETED
```
Issue #76: Backend - Public API endpoints
Duration: 2-3 hours
Dependencies: #74, #75 COMPLETE
Status: MERGED via PR #89
```

**Completed** - All 4 public endpoints working with Berlin timezone unlock logic.

**Implementation Details:**
- Created `app/utils/unlock_logic.py` with `is_day_unlocked()` function
- Created `app/routes/shared.py` with 4 public API endpoints
- Added service layer functions for public calendar data
- All endpoints tested with curl and working correctly
- Days unlock at midnight Berlin time as designed
- Privacy protection: No user data exposed in public responses

---

#### Stage 1D: Rate Limiting (Issue #77) - NEXT
```
Issue #77: Backend - Rate limiting
Duration: 1 hour
Dependencies: #76 COMPLETE
```

**Ready to implement** - Public endpoints exist and need rate limiting protection.

**Note:** Quick implementation - just add Flask-Limiter decorators to shared.py endpoints.

---

### Phase 2: Frontend Core (Issues #78-#80)

Now frontend can begin. These have some flexibility.

#### Stage 2A: Share Modal (Issue #78)
```
Issue #78: Frontend - Share modal
Duration: 2-3 hours
Dependencies: Backend #75 complete
```

**Why first?** Owner needs to generate share tokens before viewers can access.

**Workflow:**
1. Create share modal component
2. Integrate with calendar detail page
3. Test token generation and copy functionality
4. Must work before moving to viewer

---

#### Stage 2B: Public Viewer (Issue #79)
```
Issue #79: Frontend - Public viewer
Duration: 2-3 hours
Dependencies: Backend #76 complete
```

**Why next?** Creates the foundation for shared calendar display.

**Key:** This just creates the layout and route, doesn't handle door logic yet.

---

#### Stage 2C: Door States (Issue #80)
```
Issue #80: Frontend - Door states and unlock logic
Duration: 3-4 hours
Dependencies: #79 must be complete
```

**Why last?** Builds on the viewer layout created in #79.

**Critical:** This is the most complex frontend issue. Take time to implement all three door states correctly.

---

### Phase 3: Advanced Features (Issues #81-#86)

These can be more flexible and some can be done in parallel.

#### Parallel Group A: Calendar Creation Enhancements
```
Issue #81: Door ordering toggle (2-3 hours)
Issue #82: Theme selector (1 hour)
Dependencies: Backend #74 complete
```

**Can be done together** in same feature branch since both modify calendar creation form.

**Workflow:**
```bash
git checkout -b feature/81-82-calendar-creation-enhancements
# Implement both features
git commit -m "Add door ordering and theme selector Closes #81 Closes #82"
```

---

#### Sequential: Preview (Issue #83)
```
Issue #83: Preview functionality (1-2 hours)
Dependencies: #78, #79, #80 complete
```

**Why after core?** Preview opens the shared viewer, which must work first.

---

#### Parallel Group B: Polish & Animation
```
Issue #84: Door animation (2-3 hours)
Issue #85: Video modal (2-3 hours)
Dependencies: #80 complete
```

**Can be done in parallel** by working in separate branches, or sequentially if you prefer.

**Recommendation:** Do sequentially in one session for smooth flow.

---

#### Final Polish: Theme Styling (Issue #86)
```
Issue #86: Christmas theme styling (2-3 hours)
Dependencies: All other issues complete
```

**Why last?** Applies visual polish to everything that's already working.

---

### Complete Implementation Order

#### Progress Tracker

**Backend Foundation** (Issues #74-#77)
- [x] #74 - Data model (COMPLETED - PR #87)
- [x] #75 - Token generation (COMPLETED - PR #88)
- [x] #76 - Public API (COMPLETED - PR #89)
- [ ] #77 - Rate limiting (CURRENT)

**Frontend Core** (Issues #78-#80)
- [ ] #78 - Share modal
- [ ] #79 - Public viewer
- [ ] #80 - Door states

**Advanced Features** (Issues #81-#86)
- [ ] #81 - Door ordering toggle
- [ ] #82 - Theme selector
- [ ] #83 - Preview functionality
- [ ] #84 - Door animation
- [ ] #85 - Video modal
- [ ] #86 - Christmas styling

**Estimated remaining time:** 2-4 days of focused work

---

### Standard Workflow Per Issue

Repeat this workflow for each issue:

```bash
# 1. Start fresh from main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/<issue-number>-<short-description>

# 3. Move issue to "In Progress" on GitHub Projects
# (Update Kanban board)

# 4. Implement the feature
# - Write code
# - Follow acceptance criteria
# - Check NFRs

# 5. Test thoroughly
# - Run manual tests from issue description
# - Test edge cases
# - Verify NFR compliance

# 6. Commit with issue reference
git add .
git commit -m "Descriptive message Closes #<issue-number>"

# 7. Push when ready (only when you decide to)
git push origin feature/<issue-number>-<short-description>

# 8. Create Pull Request on GitHub
# - Review changes
# - Verify tests pass
# - Merge to main

# 9. Move issue to "Done" on GitHub Projects

# 10. Delete feature branch
git branch -d feature/<issue-number>-<short-description>
git push origin --delete feature/<issue-number>-<short-description>
```

---

### When to Group Issues

**Group together when:**
- Both modify the same file/component
- Testing them separately doesn't make sense
- They're both small (less than 2 hours each)
- No external dependencies between them

**Example:** Issues #81 and #82 (both modify calendar creation form)

**Keep separate when:**
- Issue is complex (more than 3 hours)
- High risk of breaking changes
- Different team members could work on them
- You want to test/demo incrementally

**Example:** Issue #80 (door states) should be alone due to complexity

---

### Testing Checkpoints

**After Backend Phase (Issues #74-#77):**
```bash
# Test entire backend with curl
curl -X POST http://localhost:5000/api/calendars/cal_123/generate-share-token \
  -H "Authorization: Bearer <token>"

curl http://localhost:5000/api/shared/<share_token>
```

**After Frontend Core (Issues #78-#80):**
- Owner can generate share link
- Owner can copy link
- Viewer can open link (no auth)
- Viewer sees correct door states
- Locked doors are not clickable

**After Advanced Features (Issues #81-#86):**
- Full end-to-end flow works
- Animations are smooth
- Theme is festive
- Preview shows correct view

---

### Things to Remember

**During Implementation:**
1. Always check NFRs from `non_functional_requirements_tracking.md`
2. Update documentation if you discover design issues
3. Test on mobile (use Chrome DevTools device emulation)
4. Test accessibility (use keyboard navigation, screen reader)
5. Check performance (calendar should render under 3 seconds)
6. Take screenshots of GitHub Projects board for academic documentation

**Before Merging Each PR:**
- All acceptance criteria met
- Manual testing complete
- NFRs verified
- Code is clean and commented
- No console errors
- Backward compatibility maintained

**After Each Merge:**
- Update Kanban board (move to Done)
- Take screenshot of progress (for portfolio)
- Update NFR tracking document if applicable
- Celebrate small win

---

### Quick Reference Card

```
BACKEND SEQUENCE (must be in order):
#74 → #75 → #76 → #77

FRONTEND CORE (must be in order):
#78 → #79 → #80

ADVANCED FEATURES (flexible):
#81 + #82 together
↓
#83 (needs #78, #79, #80)
↓
#84 + #85 (sequential or parallel)
↓
#86 (final polish)
```

---

### Issue Dependencies Diagram

```
Backend Foundation:
#74 (Data Model)
  ↓
#75 (Share Token)
  ↓
#76 (Public API)
  ↓
#77 (Rate Limiting)

Frontend Core:
#75 → #78 (Share Modal)
#76 → #79 (Public Viewer)
#79 → #80 (Door States)

Advanced Features:
#74 → #81 + #82 (Creation Form)
#78, #79, #80 → #83 (Preview)
#80 → #84 (Animation)
#80 → #85 (Video Modal)
All → #86 (Theme Styling)
```

---

### Issues Status Summary

**Epic 4: Core Sharing Functionality (7 issues)**

Backend Issues:
- [x] #74 - Backend - Extend calendar data model for sharing (COMPLETED)
- [x] #75 - Backend - Implement share token generation endpoint (COMPLETED)
- [ ] #76 - Backend - Create public API endpoints for shared calendars
- [ ] #77 - Backend - Add rate limiting to public endpoints

Frontend Issues:
- [ ] #78 - Frontend - Create share modal with copy-to-clipboard
- [ ] #79 - Frontend - Build public shared calendar viewer
- [ ] #80 - Frontend - Implement door states and unlock logic

**Epic 5: Advanced Sharing Features (6 issues)**

Frontend Issues:
- [ ] #81 - Frontend - Add door ordering toggle to calendar creation
- [ ] #82 - Frontend - Add theme selector to calendar creation
- [ ] #83 - Frontend - Implement preview functionality
- [ ] #84 - Frontend - Create door opening animation
- [ ] #85 - Frontend - Build video modal with autoplay and fullscreen
- [ ] #86 - Frontend - Implement Christmas theme styling

**Progress:** 3/13 issues completed (23%)

---

## Future Enhancements

### Phase 3 Features (Not in Epic 4/5)

1. **Advanced Rate Limiting**
   - Token-based throttling
   - View analytics per calendar
   - Block abusive IPs

2. **Viewer-Based Timezone Unlocking**
   - Unlocks based on viewer's local midnight
   - More personalized experience
   - Requires timezone detection in frontend

3. **Calendar Description Field**
   - Add description/message to calendars
   - Show on shared view
   - Optional field in creation form

4. **Revoke Share Link**
   - "Unshare" button without deleting calendar
   - Regenerate token to invalidate old links
   - Share history tracking

5. **Multiple Themes**
   - Birthday theme
   - Holiday theme
   - Custom theme builder
   - User-uploaded background images

6. **Loading States**
   - Skeleton loaders for door grid
   - Video buffering indicators
   - Smooth page transitions

7. **Decorative Images**
   - Source festive images (Unsplash, Freepik)
   - Snowfall animation
   - Holly, snowflakes, stars decorations
   - Background patterns

8. **Analytics Dashboard**
   - View count per calendar
   - Most viewed days
   - Viewer locations (country level)
   - Peak viewing times

9. **Social Sharing**
   - Share to Facebook, Twitter, WhatsApp
   - Generate preview cards (Open Graph)
   - QR code generation for easy mobile sharing

10. **Advanced Door Features**
    - Custom door colors per day
    - Animated door knock on hover
    - Sound effects on door open
    - Confetti animation on unlock

---

## Implementation Notes

### Epic 4 Priority
1. Backend API endpoints (Issues #23, #24, #25)
2. Share modal and copy link (Issues #29, #30)
3. Public viewer with door grid (Issue #32)
4. Door states and unlock logic (Issues #33, #35)
5. Error handling and tracking (Issues #36, #37)

### Epic 5 Priority
1. Door ordering toggle (Issues #26, #27, #28)
2. Theme selector UI (Issue #27)
3. Preview functionality (Issue #31)
4. Door animations (Issue #34)
5. Video modal with autoplay (Issue #34)
6. Christmas theme styling (Issue #38)

### Testing Checklist
- [ ] Share token generation works
- [ ] Public API respects rate limits
- [ ] Copy to clipboard works on mobile and desktop
- [ ] Door states calculate correctly based on date
- [ ] Locked doors cannot be clicked
- [ ] Unlocked doors open smoothly
- [ ] Video autoplay works (with fallback)
- [ ] Fullscreen video works
- [ ] LocalStorage tracking persists across page reloads
- [ ] Random door ordering displays correctly
- [ ] Preview opens in new tab with correct data
- [ ] Error page shows for invalid tokens
- [ ] Responsive grid works on 320px mobile screens
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Screen readers announce door states correctly
- [ ] All touch targets are 44px+ on mobile

---

## Documentation References

- **Main Project Instructions**: `/countdown-calendar-app/CLAUDE.md`
- **Requirements**: `/countdown-calendar-app/REQUIREMENTS.md`
- **NFR Tracking**: `/countdown-calendar-app/non_functional_requirements_tracking.md`
- **Technology Stack**: `/countdown-calendar-app/Tech_Stack_Planned.md`
- **This Document**: `/countdown-calendar-app/SHARING_FEATURE_DESIGN.md`

---

**Document Version**: 1.0
**Last Updated**: November 11, 2025
**Next Review**: After Epic 4 completion
