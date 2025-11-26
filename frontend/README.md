# Frontend - Ionic Vue PWA

Progressive Web App built with Ionic Vue and TypeScript for the Countdown Calendar App.

## Prerequisites

- **Node.js 16+** with npm
- Backend API running (see [backend/README.md](../backend/README.md))

## Installation

```bash
cd frontend

# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env.development
```

## Configuration

Edit `.env.development` for local development:

```env
# API Base URL (leave empty for auto-detection)
VUE_APP_API_BASE_URL=

# For production
# VUE_APP_API_BASE_URL=https://api.yourdomain.com/api
```

Auto-detection uses `http://<current-hostname>:5001/api` in development.

## Development

```bash
# Start development server with hot-reload
npm run serve

# App runs at http://localhost:8080
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run serve` | Start development server |
| `npm run build` | Build for production |
| `npm run lint` | Lint and fix files |
| `npm run test:unit` | Run unit tests |
| `npm run test:e2e` | Run end-to-end tests |

## Project Structure

```
frontend/
├── src/
│   ├── App.vue              # Root component
│   ├── main.ts              # Application entry point
│   │
│   ├── views/               # Page components
│   │   ├── CalendarsPage.vue      # Dashboard (calendar list)
│   │   ├── CalendarCreatePage.vue # Create new calendar
│   │   ├── CalendarEditPage.vue   # Edit calendar settings
│   │   ├── CalendarViewPage.vue   # Shared calendar viewer
│   │   ├── LoginPage.vue          # User login
│   │   ├── RegisterPage.vue       # User registration
│   │   ├── ProfilePage.vue        # User profile management
│   │   ├── EmailVerificationPage.vue # Email verification
│   │   └── HelpPage.vue           # Help documentation
│   │
│   ├── components/          # Reusable UI components
│   │   ├── CalendarCard.vue       # Calendar list item
│   │   ├── CalendarDayCard.vue    # Individual door component
│   │   ├── CalendarDayGrid.vue    # Door grid layout
│   │   ├── CalendarForm.vue       # Calendar create/edit form
│   │   ├── VideoModal.vue         # Video playback modal
│   │   ├── ShareModal.vue         # Sharing dialog
│   │   ├── StatusChip.vue         # Calendar status indicator
│   │   ├── ThemeSelector.vue      # Theme picker
│   │   ├── DoorOrderToggle.vue    # Sequential/random toggle
│   │   └── ...                    # Additional components
│   │
│   ├── composables/         # Vue Composition API functions
│   │   ├── useAuth.ts             # Authentication state
│   │   ├── useCalendar.ts         # Calendar operations
│   │   ├── useVideoManagement.ts  # Video upload/streaming
│   │   ├── useSharedCalendar.ts   # Public calendar access
│   │   ├── useProfile.ts          # User profile management
│   │   ├── useFormValidation.ts   # Form validation
│   │   ├── useToast.ts            # Toast notifications
│   │   ├── useAlert.ts            # Alert dialogs
│   │   ├── useLoading.ts          # Loading states
│   │   └── useModal.ts            # Modal management
│   │
│   ├── router/              # Vue Router configuration
│   │   └── index.ts               # Route definitions
│   │
│   ├── theme/               # Theming system
│   │   ├── variables.css          # CSS custom properties
│   │   └── themes/                # Theme definitions
│   │
│   ├── utils/               # Helper functions
│   │   ├── api.ts                 # HTTP client
│   │   ├── constants.ts           # Application constants
│   │   ├── dateUtils.ts           # Date formatting
│   │   └── validation.ts          # Input validation
│   │
│   ├── types/               # TypeScript definitions
│   │   └── index.ts               # Type interfaces
│   │
│   ├── config/              # Configuration
│   │   └── api.config.ts          # API configuration
│   │
│   └── assets/              # Static assets
│       └── ...                    # Images, icons
│
├── public/                  # Public static files
│   ├── index.html           # HTML template
│   └── assets/              # Public assets
│
├── tests/                   # Test files
│   ├── unit/                # Unit tests
│   └── e2e/                 # End-to-end tests
│
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript configuration
├── .eslintrc.js             # ESLint configuration
└── babel.config.js          # Babel configuration
```

## Key Components

### Views (Pages)

| Component | Route | Description |
|-----------|-------|-------------|
| `CalendarsPage` | `/calendars` | User dashboard with calendar list |
| `CalendarCreatePage` | `/calendars/new` | Create new calendar form |
| `CalendarEditPage` | `/calendars/:id` | Edit calendar and manage videos |
| `CalendarViewPage` | `/calendar/:id` | Public shared calendar viewer |
| `LoginPage` | `/login` | User authentication |
| `RegisterPage` | `/register` | New user registration |
| `ProfilePage` | `/profile` | User profile management |
| `HelpPage` | `/help` | Feature documentation |

### Composables (Hooks)

| Composable | Purpose |
|------------|---------|
| `useAuth` | Authentication state and operations |
| `useCalendar` | Calendar CRUD operations |
| `useVideoManagement` | Video upload, compression status, streaming |
| `useSharedCalendar` | Public calendar fetching |
| `useProfile` | User profile updates |
| `useFormValidation` | Input validation with error messages |
| `useToast` | Toast notifications |
| `useLoading` | Loading state management |

## Technology Stack

- **Framework**: Vue 3.2 with Composition API
- **UI Library**: Ionic Vue 7.0
- **Language**: TypeScript 4.3
- **Router**: Vue Router 4.1
- **Icons**: Ionicons 7.0
- **Testing**: Jest (unit), Cypress (e2e)
- **Build**: Vue CLI 5.0

## Code Patterns

### Composition API
All components use Vue 3 Composition API with `<script setup>`:

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useCalendar } from '@/composables/useCalendar';

const { calendars, fetchCalendars } = useCalendar();

onMounted(() => {
  fetchCalendars();
});
</script>
```

### API Calls
Use the centralized API configuration:

```typescript
import { API_CONFIG } from '@/config/api.config';

const response = await fetch(`${API_CONFIG.BASE_URL}/calendars`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## Building for Production

```bash
# Build optimized bundle
npm run build

# Output in dist/ directory
```

The build output can be served by any static file server or the Flask backend.

## Testing

```bash
# Unit tests
npm run test:unit

# E2E tests (requires running app)
npm run test:e2e

# Lint check
npm run lint
```

## Mobile Support

The app is built as a Progressive Web App (PWA) with:
- Responsive design (320px minimum width)
- Touch-friendly interface (44px minimum touch targets)
- Capacitor plugins for native features
- Installable on mobile devices

## Theming

Themes are defined in `src/theme/themes/` and applied via CSS custom properties:

- **Default**: Clean, minimal design
- **Christmas**: Festive with snowflakes
- **Birthday**: Colorful with confetti

Theme selection is stored per-calendar in the backend.
