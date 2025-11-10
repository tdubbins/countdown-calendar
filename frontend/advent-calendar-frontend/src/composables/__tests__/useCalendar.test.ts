/**
 * Unit Tests for useCalendar Composable
 *
 * Tests calendar CRUD operations with mocked API calls.
 * Ensures proper state management, error handling, and loading states.
 *
 * Coverage targets:
 * - createCalendar(): Create new calendar
 * - loadCalendars(): Fetch user's calendars
 * - getCalendar(): Fetch single calendar details
 * - updateCalendar(): Update calendar data
 * - deleteCalendar(): Delete calendar
 * - Reactive state: calendars, isLoading, hasCalendars, currentCalendar
 *
 * Run with: npm run test:unit src/composables/__tests__/useCalendar.test.ts
 */

import { useCalendar } from '../useCalendar';
import { API_ENDPOINTS } from '@/config/api';
import type { Calendar, CalendarSummary, CalendarCreateData } from '@/types/calendar';

// Mock dependencies
jest.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    getAuthHeaders: jest.fn(() => ({
      'Content-Type': 'application/json',
      Authorization: 'Bearer mock-token',
    })),
  }),
}));

jest.mock('@/config/api', () => ({
  API_ENDPOINTS: {
    CALENDARS_LIST: () => 'http://localhost:5001/api/calendars',
    CALENDAR_BY_ID: (id: string) => `http://localhost:5001/api/calendars/${id}`,
    CALENDAR_UPDATE: (id: string) => `http://localhost:5001/api/calendars/${id}`,
    CALENDAR_DELETE: (id: string) => `http://localhost:5001/api/calendars/${id}`,
  },
}));

