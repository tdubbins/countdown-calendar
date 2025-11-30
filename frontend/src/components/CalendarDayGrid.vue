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
        :is-dragging="draggedDay === day"
        :is-drag-over="dragOverDay === day"
        @click="handleDayClick(day)"
        @dragstart="handleDragStart"
        @dragend="handleDragEnd"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      />
    </div>

    <!-- ARIA Live Region for Status Announcements -->
    <div
      aria-live="polite"
      aria-atomic="true"
      class="sr-only"
      role="status"
    >
      {{ statusAnnouncement }}
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInputRef"
      type="file"
      accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
      @change="handleFileSelect"
      class="hidden-file-input"
      aria-label="Choose video file"
    />

    <!-- Video Playback Modal -->
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
        <!-- Processing State - video still compressing -->
        <div v-if="isPlaybackProcessing" class="playback-processing">
          <img
            v-if="playbackThumbnailUrl"
            :src="playbackThumbnailUrl"
            :alt="`Day ${playbackDay} thumbnail`"
            class="processing-thumbnail"
          />
          <div class="processing-overlay">
            <ion-spinner name="crescent" color="light"></ion-spinner>
            <p>Video is being compressed...</p>
          </div>
        </div>

        <!-- Completed State - video ready for playback -->
        <div v-else-if="videoMetadata" class="playback-container">
          <!-- Video Player -->
          <video
            ref="videoPlayerRef"
            controls
            preload="metadata"
            :src="playbackVideoUrl || undefined"
            :poster="playbackThumbnailUrl || undefined"
            class="video-player"
            :aria-label="`Day ${playbackDay} video player`"
            @loadedmetadata="handlePlaybackVideoMetadata"
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
              <span>{{ formatFileSizeMB(videoMetadata.size) }}</span>
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
import API_CONFIG from '@/config/api';
import {
  IonAlert,
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonIcon,
  IonModal,
  IonSpinner,
  IonTitle,
  IonToolbar
} from '@ionic/vue';
import {
  alertCircleOutline,
  calendarOutline,
  documentOutline,
  timeOutline,
  trashOutline
} from 'ionicons/icons';
import CalendarDayCard from '@/components/CalendarDayCard.vue';
import { useVideoManagement, type VideoMetadata } from '@/composables/useVideoManagement';
import { useToast } from '@/composables/useToast';
import { formatDuration, formatFileSizeMB } from '@/utils/mediaUtils';

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
  'videoReassigned': [sourceDay: number, targetDay: number, swapped: boolean];
}>();

// Composable
const {
  isLoading,
  activePollDays,
  // uploadProgress, // Reserved for future use
  // isUploading, // Reserved for future use
  initializeDayStatuses,
  loadVideoStatuses,
  pollAllStatuses,
  stopPolling,
  uploadVideo,
  getVideoMetadata,
  deleteVideo,
  reassignVideo,
  getDayStatus,
  getDayThumbnail,
  getDayProgress,
  getDayError
} = useVideoManagement(props.calendarId);

// Composables
const { showSuccess, showError } = useToast();

// Local state
const loadError = ref<string>('');
const statusAnnouncement = ref<string>(''); // ARIA live region
const fileInputRef = ref<HTMLInputElement | null>(null);
const selectedDay = ref<number | null>(null);

// Playback modal state
const isPlaybackModalOpen = ref(false);
const playbackDay = ref<number | null>(null);
const videoMetadata = ref<VideoMetadata | null>(null);
const videoPlayerRef = ref<HTMLVideoElement | null>(null);
const playbackThumbnailUrl = ref<string | null>(null);
const playbackVideoUrl = ref<string | null>(null);
const isPlaybackProcessing = ref(false);

// Delete alert state
const isDeleteAlertOpen = ref(false);

// Drag and drop state
const draggedDay = ref<number | null>(null);
const dragOverDay = ref<number | null>(null);
const isReassigning = ref(false);

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
 * - Empty/Failed: Open file picker
 * - Completed: Open playback modal
 * - Processing: Open modal with processing state (allows deletion)
 */
const handleDayClick = async (day: number) => {
  const status = getDayStatus(day);

  if (status === 'empty' || status === 'failed') {
    // Open file picker
    selectedDay.value = day;
    fileInputRef.value?.click();
  } else if (status === 'completed') {
    // Open playback modal
    await openPlaybackModal(day);
  } else if (status === 'processing') {
    // Open modal with processing state (allows deletion)
    await openProcessingModal(day);
  }
};

/**
 * Validate video file
 */
