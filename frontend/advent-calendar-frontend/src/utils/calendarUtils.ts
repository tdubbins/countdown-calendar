/**
 * Calendar Utilities
 * 
 * Reusable functions for calendar date calculations, validation, and formatting.
 * These utilities will be used across calendar creation, editing, display, and validation.
 */

/**
 * Calculate the number of days between two dates (inclusive)
 * 
 * @param startDate - Start date in YYYY-MM-DD format
 * @param endDate - End date in YYYY-MM-DD format
 * @returns Number of days between dates (inclusive) or null if invalid
 * 
 * @example
 * calculateDaysBetween('2025-12-01', '2025-12-25') // Returns 25
 * calculateDaysBetween('2025-12-25', '2025-12-01') // Returns null (invalid range)
 */
export const calculateDaysBetween = (startDate: string, endDate: string): number | null => {
  if (!startDate || !endDate) return null;
  
  try {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // Check for invalid dates
    if (isNaN(start.getTime()) || isNaN(end.getTime())) return null;
    
    // Calculate difference in days (inclusive)
    const timeDiff = end.getTime() - start.getTime();
    const dayDiff = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1;
    
    return dayDiff > 0 ? dayDiff : null;
  } catch {
    return null;
  }
};

/**
 * Format a calendar summary with date range and duration
 * 
 * @param startDate - Start date in YYYY-MM-DD format
 * @param endDate - End date in YYYY-MM-DD format
 * @param duration - Number of days (optional, will be calculated if not provided)
 * @returns Formatted summary string
 * 
 * @example
 * formatCalendarSummary('2025-12-01', '2025-12-25') 
 * // Returns "📅 25-day calendar from Dec 1 - Dec 25, 2025"
 */
export const formatCalendarSummary = (
  startDate: string, 
  endDate: string, 
  duration?: number
): string => {
  if (!startDate || !endDate) return '';
  
  try {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // Check for invalid dates
    if (isNaN(start.getTime()) || isNaN(end.getTime())) return '';
    
    const calculatedDuration = duration || calculateDaysBetween(startDate, endDate);
    if (!calculatedDuration) return '';
    
    const startFormatted = start.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
    
    const endFormatted = end.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
    
    const dayText = calculatedDuration === 1 ? 'day' : 'day';
    
    return `📅 ${calculatedDuration}-${dayText} calendar from ${startFormatted} - ${endFormatted}`;
  } catch {
    return '';
  }
};

/**
 * Validate a date range for calendar creation/editing
 * 
 * @param startDate - Start date in YYYY-MM-DD format
 * @param endDate - End date in YYYY-MM-DD format
 * @param maxDuration - Maximum allowed duration in days (default: 31)
 * @returns Error message if invalid, null if valid
 * 
 * @example
 * validateDateRange('2025-12-01', '2025-12-25') // Returns null (valid)
 * validateDateRange('2025-12-25', '2025-12-01') // Returns error message
 */
export const validateDateRange = (
  startDate: string, 
  endDate: string, 
  maxDuration = 31
): string | null => {
  if (!startDate || !endDate) {
    return 'Both start and end dates are required';
  }
  
  try {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // Check for invalid dates
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      return 'Invalid date format';
    }
    
    // Check if dates are in the past
    if (start < today) {
      return 'Start date cannot be in the past';
    }
    
    if (end < today) {
      return 'End date cannot be in the past';
    }
    
    // Check date order
    if (end <= start) {
      return 'End date must be after start date';
    }
    
    // Check duration limit
    const duration = calculateDaysBetween(startDate, endDate);
    if (duration && duration > maxDuration) {
      return `Calendar cannot exceed ${maxDuration} days`;
    }
    
    return null; // Valid
  } catch {
    return 'Invalid date format';
  }
};

/**
 * Check if a date string is in the past
 * 
 * @param dateString - Date in YYYY-MM-DD format
 * @returns True if date is in the past
 */
export const isDateInPast = (dateString: string): boolean => {
  if (!dateString) return false;
  
  try {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    return date < today;
  } catch {
    return false;
  }
};

/**
 * Format a single date for display
 * 
 * @param dateString - Date in YYYY-MM-DD format
 * @param options - Intl.DateTimeFormat options
 * @returns Formatted date string
 */
export const formatDisplayDate = (
  dateString: string, 
  options: Intl.DateTimeFormatOptions = {
    weekday: 'long',
    year: 'numeric', 
    month: 'long',
    day: 'numeric'
  }
): string => {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '';
    
    return date.toLocaleDateString('en-US', options);
  } catch {
    return '';
  }
};

/**
 * Get today's date in YYYY-MM-DD format
 * Useful for setting minimum dates in form inputs
 * 
 * @returns Today's date in YYYY-MM-DD format
 */
export const getTodayString = (): string => {
  const today = new Date();
  return today.toISOString().split('T')[0];
};

/**
 * Calendar utility constants
 */
export const CALENDAR_CONSTANTS = {
  MAX_DURATION_DAYS: 31,
  MIN_DURATION_DAYS: 1,
  DATE_FORMAT: 'YYYY-MM-DD'
} as const;