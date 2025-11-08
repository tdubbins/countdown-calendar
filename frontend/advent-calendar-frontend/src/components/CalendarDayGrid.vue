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
        @click="handleLoadRetry"
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

    <!-- ARIA Live Region for Status Announcements (Issue #58) -->
    <div
      aria-live="polite"
      aria-atomic="true"
      class="sr-only"
      role="status"
    >
      {{ statusAnnouncement }}
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

    <!-- Video Playback Modal (Issue #59) -->
    <ion-modal
      :is-open="isPlaybackModalOpen"
      @didDismiss="closePlaybackModal"
    >
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>Day {{ playbackDay }} Video</ion-title>
          <ion-buttons slot="end">
            <ion-button
              @click="showDeleteConfirmation"
              color="danger"
              :aria-label="`Delete day ${playbackDay} video`"
            >
              <ion-icon slot="icon-only" :icon="trashOutline"></ion-icon>
            </ion-button>
            <ion-button @click="closePlaybackModal" color="light">
              <strong>Close</strong>
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="playback-modal-content">
        <div v-if="videoMetadata" class="playback-container">
          <!-- Video Player -->
          <video
            ref="videoPlayerRef"
            controls
            preload="metadata"
            :src="playbackVideoUrl || undefined"
            :poster="playbackThumbnailUrl || undefined"
            class="video-player"
            :aria-label="`Day ${playbackDay} video player`"
          ></video>

          <!-- Video Metadata Bar (Option B) -->
          <div class="video-metadata">
            <div class="metadata-item">
              <ion-icon :icon="timeOutline" aria-hidden="true"></ion-icon>
              <span>{{ formatDuration(videoMetadata.duration) }}</span>
              <span class="sr-only">Duration:</span>
            </div>
            <div class="metadata-item">
              <ion-icon :icon="documentOutline" aria-hidden="true"></ion-icon>
              <span>{{ formatFileSize(videoMetadata.size) }}</span>
              <span class="sr-only">File size:</span>
            </div>
            <div class="metadata-item">
              <ion-icon :icon="calendarOutline" aria-hidden="true"></ion-icon>
              <span>{{ formatDate(videoMetadata.uploaded_at) }}</span>
              <span class="sr-only">Uploaded on:</span>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-else class="playback-loading">
          <ion-spinner name="crescent" color="primary"></ion-spinner>
          <p>Loading video...</p>
        </div>
      </ion-content>
    </ion-modal>

    <!-- Delete Confirmation Alert -->
    <ion-alert
      :is-open="isDeleteAlertOpen"
      :header="'⚠️ Delete Video'"
      :sub-header="`Day ${playbackDay}`"
      :message="`This will permanently delete this video. This cannot be undone.`"
      :buttons="[
        {
          text: 'Cancel',
          role: 'cancel',
          handler: () => {
            isDeleteAlertOpen = false;
          }
        },
        {
          text: 'Delete',
          role: 'destructive',
          cssClass: 'alert-button-danger',
          handler: () => {
            handleDeleteVideo();
          }
        }
      ]"
      @didDismiss="isDeleteAlertOpen = false"
    ></ion-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import {
  IonAlert,
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
  calendarOutline,
  cloudUploadOutline,
  documentOutline,
  timeOutline,
  trashOutline
} from 'ionicons/icons';
import CalendarDayCard from '@/components/CalendarDayCard.vue';
import VideoUpload from '@/components/VideoUpload.vue';
import { useVideoManagement, type VideoMetadata } from '@/composables/useVideoManagement';
import API_CONFIG from '@/config/api';

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
  'videoDeleted': [day: number];
}>();

// Composable
const {
  dayStatuses,
  isLoading,
  uploadProgress,
  isUploading,
  initializeDayStatuses,
  loadVideoStatuses,
  stopPolling,
  uploadVideo,
  getVideoMetadata,
  deleteVideo,
  getDayStatus,
  getDayThumbnail,
  getDayProgress,
  getDayError
} = useVideoManagement(props.calendarId);

// Local state
const loadError = ref<string>('');
const statusAnnouncement = ref<string>(''); // ARIA live region (Issue #58)

// Upload modal state
const isUploadModalOpen = ref(false);
const selectedDay = ref<number | null>(null);
const selectedFile = ref<File | null>(null);
const selectedDuration = ref<number>(0);

// Playback modal state (Issue #59)
const isPlaybackModalOpen = ref(false);
const playbackDay = ref<number | null>(null);
const videoMetadata = ref<VideoMetadata | null>(null);
const videoPlayerRef = ref<HTMLVideoElement | null>(null);
const playbackThumbnailUrl = ref<string | null>(null);
const playbackVideoUrl = ref<string | null>(null);

