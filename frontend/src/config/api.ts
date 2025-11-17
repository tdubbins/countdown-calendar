// API Configuration
// Hybrid approach: Use environment variable OR auto-detect from current hostname
// This works for localhost, mobile (same network), and production
const getBaseUrl = (): string => {
  // Option 1: Use explicit environment variable if set (for Webpack/Vue CLI)
  const envUrl = process.env.VUE_APP_API_BASE_URL;
  if (envUrl) {
    return envUrl;
  }

  // Option 2: Auto-detect - use current hostname with backend port
  // Works for both localhost (desktop) and IP address (mobile)
  const hostname = window.location.hostname;
  const protocol = window.location.protocol; // http: or https:
  return `${protocol}//${hostname}:5001/api`;
};

const API_CONFIG = {
  // Base URL for all API requests
  BASE_URL: getBaseUrl(),
  
  // Authentication endpoints
  AUTH: {
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile',
    VERIFY_EMAIL: '/auth/verify-email'
  },
  
  // Calendar endpoints (for future use)
  CALENDARS: {
    LIST: '/calendars',
    CREATE: '/calendars',
    GET: '/calendars',
    UPDATE: '/calendars',
    DELETE: '/calendars'
  }
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Export individual endpoint builders
export const API_ENDPOINTS = {
  // Authentication
  REGISTER: () => buildApiUrl(API_CONFIG.AUTH.REGISTER),
  LOGIN: () => buildApiUrl(API_CONFIG.AUTH.LOGIN),
  LOGOUT: () => buildApiUrl(API_CONFIG.AUTH.LOGOUT),
  PROFILE: () => buildApiUrl(API_CONFIG.AUTH.PROFILE),
  VERIFY_EMAIL: (token: string) => buildApiUrl(`${API_CONFIG.AUTH.VERIFY_EMAIL}/${token}`),
  
  // Calendars
  CALENDARS_LIST: () => buildApiUrl(API_CONFIG.CALENDARS.LIST),
  CALENDARS_CREATE: () => buildApiUrl(API_CONFIG.CALENDARS.CREATE),
  CALENDAR_BY_ID: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.GET}/${id}`),
  CALENDAR_UPDATE: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.UPDATE}/${id}`),
  CALENDAR_DELETE: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.DELETE}/${id}`),

  // Calendar Publishing
  CALENDAR_PUBLISH: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.GET}/${id}/publish`),
  CALENDAR_UNPUBLISH: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.GET}/${id}/unpublish`),

  // Video and Media URLs
  VIDEO_STREAM: (calendarId: string, dayNumber: number) =>
    buildApiUrl(`/calendars/${calendarId}/videos/${dayNumber}/stream`),
  VIDEO_THUMBNAIL: (calendarId: string, dayNumber: number) =>
    buildApiUrl(`/calendars/${calendarId}/videos/${dayNumber}/thumbnail`)
};

export default API_CONFIG;