const validateVideoFile = (file: File): string | null => {
  const MAX_FILE_SIZE = 1024 * 1024 * 1024; // 1GB
  const ALLOWED_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'];
  const ALLOWED_EXTENSIONS = ['.mp4', '.mov', '.avi', '.webm'];

  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();

  if (!ALLOWED_TYPES.includes(file.type) && !ALLOWED_EXTENSIONS.includes(fileExtension)) {
    return 'Invalid file type. Please upload MP4, MOV, AVI, or WEBM files.';
  }

  if (file.size > MAX_FILE_SIZE) {
    return `File size exceeds 1GB limit. Selected file is ${(file.size / (1024 * 1024)).toFixed(2)}MB.`;
  }

  return null;
};

/**
 * Handle file selection from file input
 */
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (!file || !selectedDay.value) return;

  const day = selectedDay.value;

  // Validate file
  const validationError = validateVideoFile(file);
  if (validationError) {
    await showError(validationError, 4000);
    target.value = ''; // Reset input
    return;
  }

  // Announce upload start
  statusAnnouncement.value = `Day ${day} upload started`;

  // Upload video
  const result = await uploadVideo(day, file);

  if (result.success) {
    statusAnnouncement.value = `Day ${day} processing`;
    await showSuccess('Video uploaded successfully! Processing...', 3000);
    watchForCompletion(day);
  } else {
    statusAnnouncement.value = `Day ${day} upload failed: ${result.error}`;
    await showError(result.error || 'Upload failed', 4000);
    emit('uploadError', day, result.error || 'Upload failed');
  }

  // Reset input
  target.value = '';
};

/**
 * Watch for compression completion.
 * Polls every 15 seconds using lightweight status endpoint (no thumbnail reload).
 * Stores interval IDs to prevent memory leaks.
 */
const activeWatchers = ref<Map<number, number>>(new Map());

const watchForCompletion = (day: number) => {
  // Clear any existing watcher for this day
  const existingInterval = activeWatchers.value.get(day);
  if (existingInterval) {
    clearInterval(existingInterval);
  }

  // Add to active poll days so pollAllStatuses includes this day
  activePollDays.value.add(day);

  // Poll every 15 seconds using lightweight status endpoint (no thumbnail reload)
  const checkInterval = window.setInterval(async () => {
    // Use status endpoint - doesn't reload videos/thumbnails, no flicker
    await pollAllStatuses();

    const status = getDayStatus(day);

    if (status === 'completed') {
      statusAnnouncement.value = `Day ${day} video ready`;
      emit('uploadComplete', day);

      // Clean up
      clearInterval(checkInterval);
      activeWatchers.value.delete(day);
    } else if (status === 'failed') {
      const error = getDayError(day);
      statusAnnouncement.value = `Day ${day} processing failed: ${error}`;
      emit('uploadError', day, error || 'Processing failed');

      // Clean up
      clearInterval(checkInterval);
      activeWatchers.value.delete(day);
    }
  }, 15000); // Check every 15 seconds

  // Store interval ID
  activeWatchers.value.set(day, checkInterval);

  // Safety timeout: Clear interval after 5 minutes max
  setTimeout(() => {
    if (activeWatchers.value.has(day)) {
      clearInterval(checkInterval);
      activeWatchers.value.delete(day);
      activePollDays.value.delete(day);
    }
  }, 300000);
};


/**
 * Handle playback video metadata loaded - ensures audio is enabled and auto-plays
 */
const handlePlaybackVideoMetadata = (e: Event) => {
  const video = e.target as HTMLVideoElement;
  video.muted = false;
  video.volume = 1.0;
  video.play().catch(() => {
    // Autoplay may be prevented by browser policy
  });
};

/**
 * Open playback modal for a day's video.
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
      const baseWithoutApi = API_CONFIG.BASE_URL.replace(/\/api$/, '');
      const videoUrl = `${baseWithoutApi}${result.data.stream_url}`;

      const response = await fetch(videoUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        playbackVideoUrl.value = URL.createObjectURL(blob);
      } else {
        throw new Error('Failed to fetch video');
      }
    } catch (error) {
      console.error('Failed to load video for playback:', error);
      await showError('Failed to load video for playback');
    }
  } else {
    await showError('Failed to load video');
    closePlaybackModal();
  }
};

/**
 * Open modal for processing video (allows deletion while compressing).
 */
