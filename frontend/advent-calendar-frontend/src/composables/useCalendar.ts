import { ref, computed } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { API_ENDPOINTS } from '@/config/api';
import type { Calendar, CalendarSummary, CalendarCreateData, CalendarCreateResponse, CalendarListResponse, CalendarGetResponse, CalendarUpdateResponse } from '@/types/calendar';

// Global calendar state
const calendars = ref<CalendarSummary[]>([]);
const isLoading = ref(false);
const currentCalendar = ref<Calendar | null>(null);

export const useCalendar = () => {
  const { getAuthHeaders } = useAuth();
  
  // Computed properties
  const hasCalendars = computed(() => calendars.value.length > 0);
  const calendarCount = computed(() => calendars.value.length);
  
  // API call helper with error handling
  const makeApiCall = async <T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<{ success: boolean; data?: T; error?: string }> => {
    try {
      const response = await fetch(url, {
        headers: getAuthHeaders(),
        ...options,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || `Request failed with status ${response.status}`
        };
      }
      
      const data = await response.json();
      return {
        success: true,
        data: data
      };
      
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Network error occurred'
      };
    }
  };
  
  // Create a new calendar
  const createCalendar = async (calendarData: CalendarCreateData): Promise<{ success: boolean; calendar?: Calendar; error?: string }> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall<CalendarCreateResponse>(API_ENDPOINTS.CALENDARS_LIST(), {
        method: 'POST',
        body: JSON.stringify(calendarData),
      });
      
      if (result.success && result.data) {
        // Ensure calendars array is properly initialized
        if (!Array.isArray(calendars.value)) {
          calendars.value = [];
        }
        
        // Extract calendar data from the response (backend returns nested structure)
        const calendarData = result.data.calendar;
        
        // Add the new calendar to our local state
        const newCalendarSummary: CalendarSummary = {
          id: calendarData.id,
          title: calendarData.title,
          dateRange: calendarData.dateRange,
          videoCount: calendarData.videoCount,
          status: calendarData.status
        };
        
        calendars.value.unshift(newCalendarSummary); // Add to beginning of list
        
        return {
          success: true,
          calendar: calendarData
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
  const loadCalendars = async (): Promise<{ success: boolean; error?: string }> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall<CalendarListResponse>(API_ENDPOINTS.CALENDARS_LIST());
      
      if (result.success && result.data) {
        // Convert full Calendar objects to CalendarSummary for state management
        const calendarSummaries: CalendarSummary[] = result.data.calendars.map(calendar => ({
          id: calendar.id,
          title: calendar.title,
          dateRange: calendar.dateRange,
          videoCount: calendar.videoCount,
          status: calendar.status
        }));
        
        calendars.value = calendarSummaries;
        return { success: true };
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
  const getCalendar = async (calendarId: string): Promise<{ success: boolean; calendar?: Calendar; error?: string }> => {
    isLoading.value = true;
    
    try {
      const result = await makeApiCall<CalendarGetResponse>(API_ENDPOINTS.CALENDAR_BY_ID(calendarId));
      
      if (result.success && result.data) {
        currentCalendar.value = result.data.calendar;
        return {
          success: true,
          calendar: result.data.calendar
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
  const updateCalendar = async (calendarId: string, updateData: Partial<CalendarCreateData>): Promise<{ success: boolean; calendar?: Calendar; error?: string }> => {
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
            status: result.data.calendar.status
          };
        }
        
        // Update current calendar if it's the same one
        if (currentCalendar.value?.id === calendarId) {
          currentCalendar.value = result.data.calendar;
        }
        
        return {
          success: true,
          calendar: result.data.calendar
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
  const deleteCalendar = async (calendarId: string): Promise<{ success: boolean; error?: string }> => {
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
  
  // Clear all calendar data (for logout)
  const clearCalendarData = () => {
    calendars.value = [];
    currentCalendar.value = null;
    isLoading.value = false;
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
    clearCalendarData
  };
};