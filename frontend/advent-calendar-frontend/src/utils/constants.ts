/**
 * Application Constants
 *
 * Centralized constants for the Advent Calendar App to ensure consistency
 * and make maintenance easier across the entire codebase.
 *
 * Benefits:
 * - Single source of truth for configuration values
 * - Easy to update across the entire app
 * - Type-safe constants with TypeScript
 * - Self-documenting code (names explain purpose)
 * - Prevents typos in repeated strings
 */

/**
 * Responsive Breakpoints (pixels)
 * Used by useResponsive composable and responsive logic
 */
export const BREAKPOINTS = {
  /** Mobile devices - below 768px */
  MOBILE: 768,
  /** Tablet devices - below 1024px */
  TABLET: 1024,
  /** Desktop devices - 1200px and above */
  DESKTOP: 1200
} as const;

/**
 * Touch Target Sizes (pixels)
 * NFR [U2]: Minimum touch target sizes for mobile accessibility
 */
export const TOUCH_TARGETS = {
  /** Minimum touch target size (44px per Apple/Google guidelines) */
  MIN_SIZE: 44,
  /** Comfortable touch target size */
  COMFORTABLE_SIZE: 48,
  /** Large touch target for primary actions */
  LARGE_SIZE: 56
} as const;

/**
 * Video Upload Constraints
 * NFR [S1]: File size and duration limits
 */
export const VIDEO_CONSTRAINTS = {
  /** Maximum video file size in bytes (50MB) */
  MAX_FILE_SIZE: 50 * 1024 * 1024,
  /** Maximum video duration in seconds (3 minutes) */
  MAX_DURATION: 180,
  /** Allowed video MIME types */
  ALLOWED_TYPES: ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'] as const
} as const;

/**
 * Calendar Constraints
 * Business logic limits for calendar creation
 */
export const CALENDAR_CONSTRAINTS = {
  /** Minimum number of days for a calendar */
  MIN_DAYS: 1,
  /** Maximum number of days for a calendar */
  MAX_DAYS: 31,
  /** Maximum title length */
  MAX_TITLE_LENGTH: 100,
  /** Minimum title length */
  MIN_TITLE_LENGTH: 3
} as const;

/**
 * Performance Thresholds
 * NFR [P1], [P3]: Performance targets
 */
export const PERFORMANCE = {
  /** Maximum app load time in milliseconds (5 seconds) */
  MAX_LOAD_TIME: 5000,
  /** Maximum calendar render time in milliseconds (3 seconds) */
  MAX_RENDER_TIME: 3000,
  /** Video compression target (reduce to 30-50% of original) */
  VIDEO_COMPRESSION_TARGET: 0.4
} as const;

/**
 * Error Messages
 * Standardized error messages for consistency across the app
 */
export const ERROR_MESSAGES = {
  // Generic errors
  GENERIC: 'An unexpected error occurred',
  NETWORK: 'Network error occurred. Please check your connection.',
  INTERNAL_SERVER: 'Internal server error. Please try again later.',

  // Authentication errors
  AUTH_FAILED: 'Authentication failed. Please check your credentials.',
  UNAUTHORIZED: 'Unauthorized access. Please log in again.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',

  // Calendar errors
  CALENDAR_NOT_FOUND: 'Calendar not found',
  CALENDAR_DELETE_FAILED: 'Failed to delete calendar',
  CALENDAR_UPDATE_FAILED: 'Failed to update calendar',
  CALENDAR_CREATE_FAILED: 'Failed to create calendar',
  CALENDAR_LOAD_FAILED: 'Failed to load calendars',

  // Video errors
  VIDEO_UPLOAD_FAILED: 'Failed to upload video',
  VIDEO_TOO_LARGE: 'Video file is too large (max 50MB)',
  VIDEO_TOO_LONG: 'Video is too long (max 3 minutes)',
  VIDEO_INVALID_TYPE: 'Invalid video format',

  // Validation errors
  VALIDATION_FAILED: 'Validation failed. Please check your input.',
  REQUIRED_FIELD: 'This field is required',
  INVALID_EMAIL: 'Invalid email address',
  INVALID_DATE: 'Invalid date',
  PASSWORDS_DONT_MATCH: 'Passwords do not match'
} as const;

/**
 * Success Messages
 * Standardized success messages for consistency
 */
export const SUCCESS_MESSAGES = {
  // Calendar operations
  CALENDAR_CREATED: 'Calendar created successfully',
  CALENDAR_UPDATED: 'Calendar updated successfully',
  CALENDAR_DELETED: 'Calendar deleted successfully',

  // Video operations
  VIDEO_UPLOADED: 'Video uploaded successfully',
  VIDEO_DELETED: 'Video deleted successfully',

  // Authentication
  LOGIN_SUCCESS: 'Logged in successfully',
  LOGOUT_SUCCESS: 'Logged out successfully',
  REGISTRATION_SUCCESS: 'Registration successful. Please check your email.',

  // Sharing
  LINK_COPIED: 'Share link copied to clipboard',
  CALENDAR_SHARED: 'Calendar shared successfully'
} as const;

/**
 * Local Storage Keys
 * Centralized keys to prevent typos and make refactoring easier
 */
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  THEME_PREFERENCE: 'theme_preference',
  LAST_CALENDAR_ID: 'last_calendar_id'
} as const;

/**
 * Route Paths
 * Centralized route paths for type-safe navigation
 */
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  CALENDAR_CREATE: '/calendar/create',
  CALENDAR_DETAIL: '/calendar/:id',
  SHARED_CALENDAR: '/shared/:token'
} as const;

/**
 * HTTP Status Codes
 * Common HTTP status codes for API responses
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
} as const;

/**
 * Animation Durations (milliseconds)
 * Consistent animation timings across the app
 */
export const ANIMATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
  VERY_SLOW: 800
} as const;

/**
 * Z-Index Layers
 * Consistent z-index management
 */
export const Z_INDEX = {
  BASE: 1,
  DROPDOWN: 1000,
  STICKY: 1020,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070
} as const;

/**
 * Calendar Themes
 * Available themes for shared calendar customization (Issue #82)
 * NFR [SC3]: Modular architecture prepared for future theme expansion
 */
export const THEME_OPTIONS = {
  /** Christmas theme - festive red and green color palette */
  CHRISTMAS: 'christmas'
  // Future themes:
  // BIRTHDAY: 'birthday',
  // HOLIDAY: 'holiday',
  // CUSTOM: 'custom'
} as const;

/**
 * Default calendar theme
 */
export const DEFAULT_THEME = THEME_OPTIONS.CHRISTMAS;