describe('useCalendar Composable', () => {
  // Test data
  const mockCalendar: Calendar = {
    id: 'cal-123',
    title: 'Advent Calendar 2025',
    startDate: '2025-12-01',
    endDate: '2025-12-25',
    duration: 25,
    dateRange: 'Dec 1 - Dec 25, 2025',
    videoCount: 5,
    status: 'active',
    shareToken: 'share-123',
    createdAt: '2025-11-01T00:00:00Z',
    userId: 'user-123',
  };

  const mockCalendarSummary: CalendarSummary = {
    id: mockCalendar.id,
    title: mockCalendar.title,
    dateRange: mockCalendar.dateRange,
    videoCount: mockCalendar.videoCount,
    status: mockCalendar.status,
  };

  const mockCalendarCreateData: CalendarCreateData = {
    title: 'New Calendar',
    startDate: '2025-12-01',
    duration: 24,
  };

  // Setup and teardown
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  /**
   * Test Suite: createCalendar()
   *
   * Tests calendar creation with various scenarios.
   */
  describe('createCalendar', () => {
    describe('Successful creation', () => {
      it('should create calendar successfully', async () => {
        // Mock successful API response
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 201,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            message: 'Calendar created successfully',
            calendar: mockCalendar,
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.createCalendar(mockCalendarCreateData);

        // Verify result
        expect(result.success).toBe(true);
        expect(result.data).toEqual(mockCalendar);

        // Verify API call
        expect(global.fetch).toHaveBeenCalledWith(
          API_ENDPOINTS.CALENDARS_LIST(),
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
              Authorization: 'Bearer mock-token',
            }),
            body: JSON.stringify(mockCalendarCreateData),
          })
        );

        // Verify state updated
        expect(calendar.calendars.value).toHaveLength(1);
        expect(calendar.hasCalendars.value).toBe(true);
        expect(calendar.calendarCount.value).toBe(1);
      });

      it('should add new calendar to the beginning of the list', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendars: [mockCalendar],
          }),
        });

        const calendar = useCalendar();
        await calendar.loadCalendars();

        // Mock second calendar creation
        const secondCalendar = { ...mockCalendar, id: 'cal-456', title: 'Second Calendar' };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 201,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendar: secondCalendar,
          }),
        });

        await calendar.createCalendar(mockCalendarCreateData);

        // New calendar should be first
        expect(calendar.calendars.value[0].id).toBe('cal-456');
        expect(calendar.calendarCount.value).toBe(2);
      });

      it('should set loading state during creation', async () => {
        (global.fetch as jest.Mock).mockImplementationOnce(
          () =>
            new Promise((resolve) =>
              setTimeout(
                () =>
                  resolve({
                    ok: true,
                    headers: new Headers({
                      'content-type': 'application/json',
                      'content-length': '500',
                    }),
                    json: async () => ({
                      success: true,
                      calendar: mockCalendar,
                    }),
                  }),
                100
              )
            )
        );

        const calendar = useCalendar();
        const createPromise = calendar.createCalendar(mockCalendarCreateData);

        expect(calendar.isLoading.value).toBe(true);
        await createPromise;
        expect(calendar.isLoading.value).toBe(false);
      });
    });

    describe('Failed creation', () => {
      it('should handle validation errors', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 400,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'Calendar title must be at least 3 characters',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.createCalendar({
          title: 'AB',
          startDate: '2025-12-01',
          duration: 24,
        });

        expect(result.success).toBe(false);
        expect(result.error).toContain('3 characters');
        expect(calendar.calendars.value).toHaveLength(0);
      });

      it('should handle duplicate calendar name', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 409,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'A calendar with this title already exists',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.createCalendar(mockCalendarCreateData);

        expect(result.success).toBe(false);
        expect(result.error).toContain('already exists');
      });

      it('should handle network errors', async () => {
        (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

        const calendar = useCalendar();
        const result = await calendar.createCalendar(mockCalendarCreateData);

        expect(result.success).toBe(false);
        expect(result.error).toBe('Network error');
      });

      it('should set loading to false after error', async () => {
        (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Error'));

        const calendar = useCalendar();
        await calendar.createCalendar(mockCalendarCreateData);

        expect(calendar.isLoading.value).toBe(false);
      });
    });
  });

  /**
   * Test Suite: loadCalendars()
   *
   * Tests fetching user's calendar list.
   */
  describe('loadCalendars', () => {
    describe('Successful load', () => {
      it('should load calendars successfully', async () => {
        const mockCalendars = [mockCalendar, { ...mockCalendar, id: 'cal-456' }];

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendars: mockCalendars,
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.loadCalendars();

        expect(result.success).toBe(true);
        expect(result.data).toHaveLength(2);
        expect(calendar.calendars.value).toHaveLength(2);
        expect(calendar.hasCalendars.value).toBe(true);
      });

      it('should handle empty calendar list', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '50',
          }),
          json: async () => ({
            success: true,
            calendars: [],
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.loadCalendars();

        expect(result.success).toBe(true);
        expect(result.data).toHaveLength(0);
        expect(calendar.hasCalendars.value).toBe(false);
        expect(calendar.calendarCount.value).toBe(0);
      });

      it('should convert Calendar to CalendarSummary', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendars: [mockCalendar],
          }),
        });

        const calendar = useCalendar();
        await calendar.loadCalendars();

        const summary = calendar.calendars.value[0];
        expect(summary).toHaveProperty('id');
        expect(summary).toHaveProperty('title');
        expect(summary).toHaveProperty('dateRange');
        expect(summary).toHaveProperty('videoCount');
        expect(summary).toHaveProperty('status');
        expect(summary).not.toHaveProperty('startDate'); // CalendarSummary excludes these
      });
    });

    describe('Failed load', () => {
      it('should handle unauthorized error', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 401,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'Unauthorized',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.loadCalendars();

        expect(result.success).toBe(false);
        expect(result.error).toBe('Unauthorized');
      });

      it('should handle network errors', async () => {
        (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

        const calendar = useCalendar();
        const result = await calendar.loadCalendars();

        expect(result.success).toBe(false);
        expect(result.error).toBe('Network error');
      });
    });
  });

  /**
   * Test Suite: getCalendar()
   *
   * Tests fetching single calendar details.
   */
  describe('getCalendar', () => {
    const calendarId = 'cal-123';

    describe('Successful fetch', () => {
      it('should fetch calendar by ID successfully', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendar: mockCalendar,
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.getCalendar(calendarId);

        expect(result.success).toBe(true);
        expect(result.data).toEqual(mockCalendar);

        // Verify API call
        expect(global.fetch).toHaveBeenCalledWith(
          API_ENDPOINTS.CALENDAR_BY_ID(calendarId),
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer mock-token',
            }),
          })
        );

        // Verify currentCalendar state updated
        expect(calendar.currentCalendar.value).toEqual(mockCalendar);
      });
    });

    describe('Failed fetch', () => {
      it('should handle calendar not found', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 404,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'Calendar not found',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.getCalendar('non-existent');

        expect(result.success).toBe(false);
        expect(result.error).toBe('Calendar not found');
      });

      it('should handle unauthorized access', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 403,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'You do not have permission to access this calendar',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.getCalendar(calendarId);

        expect(result.success).toBe(false);
        expect(result.error).toContain('permission');
      });
    });
  });

  /**
   * Test Suite: updateCalendar()
   *
   * Tests updating calendar data.
   */
  describe('updateCalendar', () => {
    const calendarId = 'cal-123';
    const updateData = {
      title: 'Updated Calendar Title',
    };

    describe('Successful update', () => {
      it('should update calendar successfully', async () => {
        const updatedCalendar = { ...mockCalendar, title: updateData.title };

        // First load calendar list
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendars: [mockCalendar],
          }),
        });

        const calendar = useCalendar();
        await calendar.loadCalendars();

        // Then update
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendar: updatedCalendar,
          }),
        });

        const result = await calendar.updateCalendar(calendarId, updateData);

        expect(result.success).toBe(true);
        expect(result.data?.title).toBe(updateData.title);

        // Verify API call
        expect(global.fetch).toHaveBeenCalledWith(
          API_ENDPOINTS.CALENDAR_UPDATE(calendarId),
          expect.objectContaining({
            method: 'PUT',
            body: JSON.stringify(updateData),
          })
        );

        // Verify state updated
        expect(calendar.calendars.value[0].title).toBe(updateData.title);
      });

      it('should update currentCalendar if it matches', async () => {
        const updatedCalendar = { ...mockCalendar, title: updateData.title };

        // Set current calendar
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendar: mockCalendar,
          }),
        });

        const calendar = useCalendar();
        await calendar.getCalendar(calendarId);

        // Update
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendar: updatedCalendar,
          }),
        });

        await calendar.updateCalendar(calendarId, updateData);

        expect(calendar.currentCalendar.value?.title).toBe(updateData.title);
      });
    });

    describe('Failed update', () => {
      it('should handle validation errors', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 400,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'Title is required',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.updateCalendar(calendarId, { title: '' });

        expect(result.success).toBe(false);
        expect(result.error).toContain('required');
      });
    });
  });

  /**
   * Test Suite: deleteCalendar()
   *
   * Tests calendar deletion.
   */
  describe('deleteCalendar', () => {
    const calendarId = 'cal-123';

    describe('Successful deletion', () => {
      it('should delete calendar successfully', async () => {
        // Load calendars first
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendars: [mockCalendar, { ...mockCalendar, id: 'cal-456' }],
          }),
        });

        const calendar = useCalendar();
        await calendar.loadCalendars();
        expect(calendar.calendarCount.value).toBe(2);

        // Delete calendar
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 204,
          headers: new Headers({}),
        });

        const result = await calendar.deleteCalendar(calendarId);

        expect(result.success).toBe(true);

        // Verify API call
        expect(global.fetch).toHaveBeenCalledWith(
          API_ENDPOINTS.CALENDAR_DELETE(calendarId),
          expect.objectContaining({
            method: 'DELETE',
          })
        );

        // Verify removed from state
        expect(calendar.calendarCount.value).toBe(1);
        expect(calendar.calendars.value.find((c) => c.id === calendarId)).toBeUndefined();
      });

      it('should clear currentCalendar if deleted calendar matches', async () => {
        // Set current calendar
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({
            'content-type': 'application/json',
            'content-length': '500',
          }),
          json: async () => ({
            success: true,
            calendar: mockCalendar,
          }),
        });

        const calendar = useCalendar();
        await calendar.getCalendar(calendarId);
        expect(calendar.currentCalendar.value).not.toBeNull();

        // Delete
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 204,
          headers: new Headers({}),
        });

        await calendar.deleteCalendar(calendarId);
        expect(calendar.currentCalendar.value).toBeNull();
      });
    });

    describe('Failed deletion', () => {
      it('should handle calendar not found', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 404,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'Calendar not found',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.deleteCalendar('non-existent');

        expect(result.success).toBe(false);
        expect(result.error).toBe('Calendar not found');
      });

      it('should handle unauthorized deletion', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 403,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({
            error: 'You do not have permission to delete this calendar',
          }),
        });

        const calendar = useCalendar();
        const result = await calendar.deleteCalendar(calendarId);

        expect(result.success).toBe(false);
        expect(result.error).toContain('permission');
      });
    });
  });

  /**
   * Test Suite: clearCalendarData()
   *
   * Tests data cleanup utility (used on logout).
   */
  describe('clearCalendarData', () => {
    it('should clear all calendar state', async () => {
      // Load calendars
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'content-type': 'application/json',
          'content-length': '500',
        }),
        json: async () => ({
          success: true,
          calendars: [mockCalendar],
        }),
      });

      const calendar = useCalendar();
      await calendar.loadCalendars();
      expect(calendar.hasCalendars.value).toBe(true);

      // Clear data
      calendar.clearCalendarData();

      expect(calendar.calendars.value).toHaveLength(0);
      expect(calendar.currentCalendar.value).toBeNull();
      expect(calendar.isLoading.value).toBe(false);
      expect(calendar.hasCalendars.value).toBe(false);
    });
  });

  /**
   * Integration Tests
   *
   * Test complete calendar management flows.
   */
  describe('Integration scenarios', () => {
    it('should handle complete calendar lifecycle', async () => {
      const calendar = useCalendar();

      // 1. Create calendar
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        headers: new Headers({
          'content-type': 'application/json',
          'content-length': '500',
        }),
        json: async () => ({
          success: true,
          calendar: mockCalendar,
        }),
      });

      await calendar.createCalendar(mockCalendarCreateData);
      expect(calendar.calendarCount.value).toBe(1);

      // 2. Update calendar
      const updatedCalendar = { ...mockCalendar, title: 'Updated Title' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'content-type': 'application/json',
          'content-length': '500',
        }),
        json: async () => ({
          success: true,
          calendar: updatedCalendar,
        }),
      });

      await calendar.updateCalendar(mockCalendar.id, { title: 'Updated Title' });
      expect(calendar.calendars.value[0].title).toBe('Updated Title');

      // 3. Delete calendar
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Headers({}),
      });

      await calendar.deleteCalendar(mockCalendar.id);
      expect(calendar.calendarCount.value).toBe(0);
    });
  });
});
