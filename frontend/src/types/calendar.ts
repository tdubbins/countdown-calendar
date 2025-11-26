// Calendar Data Types

/**
 * Door ordering type for shared calendars
 */
export type DoorOrder = 'sequential' | 'random';

export interface Calendar {
  id: string;
  title: string;
  description?: string;             // Optional calendar description visible to viewers
  startDate: string;
  endDate?: string;
  duration: number;
  dateRange?: string;
  videoCount: number;
  status?: string;
  published?: boolean;              // New: Is calendar publicly accessible
  isOwner?: boolean;                // New: Is authenticated user the owner
  createdAt: string;
  updatedAt?: string;
  doorOrder?: DoorOrder | null;
  doorPositions?: number[] | null;
  theme?: string | null;
  timezone?: string | null;
}

export interface CalendarSummary {
  id: string;
  title: string;
  startDate?: string;
  endDate?: string;
  dateRange?: string;
  videoCount: number;
  status?: string;
  published?: boolean;  // Is calendar publicly accessible
}

export interface CalendarCreateData {
  title: string;
  description?: string;        // Optional calendar description visible to viewers
  startDate: string;
  duration: number;
}

/**
 * Data for updating an existing calendar.
 * All fields are optional - only provided fields will be updated.
 */
export interface CalendarUpdateData {
  title?: string;
  description?: string;
  startDate?: string;
  duration?: number;
  doorOrder?: DoorOrder;
  doorPositions?: number[];
  theme?: string;
  timezone?: string;
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