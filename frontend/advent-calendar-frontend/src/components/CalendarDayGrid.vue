<template>
  <div class="calendar-day-grid-container">
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-section">
      <ion-spinner name="crescent" color="primary"></ion-spinner>
      <p class="loading-text">Loading calendar days...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="loadError" class="error-section" role="alert">
      <ion-icon :icon="alertCircleOutline" class="error-icon"></ion-icon>
      <p class="error-message">{{ loadError }}</p>
      <ion-button
        fill="outline"
        color="primary"
        size="small"
        @click="loadVideoStatuses"
      >
        Try Again
      </ion-button>
    </div>

    <!-- Day Grid -->
    <div v-else class="day-grid" role="grid" :aria-label="`Calendar with ${duration} days`">
      <CalendarDayCard
        v-for="day in duration"
        :key="day"
        :day="day"
        :status="getDayStatus(day)"
        :thumbnail-url="getDayThumbnail(day)"
        :progress="getDayProgress(day)"
        :error-message="getDayError(day)"
        @click="handleDayClick(day)"
      />
    </div>

    <!-- Upload Modal -->
    <ion-modal
      :is-open="isUploadModalOpen"
      @didDismiss="closeUploadModal"
      :initial-breakpoint="0.9"
      :breakpoints="[0, 0.5, 0.9]"
    >
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>Upload Video - Day {{ selectedDay }}</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="closeUploadModal" color="light">
              <strong>Close</strong>
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="modal-content">
        <div class="upload-modal-body">
          <!-- Video Upload Component -->
          <VideoUpload
            v-if="selectedDay"
            :day="selectedDay"
            :disabled="isUploading"
            @videoSelected="handleVideoSelected"
          />

          <!-- Upload Progress -->
          <div v-if="isUploading" class="upload-progress-section">
            <div class="progress-header">
              <ion-icon :icon="cloudUploadOutline" class="progress-icon"></ion-icon>
              <p class="progress-title">Uploading video...</p>
            </div>
            <ion-progress-bar :value="uploadProgress / 100" color="primary"></ion-progress-bar>
            <p class="progress-text">{{ uploadProgress }}% complete</p>
          </div>

          <!-- Upload Actions -->
          <div class="upload-actions">
            <ion-button
              expand="block"
              color="primary"
              :disabled="!selectedFile || isUploading"
              @click="handleUploadConfirm"
            >
              <ion-icon slot="start" :icon="cloudUploadOutline"></ion-icon>
              {{ isUploading ? 'Uploading...' : 'Upload Video' }}
            </ion-button>
          </div>
        </div>
      </ion-content>
    </ion-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import {
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonIcon,
  IonModal,
  IonProgressBar,
  IonSpinner,
  IonTitle,
  IonToolbar,
  toastController
} from '@ionic/vue';
import {
  alertCircleOutline,
  cloudUploadOutline
} from 'ionicons/icons';
import CalendarDayCard from '@/components/CalendarDayCard.vue';
import VideoUpload from '@/components/VideoUpload.vue';
import { API_BASE_URL } from '@/config/api';

// Props
interface Props {
  calendarId: string;
  duration: number; // 1-31 days
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
  'uploadComplete': [day: number];
  'uploadError': [day: number, error: string];
}>();

// Day status tracking
interface DayStatus {
  day: number;
  status: 'empty' | 'uploading' | 'processing' | 'completed' | 'failed';
  thumbnailUrl?: string;
  progress?: number;
  error?: string;
  filename?: string;
}

// Reactive state
const dayStatuses = ref<Map<number, DayStatus>>(new Map());
const isLoading = ref(true);
const loadError = ref<string>('');

// Modal state
const isUploadModalOpen = ref(false);
const selectedDay = ref<number | null>(null);
const selectedFile = ref<File | null>(null);
const selectedDuration = ref<number>(0);

// Upload state
const isUploading = ref(false);
const uploadProgress = ref(0);

// Polling state
const pollInterval = ref<number | null>(null);
const activePollDays = ref<Set<number>>(new Set());

// Initialize day statuses (all empty by default)
const initializeDayStatuses = () => {
  const statusMap = new Map<number, DayStatus>();
  for (let day = 1; day <= props.duration; day++) {
    statusMap.set(day, {
      day,
      status: 'empty'
    });
  }
  dayStatuses.value = statusMap;
};

// Get day status
const getDayStatus = (day: number): DayStatus['status'] => {
  return dayStatuses.value.get(day)?.status || 'empty';
};

