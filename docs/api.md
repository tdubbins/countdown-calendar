# API Reference

Base URL: `/api`

## Authentication

JWT token in header:
```
Authorization: Bearer <token>
```

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register user |
| POST | `/auth/login` | No | Login, returns token |
| POST | `/auth/logout` | Yes | Logout |
| GET | `/auth/profile` | Yes | Get current user |
| GET | `/auth/verify-email/<token>` | No | Verify email |
| POST | `/auth/resend-verification` | No | Resend verification email |

## Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| PUT | `/users/profile` | Yes | Update profile |
| PUT | `/users/password` | Yes | Change password |
| DELETE | `/users/account` | Yes | Delete account |

## Calendars

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/calendars` | Yes | List user's calendars |
| POST | `/calendars` | Yes | Create calendar |
| GET | `/calendars/<id>` | * | Get calendar |
| PUT | `/calendars/<id>` | Yes | Update calendar |
| DELETE | `/calendars/<id>` | Yes | Delete calendar |
| POST | `/calendars/<id>/publish` | Yes | Publish calendar |
| POST | `/calendars/<id>/unpublish` | Yes | Unpublish calendar |

*Public access if published, otherwise owner only

## Videos

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/calendars/<id>/videos` | Yes | Upload video |
| GET | `/calendars/<id>/videos` | Yes | List videos |
| GET | `/calendars/<id>/videos/status` | Yes | Bulk processing status |
| GET | `/calendars/<id>/videos/<day>` | Yes | Get video metadata |
| GET | `/calendars/<id>/videos/<day>/status` | Yes | Processing status |
| GET | `/calendars/<id>/videos/<day>/stream` | * | Stream video |
| GET | `/calendars/<id>/videos/<day>/thumbnail` | * | Get thumbnail |
| DELETE | `/calendars/<id>/videos/<day>` | Yes | Delete video |
| POST | `/calendars/<id>/videos/reassign` | Yes | Move video to different day |

*Public if published and door unlocked

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API info |

## Errors

```json
{
  "error": "Error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | Not authorized |
| 404 | Not found |
| 413 | File too large |
| 429 | Rate limited |

## Data Models

### Calendar

```json
{
  "id": "uuid",
  "title": "My Calendar",
  "startDate": "2025-12-01",
  "endDate": "2025-12-24",
  "duration": 24,
  "status": "upcoming",
  "published": false,
  "theme": "christmas",
  "doorOrder": "sequential",
  "videos": { "1": { "filename": "day_1.mp4", ... } },
  "videoCount": 1
}
```

Status: `draft`, `upcoming`, `active`, `completed`

### User

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "email_verified": true,
  "calendar_ids": ["uuid1", "uuid2"]
}
```
