// Calendar Data Types

/**
 * Door ordering type for shared calendars (Issue #81)
 * - sequential: Doors appear in order 1, 2, 3, ...
 * - random: Doors appear in shuffled order
 */
export type DoorOrder = 'sequential' | 'random';

export interface Calendar {
  id: string;
  title: string;
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
  // Issue #81: Door ordering fields for shared calendar customization
  doorOrder?: DoorOrder | null;     // How doors appear to viewers ("sequential" or "random")
  doorPositions?: number[] | null;  // Shuffled positions array for random ordering
  theme?: string | null;            // Theme identifier (e.g., "christmas")
  timezone?: string | null;         // IANA timezone (e.g., "Europe/Berlin")
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
  startDate: string;
  duration: number;
}

/**
 * Data for updating an existing calendar (Issue #81)
 * All fields are optional - only provided fields will be updated
 */
export interface CalendarUpdateData {
  title?: string;
  startDate?: string;
  duration?: number;
  doorOrder?: DoorOrder;       // Issue #81: Change door ordering for shared view
  doorPositions?: number[];    // Issue #81: Update shuffled positions
  theme?: string;              // Issue #81: Change theme
  timezone?: string;           // Issue #81: Change timezone
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