const getDayThumbnail = (day: number): string | undefined => {
  return dayStatuses.value.get(day)?.thumbnailUrl;
};

const getDayProgress = (day: number): number | undefined => {
  return dayStatuses.value.get(day)?.progress;
};

const getDayError = (day: number): string | undefined => {
  return dayStatuses.value.get(day)?.error;
};

// Load video statuses from API
const loadVideoStatuses = async () => {
  try {
    isLoading.value = true;
    loadError.value = '';

    // Initialize all days as empty first
    initializeDayStatuses();

    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    const response = await fetch(
      `${API_BASE_URL}/calendars/${props.calendarId}/videos`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to load videos');
    }

    const data = await response.json();
    const videos = data.videos || [];

    // Update status for days with videos
    videos.forEach((video: any) => {
      const status: DayStatus = {
        day: video.day,
        status: video.status || 'completed',
        thumbnailUrl: video.thumbnail
          ? `${API_BASE_URL}/calendars/${props.calendarId}/videos/${video.day}/thumbnail`
          : undefined,
        filename: video.filename
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

  } catch (error) {
    console.error('Failed to load video statuses:', error);
    loadError.value = error instanceof Error ? error.message : 'Failed to load calendar days';
  } finally {
    isLoading.value = false;
  }
};

// Poll for video status updates
const pollVideoStatus = async (day: number) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const response = await fetch(
      `${API_BASE_URL}/calendars/${props.calendarId}/videos/${day}/status`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      // If 404, video might have been deleted or doesn't exist
      if (response.status === 404) {
        activePollDays.value.delete(day);
        return;
      }
      throw new Error('Failed to get video status');
    }

    const data = await response.json();
    const currentStatus = dayStatuses.value.get(day);

    if (currentStatus) {
      const updatedStatus: DayStatus = {
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
          emit('uploadComplete', day);
        } else if (data.status === 'failed') {
          emit('uploadError', day, data.error || 'Video processing failed');
        }
      }
    }

  } catch (error) {
    console.error(`Failed to poll status for day ${day}:`, error);
  }
};

// Start polling for active uploads
const startPolling = () => {
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

// Stop polling
const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value);
    pollInterval.value = null;
  }
};

// Handle day card click
const handleDayClick = (day: number) => {
  const status = getDayStatus(day);

  // Only allow upload if empty or failed
  if (status === 'empty' || status === 'failed') {
    selectedDay.value = day;
    selectedFile.value = null;
    selectedDuration.value = 0;
    isUploadModalOpen.value = true;
  } else if (status === 'completed') {
    // TODO: Show video preview/playback
    console.log('Show video for day', day);
  }
};

// Handle video selection from VideoUpload component
const handleVideoSelected = (file: File, duration: number) => {
  selectedFile.value = file;
  selectedDuration.value = duration;
};

// Handle upload confirmation
const handleUploadConfirm = async () => {
  if (!selectedFile.value || !selectedDay.value) return;

  try {
    isUploading.value = true;
    uploadProgress.value = 0;

    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    // Create FormData
    const formData = new FormData();
    formData.append('video', selectedFile.value);
    formData.append('day', selectedDay.value.toString());

    // Upload with progress tracking
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        uploadProgress.value = Math.round((e.loaded / e.total) * 100);
      }
    });

    xhr.addEventListener('load', async () => {
      if (xhr.status === 201) {
        const response = JSON.parse(xhr.responseText);

        // Update day status to processing
        if (selectedDay.value) {
          const updatedStatus: DayStatus = {
            day: selectedDay.value,
            status: 'processing',
            progress: 0
          };
          dayStatuses.value.set(selectedDay.value, updatedStatus);

          // Add to polling list
          activePollDays.value.add(selectedDay.value);
          startPolling();
        }

        // Show success toast
        const toast = await toastController.create({
          message: 'Video uploaded successfully! Processing...',
          duration: 3000,
          color: 'success',
          position: 'top'
        });
        await toast.present();

        // Close modal
        closeUploadModal();

      } else {
        const errorData = JSON.parse(xhr.responseText);
        throw new Error(errorData.error || 'Upload failed');
      }
    });

    xhr.addEventListener('error', () => {
      throw new Error('Network error during upload');
    });

    xhr.open('POST', `${API_BASE_URL}/calendars/${props.calendarId}/videos`);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);

  } catch (error) {
    console.error('Upload error:', error);

    const toast = await toastController.create({
      message: error instanceof Error ? error.message : 'Upload failed',
      duration: 4000,
      color: 'danger',
      position: 'top'
    });
    await toast.present();

  } finally {
    isUploading.value = false;
    uploadProgress.value = 0;
  }
};

