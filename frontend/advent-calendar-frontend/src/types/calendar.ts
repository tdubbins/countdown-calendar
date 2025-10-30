// Calendar Data Types

export interface Calendar {
  id: string;
  title: string;
  startDate: string;
  endDate: string;
  duration: number;
  dateRange: string;
  videoCount: number;
  status: string;
  shareToken?: string;
  createdAt: string;
  userId: string;
}

export interface CalendarSummary {
  id: string;
  title: string;
  dateRange: string;
  videoCount: number;
  status: string;
}

export interface CalendarCreateData {
  title: string;
  startDate: string;
  duration: number;
}

// API Response Types
export interface CalendarCreateResponse {
  success: boolean;
  message: string;
  calendar: Calendar;
}

export interface CalendarListResponse {
  success: boolean;
  message: string;
  calendars: Calendar[];
}

export interface CalendarGetResponse {
  success: boolean;
  message: string;
  calendar: Calendar;
}

export interface CalendarUpdateResponse {
  success: boolean;
  message: string;
  calendar: Calendar;
}

export interface CalendarVideo {
  day: number;
  fileName: string;
  filePath: string;
  uploadedAt: string;
  processed: boolean;
}

// UI Component Props
export interface CalendarCardProps {
  calendar: CalendarSummary;
  onClick?: (calendarId: string) => void;
}

export interface EmptyStateProps {
  icon: string;
  title: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}