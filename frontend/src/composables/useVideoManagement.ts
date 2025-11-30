import { ref } from 'vue';
import { useAuth } from '@/composables/useAuth';
import API_CONFIG from '@/config/api';

// Video status interface
export interface VideoStatus {
  day: number;
  status: 'empty' | 'uploading' | 'processing' | 'pending' | 'completed' | 'failed';
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

// Reassign response type
export interface ReassignResult {
  swapped: boolean;
  sourceDay: {
    day: number;
    status: 'empty' | 'completed';
    filename?: string;
  };
  targetDay: {
    day: number;
    status: 'completed';
    filename?: string;
  };
}

export const useVideoManagement = (calendarId: string) => {
  const { getAuthHeaders } = useAuth();

  // Day statuses map
  const dayStatuses = ref<Map<number, VideoStatus>>(new Map());
  const isLoading = ref(false);
  const uploadProgress = ref(0);
  const isUploading = ref(false);

  // Polling state (per-composable instance)
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

      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos`,
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
      for (const video of videos) {
        const status: VideoStatus = {
          day: video.day,
          status: video.status || 'completed',
          thumbnailUrl: undefined, // Will be loaded separately
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

        // Load thumbnail as data URL if video has one (run in background)
        if (video.thumbnail && (video.status === 'completed' || !video.status)) {
          // Don't await - load thumbnails in parallel
          loadThumbnailAsDataUrl(video.day);
        }
      }

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
   * Load thumbnail as base64 data URL (fixes auth issue with img tags)
   * Skips loading if thumbnail is already cached
   */
  const loadThumbnailAsDataUrl = async (day: number): Promise<void> => {
    try {
      // Skip if thumbnail already loaded
      const currentStatus = dayStatuses.value.get(day);
      if (currentStatus?.thumbnailUrl) {
        return;
      }

      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos/${day}/thumbnail`,
        {
          method: 'GET',
          headers
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const dataUrl = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result as string);
          reader.readAsDataURL(blob);
        });

        // Update thumbnail URL with data URL
        const currentStatus = dayStatuses.value.get(day);
        if (currentStatus) {
          dayStatuses.value.set(day, {
            ...currentStatus,
            thumbnailUrl: dataUrl
          });
        }
      }
      // Silently ignore 404s - thumbnail may not be ready yet
    } catch (error) {
      // Silently ignore errors - thumbnail loading is non-critical
    }
  };

  /**
   * Poll video status for a specific day (legacy - kept for compatibility)
   * GET /api/calendars/{id}/videos/{day}/status
   */
  const pollVideoStatus = async (day: number): Promise<void> => {
    try {
      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos/${day}/status`,
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

          // Load thumbnail for completed video
          if (data.status === 'completed') {
            await loadThumbnailAsDataUrl(day);
          }
        }
      }

    } catch (error) {
      console.error(`Failed to poll status for day ${day}:`, error);
    }
  };

  /**
   * Poll all video statuses in a single batch request
   * GET /api/calendars/{id}/videos/status
   * Only processes days that are actively being polled (processing/pending)
   */
  const pollAllStatuses = async (): Promise<void> => {
    try {
      // Skip if nothing to poll
      if (activePollDays.value.size === 0) {
        return;
      }

      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos/status`,
        {
          method: 'GET',
          headers
        }
      );

      if (!response.ok) {
        throw new Error('Failed to get video statuses');
      }

      const data = await response.json();
      const statuses = data.statuses || {};

      // Only process days that are actively being polled
      for (const day of activePollDays.value) {
        const statusData = statuses[day.toString()];
        if (!statusData) continue;

        const status = statusData as { status: string; progress?: number; error?: string };
        const currentStatus = dayStatuses.value.get(day);

        if (currentStatus) {
          const updatedStatus: VideoStatus = {
            ...currentStatus,
            status: status.status as VideoStatus['status'],
            progress: status.progress || 0,
            error: status.error
          };

          dayStatuses.value.set(day, updatedStatus);

          // Stop polling if completed or failed
          if (status.status === 'completed' || status.status === 'failed') {
            activePollDays.value.delete(day);

            // Load thumbnail for newly completed video (only once)
            if (status.status === 'completed') {
              loadThumbnailAsDataUrl(day);
            }
          }
        }
      }

    } catch (error) {
      console.error('Failed to poll all statuses:', error);
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

      // Use batch endpoint for efficiency (1 request instead of N)
      await pollAllStatuses();

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
        isUploading.value = false;
        uploadProgress.value = 0;

        if (xhr.status === 201) {
          try {
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

      xhr.open('POST', `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos`);
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
        `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos/${day}`,
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
        `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos/${day}`,
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
   * Reassign video from one day to another (move or swap)
   * POST /api/calendars/{id}/videos/reassign
   *
   * @param sourceDay Day to move video from
   * @param targetDay Day to move video to
   * @returns Promise with reassign result
   */
  const reassignVideo = async (
    sourceDay: number,
    targetDay: number
  ): Promise<ApiResponse<ReassignResult>> => {
    try {
      const headers = getAuthHeaders();

      const response = await fetch(
        `${API_CONFIG.BASE_URL}/calendars/${calendarId}/videos/reassign`,
        {
          method: 'POST',
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ sourceDay, targetDay })
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to reassign video'
        };
      }

      const data = await response.json();

      // Update local day statuses based on result
      const sourceStatus = dayStatuses.value.get(sourceDay);
      const targetStatus = dayStatuses.value.get(targetDay);

      if (data.swapped) {
        // Swap: exchange statuses and cached thumbnails (no network requests needed)
        if (sourceStatus && targetStatus) {
          const sourceThumbnail = sourceStatus.thumbnailUrl;
          const targetThumbnail = targetStatus.thumbnailUrl;

          dayStatuses.value.set(sourceDay, {
            ...targetStatus,
            day: sourceDay,
            thumbnailUrl: targetThumbnail
          });
          dayStatuses.value.set(targetDay, {
            ...sourceStatus,
            day: targetDay,
            thumbnailUrl: sourceThumbnail
          });
        }
      } else {
        // Move: source becomes empty, target gets the video with its thumbnail
        if (sourceStatus) {
          const sourceThumbnail = sourceStatus.thumbnailUrl;

          dayStatuses.value.set(targetDay, {
            ...sourceStatus,
            day: targetDay,
            thumbnailUrl: sourceThumbnail
          });
          dayStatuses.value.set(sourceDay, {
            day: sourceDay,
            status: 'empty',
            thumbnailUrl: undefined
          });
        }
      }

      return {
        success: true,
        data: {
          swapped: data.swapped,
          sourceDay: data.sourceDay,
          targetDay: data.targetDay
        }
      };

    } catch (error) {
      console.error('Failed to reassign video:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to reassign video'
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
    pollAllStatuses,
    startPolling,
    stopPolling,
    uploadVideo,
    getVideoMetadata,
    deleteVideo,
    reassignVideo,

    // Getters
    getDayStatus,
    getDayThumbnail,
    getDayProgress,
    getDayError,
    getFullDayStatus
  };
};