// Close upload modal
const closeUploadModal = () => {
  isUploadModalOpen.value = false;
  selectedDay.value = null;
  selectedFile.value = null;
  selectedDuration.value = 0;
  isUploading.value = false;
  uploadProgress.value = 0;
};

// Lifecycle
onMounted(async () => {
  await loadVideoStatuses();
});

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
/* Calendar Day Grid Container */
.calendar-day-grid-container {
  width: 100%;
  container-type: inline-size;
}

/* Loading State */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(0.75rem, 2vh, 1rem);
  min-height: clamp(12rem, 30vh, 16rem);
  padding: clamp(1.5rem, 4vw, 2rem);
}

.loading-section ion-spinner {
  --color: var(--ion-color-primary);
  width: clamp(2.5rem, 6vw, 3rem);
  height: clamp(2.5rem, 6vw, 3rem);
}

.loading-text {
  font-size: clamp(0.9rem, 2vw, 1rem);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  margin: 0;
}

/* Error State */
.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(0.75rem, 2vh, 1rem);
  min-height: clamp(12rem, 30vh, 16rem);
  padding: clamp(1.5rem, 4vw, 2rem);
  background-color: rgba(var(--ion-color-danger-rgb), 0.05);
  border: 1px solid rgba(var(--ion-color-danger-rgb), 0.2);
  border-radius: var(--radius-lg);
}

.error-icon {
  font-size: clamp(2rem, 5vw, 3rem);
  color: var(--ion-color-danger);
}

.error-message {
  font-size: clamp(0.9rem, 2vw, 1rem);
  color: var(--ion-color-danger);
  font-weight: var(--font-weight-medium);
  text-align: center;
  margin: 0;
}

/* Day Grid - Intrinsic Responsive Design */
.day-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(clamp(4rem, 15vw, 8rem), 1fr));
  gap: clamp(0.5rem, 2vw, 1rem);
  padding: clamp(0.5rem, 2vw, 1rem);
}

/* Container query for very small containers */
@container (max-width: 20rem) {
  .day-grid {
    grid-template-columns: repeat(auto-fill, minmax(4rem, 1fr));
    gap: 0.5rem;
  }
}

/* Container query for medium containers */
@container (min-width: 40rem) {
  .day-grid {
    grid-template-columns: repeat(auto-fill, minmax(6rem, 1fr));
    gap: 0.75rem;
  }
}

/* Container query for large containers */
@container (min-width: 60rem) {
  .day-grid {
    grid-template-columns: repeat(7, 1fr); /* Week-style layout */
    gap: 1rem;
  }
}

/* Modal Content */
.modal-content {
  --padding-top: clamp(1rem, 3vw, 1.5rem);
  --padding-bottom: clamp(1rem, 3vw, 1.5rem);
  --padding-start: clamp(1rem, 3vw, 1.5rem);
  --padding-end: clamp(1rem, 3vw, 1.5rem);
}

.upload-modal-body {
  display: flex;
  flex-direction: column;
  gap: clamp(1rem, 3vw, 1.5rem);
}

/* Upload Progress Section */
.upload-progress-section {
  padding: clamp(1rem, 3vw, 1.5rem);
  background: rgba(var(--ion-color-primary-rgb), 0.05);
  border: 1px solid rgba(var(--ion-color-primary-rgb), 0.2);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: clamp(0.5rem, 1.5vw, 0.75rem);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 1.5vw, 0.75rem);
}

.progress-icon {
  font-size: clamp(1.5rem, 4vw, 2rem);
  color: var(--ion-color-primary);
}

.progress-title {
  font-size: clamp(0.9rem, 2vw, 1rem);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.progress-text {
  font-size: clamp(0.85rem, 2vw, 0.9rem);
  color: var(--color-text-secondary);
  text-align: center;
  margin: 0;
}

/* Upload Actions */
.upload-actions {
  padding-top: clamp(0.5rem, 1.5vw, 1rem);
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .loading-section ion-spinner {
    animation: none;
  }
}

@media (prefers-contrast: high) {
  .error-section {
    border-width: 2px;
  }

  .upload-progress-section {
    border-width: 2px;
  }
}
</style>
