// API Configuration
const API_CONFIG = {
  // Base URL for all API requests
  BASE_URL: 'http://localhost:5001/api',
  
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
  
  // Calendars (for future use)
  CALENDARS_LIST: () => buildApiUrl(API_CONFIG.CALENDARS.LIST),
  CALENDAR_BY_ID: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.GET}/${id}`)
};

export default API_CONFIG;