// Delete alert state
const isDeleteAlertOpen = ref(false);

/**
 * Helper: Format duration (seconds to MM:SS)
 * Reused from VideoUpload.vue pattern
 */
const formatDuration = (seconds: number): string => {
  if (seconds === 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Helper: Format file size (bytes to MB)
 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 MB';
  const mb = bytes / (1024 * 1024);
  return `${Math.round(mb)} MB`;
};

/**
 * Helper: Format date (ISO to readable)
 */
const formatDate = (isoString: string): string => {
  return new Date(isoString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

/**
 * Load videos and initialize day statuses
 */
const handleLoadRetry = async () => {
  loadError.value = '';
  await loadVideos();
};

const loadVideos = async () => {
  // Initialize all days as empty first
  initializeDayStatuses(props.duration);

  const result = await loadVideoStatuses();

  if (!result.success) {
    loadError.value = result.error || 'Failed to load calendar days';
  }
};

/**
 * Handle day card click
 * - Empty/Failed: Open upload modal
 * - Completed: Open playback modal
 * - Processing/Uploading: No action (visual feedback only)
 */
const handleDayClick = async (day: number) => {
  const status = getDayStatus(day);

  if (status === 'empty' || status === 'failed') {
    // Open upload modal
    selectedDay.value = day;
    selectedFile.value = null;
    selectedDuration.value = 0;
    isUploadModalOpen.value = true;
  } else if (status === 'completed') {
    // Open playback modal
    await openPlaybackModal(day);
  }
  // Processing/uploading: no action
};

/**
 * Handle video selection from VideoUpload component
 */
const handleVideoSelected = (file: File, duration: number) => {
  selectedFile.value = file;
  selectedDuration.value = duration;
};

/**
 * Handle upload confirmation
 */
const handleUploadConfirm = async () => {
  if (!selectedFile.value || !selectedDay.value) return;

  const day = selectedDay.value;

  // Announce upload start (ARIA - Issue #58, Option B: Major transitions)
  statusAnnouncement.value = `Day ${day} upload started`;

  const result = await uploadVideo(day, selectedFile.value);

  if (result.success) {
    // Announce processing (ARIA - Issue #58)
    statusAnnouncement.value = `Day ${day} processing`;

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

    // Wait for processing to complete, then announce
    watchForCompletion(day);

  } else {
    // Announce failure (ARIA - Issue #58)
    statusAnnouncement.value = `Day ${day} upload failed: ${result.error}`;

    const toast = await toastController.create({
      message: result.error || 'Upload failed',
      duration: 4000,
      color: 'danger',
      position: 'top'
    });
    await toast.present();

    emit('uploadError', day, result.error || 'Upload failed');
  }
};

/**
 * Watch for completion to announce (ARIA - Issue #58)
 * FIX BUG #4: Store interval IDs to prevent memory leaks
 */
const activeWatchers = ref<Map<number, number>>(new Map());

const watchForCompletion = (day: number) => {
  // Clear any existing watcher for this day
  const existingInterval = activeWatchers.value.get(day);
  if (existingInterval) {
    clearInterval(existingInterval);
  }

  const checkInterval = window.setInterval(() => {
    const status = getDayStatus(day);

    if (status === 'completed') {
      statusAnnouncement.value = `Day ${day} video uploaded successfully`;
      emit('uploadComplete', day);

      // Clean up
      clearInterval(checkInterval);
      activeWatchers.value.delete(day);
    } else if (status === 'failed') {
      const error = getDayError(day);
      statusAnnouncement.value = `Day ${day} upload failed: ${error}`;
      emit('uploadError', day, error || 'Processing failed');

      // Clean up
      clearInterval(checkInterval);
      activeWatchers.value.delete(day);
    }
  }, 1000);

  // Store interval ID
  activeWatchers.value.set(day, checkInterval);

  // Safety timeout: Clear interval after 5 minutes max
  setTimeout(() => {
    if (activeWatchers.value.has(day)) {
      clearInterval(checkInterval);
      activeWatchers.value.delete(day);
    }
  }, 300000);
};

/**
 * Close upload modal
 */
const closeUploadModal = () => {
  isUploadModalOpen.value = false;
  selectedDay.value = null;
  selectedFile.value = null;
  selectedDuration.value = 0;
};

/**
 * Open playback modal (Issue #59)
 */
const openPlaybackModal = async (day: number) => {
  playbackDay.value = day;
  videoMetadata.value = null;
  playbackThumbnailUrl.value = null;
  playbackVideoUrl.value = null;
  isPlaybackModalOpen.value = true;

  // Use thumbnail from grid if available (already loaded as data URL)
  const dayThumbnail = getDayThumbnail(day);
  if (dayThumbnail) {
    playbackThumbnailUrl.value = dayThumbnail;
  }

  // Fetch video metadata
  const result = await getVideoMetadata(day);

  if (result.success && result.data) {
    videoMetadata.value = result.data;

    // Fetch video blob and create object URL for playback
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${result.data.stream_url}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        playbackVideoUrl.value = URL.createObjectURL(blob);
      } else {
        throw new Error('Failed to fetch video');
      }
    } catch (error) {
      console.error('Failed to load video for playback:', error);
      const toast = await toastController.create({
        message: 'Failed to load video for playback',
        duration: 3000,
        color: 'danger',
        position: 'top'
      });
      await toast.present();
    }
  } else {
    const toast = await toastController.create({
      message: 'Failed to load video',
      duration: 3000,
      color: 'danger',
      position: 'top'
    });
    await toast.present();
    closePlaybackModal();
  }
};

/**
 * Close playback modal
 */
const closePlaybackModal = () => {
  // Pause video if playing
  if (videoPlayerRef.value) {
    videoPlayerRef.value.pause();
  }

  // Revoke object URL to free memory
  if (playbackVideoUrl.value) {
    URL.revokeObjectURL(playbackVideoUrl.value);
    playbackVideoUrl.value = null;
  }

  isPlaybackModalOpen.value = false;
  playbackDay.value = null;
  videoMetadata.value = null;
  playbackThumbnailUrl.value = null;
};

/**
 * Show delete confirmation (Issue #59)
 */
const showDeleteConfirmation = () => {
  isDeleteAlertOpen.value = true;
};

/**
 * Handle video deletion (Issue #59)
 */
const handleDeleteVideo = async () => {
  if (!playbackDay.value) return;

  const day = playbackDay.value;

  const result = await deleteVideo(day);

  if (result.success) {
    // Announce deletion (ARIA - Issue #58)
    statusAnnouncement.value = `Day ${day} video deleted`;

    const toast = await toastController.create({
      message: 'Video deleted successfully',
      duration: 3000,
      color: 'success',
      position: 'top'
    });
    await toast.present();

    // Close modal
    closePlaybackModal();

    // Emit event
    emit('videoDeleted', day);

  } else {
    const toast = await toastController.create({
      message: result.error || 'Failed to delete video',
      duration: 3000,
      color: 'danger',
      position: 'top'
    });
    await toast.present();
  }
};

// Lifecycle
onMounted(async () => {
  await loadVideos();
});

onUnmounted(() => {
  // Clean up polling
  stopPolling();

  // FIX BUG #4: Clean up all active watchers on unmount
  activeWatchers.value.forEach((intervalId) => {
    clearInterval(intervalId);
  });
  activeWatchers.value.clear();
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

/* Screen Reader Only - ARIA Live Region */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Upload Modal Content */
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

/* Playback Modal Content (Issue #59) */
.playback-modal-content {
  --padding-top: 0;
  --padding-bottom: 0;
  --padding-start: 0;
  --padding-end: 0;
}

.playback-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Video Player */
.video-player {
  width: 100%;
  max-height: 70vh;
  background: #000;
  object-fit: contain;
}

/* Video Metadata Bar (Option B) */
.video-metadata {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: clamp(1rem, 3vw, 1.5rem);
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  gap: clamp(0.75rem, 2vw, 1rem);
  flex-wrap: wrap;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: clamp(0.25rem, 1vw, 0.5rem);
  font-size: clamp(0.85rem, 2vw, 0.95rem);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.metadata-item ion-icon {
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  color: var(--ion-color-primary);
}

/* Playback Loading State */
.playback-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(0.75rem, 2vh, 1rem);
  min-height: 50vh;
  padding: clamp(1.5rem, 4vw, 2rem);
}

.playback-loading ion-spinner {
  --color: var(--ion-color-primary);
  width: clamp(2.5rem, 6vw, 3rem);
  height: clamp(2.5rem, 6vw, 3rem);
}

.playback-loading p {
  font-size: clamp(0.9rem, 2vw, 1rem);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  margin: 0;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .loading-section ion-spinner,
  .playback-loading ion-spinner {
    animation: none;
  }
}

@media (prefers-contrast: high) {
  .error-section,
  .upload-progress-section {
    border-width: 2px;
  }

  .video-metadata {
    border-top-width: 2px;
  }
}
</style>
