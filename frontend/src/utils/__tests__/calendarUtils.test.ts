/**
 * Unit Tests for Calendar Utilities
 * 
 * These tests demonstrate the testability and reliability of the extracted utilities.
 * Run with: npm run test:unit
 */
import {
  calculateDaysBetween,
  formatCalendarSummary,
  validateDateRange,
  isDateInPast,
  getTodayString,
  CALENDAR_CONSTANTS
} from '../calendarUtils';

describe('Calendar Utilities', () => {
  describe('calculateDaysBetween', () => {
    it('should calculate days correctly for valid date ranges', () => {
      expect(calculateDaysBetween('2025-12-01', '2025-12-25')).toBe(25);
      expect(calculateDaysBetween('2025-01-01', '2025-01-01')).toBe(1); // Same day
      expect(calculateDaysBetween('2025-01-01', '2025-01-02')).toBe(2); // Next day
    });

    it('should return null for invalid inputs', () => {
      expect(calculateDaysBetween('', '2025-12-25')).toBe(null);
      expect(calculateDaysBetween('2025-12-01', '')).toBe(null);
      expect(calculateDaysBetween('invalid', '2025-12-25')).toBe(null);
      expect(calculateDaysBetween('2025-12-25', '2025-12-01')).toBe(null); // End before start
    });
  });

  describe('formatCalendarSummary', () => {
    it('should format calendar summary correctly', () => {
      const result = formatCalendarSummary('2025-12-01', '2025-12-25');
      expect(result).toBe('📅 25-day calendar from Dec 1 - Dec 25, 2025');
    });

    it('should handle single day calendars', () => {
      const result = formatCalendarSummary('2025-12-01', '2025-12-01');
      expect(result).toBe('📅 1-day calendar from Dec 1 - Dec 1, 2025');
    });

    it('should return empty string for invalid inputs', () => {
      expect(formatCalendarSummary('', '2025-12-25')).toBe('');
      expect(formatCalendarSummary('invalid', '2025-12-25')).toBe('');
    });
  });

  describe('validateDateRange', () => {
    const futureStart = '2026-12-01'; // Use future dates to ensure tests don't fail due to current date
    const futureEnd = '2026-12-25';
    
    it('should return null for valid date ranges', () => {
      expect(validateDateRange(futureStart, futureEnd)).toBe(null);
    });

    it('should validate date order', () => {
      const error = validateDateRange(futureEnd, futureStart);
      expect(error).toBe('End date must be after start date');
    });

    it('should validate duration limits', () => {
      const longEnd = '2027-01-15'; // More than 31 days from start
      const error = validateDateRange(futureStart, longEnd);
      expect(error).toBe('Calendar cannot exceed 31 days');
    });

    it('should validate required fields', () => {
      expect(validateDateRange('', futureEnd)).toBe('Both start and end dates are required');
      expect(validateDateRange(futureStart, '')).toBe('Both start and end dates are required');
    });
  });

  describe('isDateInPast', () => {
    it('should correctly identify past dates', () => {
      expect(isDateInPast('2020-01-01')).toBe(true);
      expect(isDateInPast('2030-01-01')).toBe(false);
    });

    it('should handle invalid inputs', () => {
      expect(isDateInPast('')).toBe(false);
      expect(isDateInPast('invalid')).toBe(false);
    });
  });

  describe('getTodayString', () => {
    it('should return today in YYYY-MM-DD format', () => {
      const today = getTodayString();
      expect(today).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      
      // Should be parseable as a valid date
      const date = new Date(today);
      expect(date).toBeInstanceOf(Date);
      expect(isNaN(date.getTime())).toBe(false);
    });
  });

  describe('CALENDAR_CONSTANTS', () => {
    it('should have correct constant values', () => {
      expect(CALENDAR_CONSTANTS.MAX_DURATION_DAYS).toBe(31);
      expect(CALENDAR_CONSTANTS.MIN_DURATION_DAYS).toBe(1);
      expect(CALENDAR_CONSTANTS.DATE_FORMAT).toBe('YYYY-MM-DD');
    });
  });
});