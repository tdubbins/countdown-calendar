import { ref } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { API_BASE_URL } from '@/config/api';

// Video status interface
export interface VideoStatus {
  day: number;
  status: 'empty' | 'uploading' | 'processing' | 'completed' | 'failed';
  thumbnailUrl?: string;
  progress?: number;
  error?: string;
  filename?: string;
  size?: number;
  duration?: number;
  uploadedAt?: string;
}

// Video metadata from API
export interface VideoMetadata {
  day: number;
  filename: string;
  thumbnail: string;
  size: number;
  duration: number;
  uploaded_at: string;
  status: string;
  stream_url: string;
  thumbnail_url: string;
}

// API response types
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

export const useVideoManagement = (calendarId: string) => {
  const { getAuthHeaders } = useAuth();

  // Day statuses map
  const dayStatuses = ref<Map<number, VideoStatus>>(new Map());
  const isLoading = ref(false);
  const uploadProgress = ref(0);
  const isUploading = ref(false);

  // FIX BUG #2: Move polling state INSIDE composable (not global)
  const pollInterval = ref<number | null>(null);
  const activePollDays = ref<Set<number>>(new Set());

  /**
   * Initialize day statuses for calendar duration
   */
  const initializeDayStatuses = (duration: number): void => {
    const statusMap = new Map<number, VideoStatus>();
    for (let day = 1; day <= duration; day++) {
      statusMap.set(day, {
        day,
        status: 'empty'
      });
    }
    dayStatuses.value = statusMap;
  };

  /**
   * Load video statuses from API
   * GET /api/calendars/{id}/videos
   */
  const loadVideoStatuses = async (): Promise<ApiResponse> => {
    try {
      isLoading.value = true;

      // FIX BUG #1: Use getAuthHeaders() instead of localStorage directly
      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_BASE_URL}/calendars/${calendarId}/videos`,
        {
          method: 'GET',
          headers
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to load videos'
        };
      }

      const data = await response.json();
      const videos = data.videos || [];

      // Update status for days with videos
      videos.forEach((video: any) => {
        const status: VideoStatus = {
          day: video.day,
          status: video.status || 'completed',
          thumbnailUrl: video.thumbnail
            ? `${API_BASE_URL}/calendars/${calendarId}/videos/${video.day}/thumbnail`
            : undefined,
          filename: video.filename,
          size: video.size,
          duration: video.duration,
          uploadedAt: video.uploaded_at
        };

        dayStatuses.value.set(video.day, status);

        // If video is processing/pending, add to polling list
        if (status.status === 'processing' || status.status === 'pending') {
          activePollDays.value.add(video.day);
        }
      });

      // Start polling if there are active uploads
      if (activePollDays.value.size > 0) {
        startPolling();
      }

      return {
        success: true,
        data: videos
      };

    } catch (error) {
      console.error('Failed to load video statuses:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to load videos'
      };
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Poll video status for a specific day
   * GET /api/calendars/{id}/videos/{day}/status
   */
  const pollVideoStatus = async (day: number): Promise<void> => {
    try {
      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_BASE_URL}/calendars/${calendarId}/videos/${day}/status`,
        {
          method: 'GET',
          headers
        }
      );

      if (!response.ok) {
        // If 404, video might have been deleted
        if (response.status === 404) {
          activePollDays.value.delete(day);
          return;
        }
        throw new Error('Failed to get video status');
      }

      const data = await response.json();
      const currentStatus = dayStatuses.value.get(day);

      if (currentStatus) {
        const updatedStatus: VideoStatus = {
          ...currentStatus,
          status: data.status,
          progress: data.progress || 0,
          error: data.error
        };

        dayStatuses.value.set(day, updatedStatus);

        // Stop polling if completed or failed
        if (data.status === 'completed' || data.status === 'failed') {
          activePollDays.value.delete(day);

          // Reload full status to get thumbnail
          if (data.status === 'completed') {
            await loadVideoStatuses();
          }
        }
      }

    } catch (error) {
      console.error(`Failed to poll status for day ${day}:`, error);
    }
  };

  /**
   * Start polling for active uploads (every 3 seconds)
   */
  const startPolling = (): void => {
    if (pollInterval.value) return; // Already polling

    pollInterval.value = window.setInterval(async () => {
      if (activePollDays.value.size === 0) {
        stopPolling();
        return;
      }

      // Poll all active days
      const pollPromises = Array.from(activePollDays.value).map(day =>
        pollVideoStatus(day)
      );
      await Promise.all(pollPromises);

    }, 3000); // Poll every 3 seconds
  };

  /**
   * Stop polling
   */
  const stopPolling = (): void => {
    if (pollInterval.value) {
      clearInterval(pollInterval.value);
      pollInterval.value = null;
    }
  };

  /**
   * Upload video for a specific day
   * POST /api/calendars/{id}/videos
   */
  const uploadVideo = async (day: number, file: File): Promise<ApiResponse> => {
    return new Promise((resolve) => {
      isUploading.value = true;
      uploadProgress.value = 0;

      const headers = getAuthHeaders();
      const token = headers['Authorization']?.replace('Bearer ', '');

      if (!token) {
        // FIX BUG #5: Reset state on error
        isUploading.value = false;
        uploadProgress.value = 0;
        resolve({
          success: false,
          error: 'No authentication token found'
        });
        return;
      }

      // Create FormData
      const formData = new FormData();
      formData.append('video', file);
      formData.append('day', day.toString());

      // Upload with progress tracking using XMLHttpRequest
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          uploadProgress.value = Math.round((e.loaded / e.total) * 100);
        }
      });

      xhr.addEventListener('load', () => {
        // FIX BUG #3: Reset state in handlers
        isUploading.value = false;
        uploadProgress.value = 0;

        if (xhr.status === 201) {
          try {
            // FIX BUG #6: Wrap JSON.parse in try-catch
            const response = JSON.parse(xhr.responseText);

            // Update day status to processing
            const updatedStatus: VideoStatus = {
              day,
              status: 'processing',
              progress: 0
            };
            dayStatuses.value.set(day, updatedStatus);

            // Add to polling list
            activePollDays.value.add(day);
            startPolling();

            resolve({
              success: true,
              data: response
            });
          } catch (parseError) {
            console.error('Failed to parse upload response:', parseError);
            resolve({
              success: false,
              error: 'Invalid response from server'
            });
          }
        } else {
          try {
            const errorData = JSON.parse(xhr.responseText);
            resolve({
              success: false,
              error: errorData.error || 'Upload failed'
            });
          } catch (parseError) {
            resolve({
              success: false,
              error: `Upload failed with status ${xhr.status}`
            });
          }
        }
      });

      xhr.addEventListener('error', () => {
        // FIX BUG #5: Reset state on error
        isUploading.value = false;
        uploadProgress.value = 0;
        resolve({
          success: false,
          error: 'Network error during upload'
        });
      });

      xhr.addEventListener('abort', () => {
        // Handle abort case
        isUploading.value = false;
        uploadProgress.value = 0;
        resolve({
          success: false,
          error: 'Upload cancelled'
        });
      });

      xhr.open('POST', `${API_BASE_URL}/calendars/${calendarId}/videos`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);
    });
  };

  /**
   * Get video metadata for playback
   * GET /api/calendars/{id}/videos/{day}
   */
  const getVideoMetadata = async (day: number): Promise<ApiResponse<VideoMetadata>> => {
    try {
      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_BASE_URL}/calendars/${calendarId}/videos/${day}`,
        {
          method: 'GET',
          headers
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to get video metadata'
        };
      }

      const data = await response.json();

      return {
        success: true,
        data: data.video
      };

    } catch (error) {
      console.error('Failed to get video metadata:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get video metadata'
      };
    }
  };

  /**
   * Delete video for a specific day
   * DELETE /api/calendars/{id}/videos/{day}
   */
  const deleteVideo = async (day: number): Promise<ApiResponse> => {
    try {
      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_BASE_URL}/calendars/${calendarId}/videos/${day}`,
        {
          method: 'DELETE',
          headers
        }
      );

      if (!response.ok) {
        // Handle 204 No Content correctly
        if (response.status === 204) {
          // Success - no content
          dayStatuses.value.set(day, {
            day,
            status: 'empty'
          });

          // Remove from polling if active
          activePollDays.value.delete(day);

          return {
            success: true
          };
        }

        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to delete video'
        };
      }

      // Update day status to empty
      dayStatuses.value.set(day, {
        day,
        status: 'empty'
      });

      // Remove from polling if active
      activePollDays.value.delete(day);

      return {
        success: true
      };

    } catch (error) {
      console.error('Failed to delete video:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete video'
      };
    }
  };

  /**
   * Get day status
   */
  const getDayStatus = (day: number): VideoStatus['status'] => {
    return dayStatuses.value.get(day)?.status || 'empty';
  };

  /**
   * Get day thumbnail URL
   */
  const getDayThumbnail = (day: number): string | undefined => {
    return dayStatuses.value.get(day)?.thumbnailUrl;
  };

  /**
   * Get day progress
   */
  const getDayProgress = (day: number): number | undefined => {
    return dayStatuses.value.get(day)?.progress;
  };

  /**
   * Get day error message
   */
  const getDayError = (day: number): string | undefined => {
    return dayStatuses.value.get(day)?.error;
  };

  /**
   * Get full day status object
   */
  const getFullDayStatus = (day: number): VideoStatus | undefined => {
    return dayStatuses.value.get(day);
  };

  return {
    // State
    dayStatuses,
    isLoading,
    uploadProgress,
    isUploading,
    activePollDays,

    // Methods
    initializeDayStatuses,
    loadVideoStatuses,
    pollVideoStatus,
    startPolling,
    stopPolling,
    uploadVideo,
    getVideoMetadata,
    deleteVideo,

    // Getters
    getDayStatus,
    getDayThumbnail,
    getDayProgress,
    getDayError,
    getFullDayStatus
  };
};
