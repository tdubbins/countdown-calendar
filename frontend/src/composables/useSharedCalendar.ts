import { ref } from 'vue';
import { API_ENDPOINTS } from '@/config/api';
import API_CONFIG from '@/config/api';

// Shared Calendar Types
export interface SharedCalendarDay {
  dayNumber: number;
  isUnlocked: boolean;
  hasVideo?: boolean; // Whether this day has a video uploaded
  videoPath?: string;
  thumbnailPath?: string;
  thumbnailUrl?: string | null;
}

export interface SharedCalendar {
  id?: string;
  title: string;
  startDate?: string;
  duration: number;
  description?: string; // Optional calendar description/message
  theme: string;
  timezone?: string;
  doorOrder: 'sequential' | 'random';
  doorPositions?: number[] | null;
  days: SharedCalendarDay[];
  isOwner?: boolean; // True if authenticated user is calendar owner
  published?: boolean; // True if calendar is published
}

export interface SharedCalendarResponse {
  success: boolean;
  message?: string;
  calendar?: SharedCalendar;
}

/**
 * Composable for fetching and managing public calendar data
 * Used by public calendar viewer (no authentication required, but optional)
 */
export function useSharedCalendar() {
  const calendar = ref<SharedCalendar | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch public calendar by ID
   *
   * Optionally sends authentication token if user is logged in to detect
   * if the viewer is the calendar owner (for owner-only controls).
   *
   * @param calendarId - Calendar UUID
   */
  const fetchSharedCalendar = async (calendarId: string): Promise<void> => {
    loading.value = true;
    error.value = null;
    calendar.value = null;

    try {
      // Optionally get auth token from localStorage if user is logged in
      const authToken = localStorage.getItem('auth_token');

      // Build headers - include Authorization if token exists
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };

      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }

      const response = await fetch(API_ENDPOINTS.CALENDAR_BY_ID(calendarId), {
        method: 'GET',
        headers
      });

      if (!response.ok) {
        if (response.status === 404) {
          error.value = 'Calendar not found or not published.';
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
        // Convert relative thumbnail URLs to absolute URLs with authentication
        // Backend returns: "/api/calendars/{id}/videos/{day}/thumbnail"
        // Frontend needs: Authenticated blob URLs for images
        if (data.calendar.days) {
          // Fetch all thumbnails with authentication and convert to blob URLs
          const thumbnailPromises = data.calendar.days.map(async (day) => {
            if (day.thumbnailUrl && day.thumbnailUrl.startsWith('/api/')) {
              // Remove leading '/api' and prepend full BASE_URL
              const relativePath = day.thumbnailUrl.substring(4); // Remove '/api'
              const absoluteUrl = `${API_CONFIG.BASE_URL}${relativePath}`;

              try {
                // Fetch thumbnail with authentication
                const authToken = localStorage.getItem('auth_token');
                const headers: Record<string, string> = {};
                if (authToken) {
                  headers['Authorization'] = `Bearer ${authToken}`;
                }

                const response = await fetch(absoluteUrl, { headers });

                if (response.ok) {
                  // Convert to blob URL for authenticated image loading
                  const blob = await response.blob();
                  const blobUrl = URL.createObjectURL(blob);
                  console.log(`[DEBUG] Day ${day.dayNumber}: Thumbnail fetched with auth → blob URL`);
                  return {
                    ...day,
                    thumbnailUrl: blobUrl
                  };
                } else {
                  console.warn(`[DEBUG] Day ${day.dayNumber}: Thumbnail fetch failed:`, response.status);
                  return {
                    ...day,
                    thumbnailUrl: null
                  };
                }
              } catch (error) {
                console.error(`[DEBUG] Day ${day.dayNumber}: Thumbnail fetch error:`, error);
                return {
                  ...day,
                  thumbnailUrl: null
                };
              }
            }
            return day;
          });

          // Wait for all thumbnail fetches to complete
          data.calendar.days = await Promise.all(thumbnailPromises);
        }

        calendar.value = data.calendar;
      } else {
        error.value = data.message || 'Failed to load calendar';
      }
    } catch (err) {
      console.error('Error fetching public calendar:', err);
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
    if (calendar.value.doorOrder === 'random' && calendar.value.doorPositions) {
      return calendar.value.doorPositions;
    }

    // Default: Sequential order 1, 2, 3, ..., duration
    return Array.from({ length: calendar.value.duration }, (_, i) => i + 1);
  };

  return {
    calendar,
    loading,
    error,
    fetchSharedCalendar,
    getDoorDisplayOrder
  };
}
