const getBaseUrl = (): string => {
  const envUrl = process.env.VUE_APP_API_BASE_URL;
  if (envUrl) {
    return envUrl;
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  return `${protocol}//${hostname}:5001/api`;
};

const API_CONFIG = {
  BASE_URL: getBaseUrl(),

  AUTH: {
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile',
    VERIFY_EMAIL: '/auth/verify-email',
    RESEND_VERIFICATION: '/auth/resend-verification'
  },

  USERS: {
    PROFILE: '/users/profile',
    PASSWORD: '/users/password',
    ACCOUNT: '/users/account'
  },

  CALENDARS: {
    LIST: '/calendars',
    CREATE: '/calendars',
    GET: '/calendars',
    UPDATE: '/calendars',
    DELETE: '/calendars'
  }
};

export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

export const API_ENDPOINTS = {
  REGISTER: () => buildApiUrl(API_CONFIG.AUTH.REGISTER),
  LOGIN: () => buildApiUrl(API_CONFIG.AUTH.LOGIN),
  LOGOUT: () => buildApiUrl(API_CONFIG.AUTH.LOGOUT),
  PROFILE: () => buildApiUrl(API_CONFIG.AUTH.PROFILE),
  VERIFY_EMAIL: (token: string) => buildApiUrl(`${API_CONFIG.AUTH.VERIFY_EMAIL}/${token}`),
  RESEND_VERIFICATION: () => buildApiUrl(API_CONFIG.AUTH.RESEND_VERIFICATION),

  UPDATE_PROFILE: () => buildApiUrl(API_CONFIG.USERS.PROFILE),
  CHANGE_PASSWORD: () => buildApiUrl(API_CONFIG.USERS.PASSWORD),
  DELETE_ACCOUNT: () => buildApiUrl(API_CONFIG.USERS.ACCOUNT),

  CALENDARS_LIST: () => buildApiUrl(API_CONFIG.CALENDARS.LIST),
  CALENDARS_CREATE: () => buildApiUrl(API_CONFIG.CALENDARS.CREATE),
  CALENDAR_BY_ID: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.GET}/${id}`),
  CALENDAR_UPDATE: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.UPDATE}/${id}`),
  CALENDAR_DELETE: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.DELETE}/${id}`),

  CALENDAR_PUBLISH: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.GET}/${id}/publish`),
  CALENDAR_UNPUBLISH: (id: string) => buildApiUrl(`${API_CONFIG.CALENDARS.GET}/${id}/unpublish`),

  VIDEO_STREAM: (calendarId: string, dayNumber: number) =>
    buildApiUrl(`/calendars/${calendarId}/videos/${dayNumber}/stream`),
  VIDEO_THUMBNAIL: (calendarId: string, dayNumber: number) =>
    buildApiUrl(`/calendars/${calendarId}/videos/${dayNumber}/thumbnail`)
};

export default API_CONFIG;