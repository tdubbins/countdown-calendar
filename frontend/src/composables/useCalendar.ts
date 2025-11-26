import { ref, computed } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { API_ENDPOINTS } from '@/config/api';
import type { Calendar, CalendarSummary, CalendarCreateData, CalendarUpdateData, CalendarCreateResponse, CalendarListResponse, CalendarGetResponse, CalendarUpdateResponse } from '@/types/calendar';

// Global calendar state
const calendars = ref<CalendarSummary[]>([]);
const isLoading = ref(false);
const currentCalendar = ref<Calendar | null>(null);

// Standalone function to clear calendar data (exported to avoid circular dependency with useAuth)
export const clearCalendarData = () => {
  calendars.value = [];
  currentCalendar.value = null;
  isLoading.value = false;
};

// Types for API responses following existing patterns
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

export const useCalendar = () => {
  const { getAuthHeaders } = useAuth();
  
  // Computed properties
  const hasCalendars = computed(() => calendars.value.length > 0);
  const calendarCount = computed(() => calendars.value.length);
  
  // Helper function to check if response has content
  const hasResponseContent = (response: Response): boolean => {
    const contentType = response.headers.get('content-type');
    return response.status !== 204 && 
           response.headers.get('content-length') !== '0' &&
           (contentType?.includes('application/json') ?? false);
  };
  
  // Helper function to parse error response
  const parseErrorResponse = async (response: Response): Promise<string> => {
    try {
      const errorData = await response.json();
      return errorData.error || `Request failed with status ${response.status}`;
    } catch {
      return `Request failed with status ${response.status}: ${response.statusText}`;
    }
  };
  
  // Helper function to parse success response
  const parseSuccessResponse = async <T>(response: Response): Promise<T | undefined> => {
    if (!hasResponseContent(response)) {
      return undefined;
    }
    
    try {
      return await response.json();
    } catch {
      return undefined;
    }
  };
  
  // Clean API call helper with proper error handling
  const makeApiCall = async <T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> => {
    try {
      const response = await fetch(url, {
        headers: getAuthHeaders(),
        ...options,
      });
      
      // Handle error responses
      if (!response.ok) {
        const error = await parseErrorResponse(response);
        return { success: false, error };
      }
      
      // Handle successful responses
      const data = await parseSuccessResponse<T>(response);
      return { success: true, data };
      
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Network error occurred'
      };
    }
  };
  
  // Calendar operations with consistent return types
  const createCalendar = async (calendarData: CalendarCreateData): Promise<ApiResponse<Calendar>> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall<CalendarCreateResponse>(API_ENDPOINTS.CALENDARS_LIST(), {
        method: 'POST',
        body: JSON.stringify(calendarData),
      });
      
      if (result.success && result.data) {
        if (!Array.isArray(calendars.value)) {
          calendars.value = [];
        }

        const calendarData = result.data.calendar;

        const newCalendarSummary: CalendarSummary = {
          id: calendarData.id,
          title: calendarData.title,
          dateRange: calendarData.dateRange,
          videoCount: calendarData.videoCount,
          status: calendarData.status,
          published: calendarData.published
        };
        
        calendars.value.unshift(newCalendarSummary); // Add to beginning of list
        
        return {
          success: true,
          data: calendarData
        };
      } else {
        return {
          success: false,
          error: result.error || 'Failed to create calendar'
        };
      }
      
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to create calendar'
      };
    } finally {
      isLoading.value = false;
    }
  };
  
  // Get all calendars for the current user
  const loadCalendars = async (): Promise<ApiResponse<CalendarSummary[]>> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall<CalendarListResponse>(API_ENDPOINTS.CALENDARS_LIST());
      
      if (result.success && result.data) {
        // Convert full Calendar objects to CalendarSummary for state management
        const calendarSummaries: CalendarSummary[] = result.data.calendars.map(calendar => ({
          id: calendar.id,
          title: calendar.title,
          startDate: calendar.startDate,
          endDate: calendar.endDate,
          dateRange: calendar.dateRange,
          videoCount: calendar.videoCount,
          status: calendar.status,
          published: calendar.published  // Include published status
        }));
        
        calendars.value = calendarSummaries;
        return { success: true, data: calendarSummaries };
      } else {
        return {
          success: false,
          error: result.error || 'Failed to load calendars'
        };
      }
      
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to load calendars'
      };
    } finally {
      isLoading.value = false;
    }
  };
  
  // Get a specific calendar by ID
  const getCalendar = async (calendarId: string): Promise<ApiResponse<Calendar>> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall<CalendarGetResponse>(API_ENDPOINTS.CALENDAR_BY_ID(calendarId));
      
      if (result.success && result.data) {
        currentCalendar.value = result.data.calendar;
        return {
          success: true,
          data: result.data.calendar
        };
      } else {
        return {
          success: false,
          error: result.error || 'Calendar not found'
        };
      }
      
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to load calendar'
      };
    } finally {
      isLoading.value = false;
    }
  };
  
  // Update a calendar
  const updateCalendar = async (calendarId: string, updateData: CalendarUpdateData): Promise<ApiResponse<Calendar>> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall<CalendarUpdateResponse>(API_ENDPOINTS.CALENDAR_UPDATE(calendarId), {
        method: 'PUT',
        body: JSON.stringify(updateData),
      });
      
      if (result.success && result.data) {
        // Update the calendar in our local state
        const index = calendars.value.findIndex(cal => cal.id === calendarId);
        if (index !== -1) {
          calendars.value[index] = {
            id: result.data.calendar.id,
            title: result.data.calendar.title,
            dateRange: result.data.calendar.dateRange,
            videoCount: result.data.calendar.videoCount,
            status: result.data.calendar.status,
            published: result.data.calendar.published
          };
        }
        
        // Update current calendar if it's the same one
        if (currentCalendar.value?.id === calendarId) {
          currentCalendar.value = result.data.calendar;
        }
        
        return {
          success: true,
          data: result.data.calendar
        };
      } else {
        return {
          success: false,
          error: result.error || 'Failed to update calendar'
        };
      }
      
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to update calendar'
      };
    } finally {
      isLoading.value = false;
    }
  };
  
  // Delete a calendar
  const deleteCalendar = async (calendarId: string): Promise<ApiResponse<void>> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall(API_ENDPOINTS.CALENDAR_DELETE(calendarId), {
        method: 'DELETE',
      });
      
      if (result.success) {
        // Remove from local state
        calendars.value = calendars.value.filter(cal => cal.id !== calendarId);
        
        // Clear current calendar if it was deleted
        if (currentCalendar.value?.id === calendarId) {
          currentCalendar.value = null;
        }
        
        return { success: true };
      } else {
        return {
          success: false,
          error: result.error || 'Failed to delete calendar'
        };
      }
      
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to delete calendar'
      };
    } finally {
      isLoading.value = false;
    }
  };
  
  // Publish calendar (make it publicly accessible)
  const publishCalendar = async (calendarId: string): Promise<ApiResponse<void>> => {
    isLoading.value = true;

    try {
      const result = await makeApiCall<{ success: boolean; message: string }>(
        API_ENDPOINTS.CALENDAR_PUBLISH(calendarId),
        {
          method: 'POST',
        }
      );

      if (result.success) {
        // Update current calendar's published status if it's loaded
        if (currentCalendar.value?.id === calendarId) {
          currentCalendar.value.published = true;
        }

        return {
          success: true,
          data: undefined
        };
      } else {
        return {
          success: false,
          error: result.error || 'Failed to publish calendar'
        };
      }

    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to publish calendar'
      };
    } finally {
      isLoading.value = false;
    }
  };

  // Unpublish calendar (make it private again)
  const unpublishCalendar = async (calendarId: string): Promise<ApiResponse<void>> => {
    isLoading.value = true;

    try {
      const result = await makeApiCall<{ success: boolean; message: string }>(
        API_ENDPOINTS.CALENDAR_UNPUBLISH(calendarId),
        {
          method: 'POST',
        }
      );

      if (result.success) {
        // Update current calendar's published status if it's loaded
        if (currentCalendar.value?.id === calendarId) {
          currentCalendar.value.published = false;
        }

        return {
          success: true,
          data: undefined
        };
      } else {
        return {
          success: false,
          error: result.error || 'Failed to unpublish calendar'
        };
      }

    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to unpublish calendar'
      };
    } finally {
      isLoading.value = false;
    }
  };

  return {
    // State
    calendars: computed(() => calendars.value),
    currentCalendar: computed(() => currentCalendar.value),
    isLoading: computed(() => isLoading.value),
    hasCalendars,
    calendarCount,

    // Actions
    createCalendar,
    loadCalendars,
    getCalendar,
    updateCalendar,
    deleteCalendar,
    publishCalendar,
    unpublishCalendar,
    clearCalendarData
  };
};