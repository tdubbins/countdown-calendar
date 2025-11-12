import { ref } from 'vue';
import { API_ENDPOINTS } from '@/config/api';

// Shared Calendar Types
export interface SharedCalendarDay {
  day_number: number;
  is_unlocked: boolean;
  video_path?: string;
  thumbnail_path?: string;
}

export interface SharedCalendar {
  id: string;
  title: string;
  start_date: string;
  duration: number;
  description?: string; // Optional calendar description/message
  theme: string;
  timezone: string;
  door_order: 'sequential' | 'random';
  door_positions?: number[];
  days: SharedCalendarDay[];
}

export interface SharedCalendarResponse {
  success: boolean;
  message?: string;
  calendar?: SharedCalendar;
}

/**
 * Composable for fetching and managing shared calendar data
 * Used by public shared calendar viewer (no authentication required)
 */
export function useSharedCalendar() {
  const calendar = ref<SharedCalendar | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch shared calendar by token
   * @param token - Share token UUID
   */
  const fetchSharedCalendar = async (token: string): Promise<void> => {
    loading.value = true;
    error.value = null;
    calendar.value = null;

    try {
      // Validate token format (basic UUID check)
      if (!isValidUUID(token)) {
        error.value = 'Invalid share link format';
        loading.value = false;
        return;
      }

      const response = await fetch(API_ENDPOINTS.SHARED_CALENDAR(token), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          error.value = 'Calendar not found. It may have been deleted.';
        } else if (response.status === 429) {
          error.value = 'Too many requests. Please try again later.';
        } else {
          error.value = 'Failed to load calendar. Please try again.';
        }
        loading.value = false;
        return;
      }

      const data: SharedCalendarResponse = await response.json();

      if (data.success && data.calendar) {
        calendar.value = data.calendar;
      } else {
        error.value = data.message || 'Failed to load calendar';
      }
    } catch (err) {
      console.error('Error fetching shared calendar:', err);
      error.value = 'Network error. Please check your connection.';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Get the display order of days based on door_order setting (Issue #81)
   *
   * This function determines how doors appear to viewers in the shared calendar:
   * - Random: Returns shuffled door_positions array (e.g., [15, 3, 24, 1, ...])
   * - Sequential: Returns ordered array [1, 2, 3, ..., duration]
   *
   * The display order is set by the calendar creator via DoorOrderToggle component
   * and locked after sharing to ensure consistent viewer experience.
   *
   * @returns Array of day numbers in display order
   *
   * @example
   * // Sequential order (default)
   * getDoorDisplayOrder() // [1, 2, 3, 4, ..., 24]
   *
   * // Random order (shuffled by creator)
   * getDoorDisplayOrder() // [15, 3, 24, 1, 7, ...] (based on door_positions)
   */
  const getDoorDisplayOrder = (): number[] => {
    if (!calendar.value) return [];

    // Issue #81: Check if random ordering is enabled with shuffled positions
    if (calendar.value.door_order === 'random' && calendar.value.door_positions) {
      return calendar.value.door_positions;
    }

    // Default: Sequential order 1, 2, 3, ..., duration
    return Array.from({ length: calendar.value.duration }, (_, i) => i + 1);
  };

  /**
   * Basic UUID v4 format validation
   */
  const isValidUUID = (uuid: string): boolean => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
  };

  return {
    calendar,
    loading,
    error,
    fetchSharedCalendar,
    getDoorDisplayOrder
  };
}