const openProcessingModal = async (day: number) => {
  playbackDay.value = day;
  videoMetadata.value = null;
  playbackThumbnailUrl.value = null;
  playbackVideoUrl.value = null;
  isPlaybackProcessing.value = true;
  isPlaybackModalOpen.value = true;

  // Use thumbnail from grid if available
  const dayThumbnail = getDayThumbnail(day);
  if (dayThumbnail) {
    playbackThumbnailUrl.value = dayThumbnail;
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
  isPlaybackProcessing.value = false;
  playbackDay.value = null;
  videoMetadata.value = null;
  playbackThumbnailUrl.value = null;
};

/**
 * Show delete confirmation dialog.
 */
const showDeleteConfirmation = () => {
  isDeleteAlertOpen.value = true;
};

/**
 * Handle video deletion.
 */
const handleDeleteVideo = async () => {
  if (!playbackDay.value) return;

  const day = playbackDay.value;

  const result = await deleteVideo(day);

  if (result.success) {
    // Announce deletion via ARIA
    statusAnnouncement.value = `Day ${day} video deleted`;

    await showSuccess('Video deleted successfully');

    // Close modal
    closePlaybackModal();

    // Emit event
    emit('videoDeleted', day);

  } else {
    await showError(result.error || 'Failed to delete video');
  }
};

/**
 * Drag and drop handlers for video reassignment
 */

/**
 * Handle drag start - set the dragged day
 */
const handleDragStart = (day: number) => {
  draggedDay.value = day;
  statusAnnouncement.value = `Dragging day ${day} video. Drop on another day to move or swap.`;
};

/**
 * Handle drag end - clear drag state
 */
const handleDragEnd = () => {
  draggedDay.value = null;
  dragOverDay.value = null;
  if (!isReassigning.value) {
    statusAnnouncement.value = 'Drag cancelled';
  }
};

/**
 * Handle drag over - track which day is being hovered
 */
const handleDragOver = (day: number) => {
  if (day !== draggedDay.value) {
    dragOverDay.value = day;
  }
};

/**
 * Handle drag leave - clear hover state
 */
const handleDragLeave = () => {
  dragOverDay.value = null;
};

/**
 * Handle drop - reassign or swap videos
 */
const handleDrop = async (targetDay: number) => {
  const sourceDay = draggedDay.value;

  // Clear drag state
  draggedDay.value = null;
  dragOverDay.value = null;

  // Validate
  if (!sourceDay || sourceDay === targetDay) {
    return;
  }

  // Check target status - prevent drop on processing/uploading
  const targetStatus = getDayStatus(targetDay);
  if (targetStatus === 'processing' || targetStatus === 'uploading') {
    await showError(`Cannot move to day ${targetDay} - video is still processing`);
    return;
  }

  // Perform reassignment
  isReassigning.value = true;
  const willSwap = targetStatus === 'completed';

  // Announce action
  statusAnnouncement.value = willSwap
    ? `Swapping videos between day ${sourceDay} and day ${targetDay}...`
    : `Moving video from day ${sourceDay} to day ${targetDay}...`;

  const result = await reassignVideo(sourceDay, targetDay);

  isReassigning.value = false;

  if (result.success && result.data) {
    statusAnnouncement.value = result.data.swapped
      ? `Videos swapped between day ${sourceDay} and day ${targetDay}`
      : `Video moved from day ${sourceDay} to day ${targetDay}`;

    await showSuccess(
      result.data.swapped
        ? `Videos swapped between day ${sourceDay} and day ${targetDay}`
        : `Video moved to day ${targetDay}`
    );

    emit('videoReassigned', sourceDay, targetDay, result.data.swapped);
  } else {
    statusAnnouncement.value = `Failed to move video: ${result.error}`;
    await showError(result.error || 'Failed to reassign video');
  }
};

// Lifecycle
onMounted(async () => {
  await loadVideos();
});

onUnmounted(() => {
  // Clean up polling
  stopPolling();

  // Clean up all active watchers on unmount
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
/* Use container-relative sizing for true responsive behavior */
.day-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 8rem), 1fr));
  gap: clamp(0.75rem, 2cqi, 1.5rem);
  padding: clamp(0.75rem, 2cqi, 1.5rem);
  width: 100%;
}

/* Container query for very small containers (portrait phones) */
@container (max-width: 30rem) {
  .day-grid {
    grid-template-columns: repeat(auto-fill, minmax(min(100%, 6.5rem), 1fr));
  }
}

/* Container query for large containers (desktop) - Week-style layout */
@container (min-width: 60rem) {
  .day-grid {
    grid-template-columns: repeat(auto-fill, minmax(min(100%, 10rem), 1fr));
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

/* Hidden File Input */
.hidden-file-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 1px;
  height: 1px;
}

/* Playback Modal Content */
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

/* Playback Processing State */
.playback-processing {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  background: #1a1a1a;
}

.processing-thumbnail {
  width: 100%;
  max-height: 60vh;
  object-fit: contain;
  opacity: 0.5;
}

.processing-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
  padding: 2rem;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 12px;
}

.processing-overlay p {
  color: #ffffff;
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
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
