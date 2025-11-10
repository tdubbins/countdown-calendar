<template>
  <div
    class="video-upload-container"
    :aria-label="`Upload video for day ${day}`"
  >
    <!-- Drag and Drop Zone -->
    <div
      ref="dropZoneRef"
      class="drop-zone"
      :class="{
        'drop-zone--dragging': isDragging,
        'drop-zone--has-file': selectedFile,
        'drop-zone--error': errorMessage
      }"
      @dragenter.prevent="handleDragEnter"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      role="region"
      :aria-describedby="errorMessage ? 'upload-error' : 'upload-instructions'"
    >
      <!-- File Selected State -->
      <div v-if="selectedFile" class="file-preview">
        <!-- Video Thumbnail -->
        <div class="video-thumbnail">
          <video
            ref="videoPreviewRef"
            :src="videoPreviewUrl"
            class="preview-video"
            controls
            preload="metadata"
            :muted="false"
            @loadedmetadata="handleVideoMetadata"
            aria-label="Video preview with playback controls"
          ></video>
        </div>

        <!-- File Information -->
        <div class="file-info">
          <p class="file-name">{{ selectedFile.name }}</p>
          <p class="file-details">
            {{ formatFileSize(selectedFile.size) }} • {{ formatDuration(videoDuration) }}
          </p>
        </div>

        <!-- Remove Button -->
        <ion-button
          fill="clear"
          color="danger"
          size="small"
          @click="handleRemoveFile"
          aria-label="Remove selected video"
          class="remove-button"
        >
          <ion-icon slot="icon-only" :icon="closeCircleOutline"></ion-icon>
        </ion-button>
      </div>

      <!-- Empty State -->
      <div v-else class="drop-zone-content">
        <ion-icon
          :icon="cloudUploadOutline"
          class="upload-icon"
          aria-hidden="true"
        ></ion-icon>

        <h3 class="upload-title">
          {{ isDragging ? 'Drop video here' : 'Upload Video' }}
        </h3>

        <p id="upload-instructions" class="upload-description">
          Drag and drop or click to browse
        </p>

        <p class="upload-requirements">
          Max 1GB • 3 minutes • MP4, MOV, AVI, WEBM
        </p>

        <!-- Hidden File Input -->
        <input
          ref="fileInputRef"
          type="file"
          accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
          @change="handleFileSelect"
          class="file-input"
          aria-label="Choose video file"
        />

        <!-- Browse Button -->
        <ion-button
          expand="block"
          color="primary"
          size="default"
          @click="triggerFileInput"
          class="browse-button"
          aria-label="Browse for video file"
        >
          <ion-icon slot="start" :icon="folderOpenOutline"></ion-icon>
          Browse Files
        </ion-button>
      </div>
    </div>

    <!-- Error Message -->
    <div
      v-if="errorMessage"
      id="upload-error"
      class="error-message"
      role="alert"
    >
      <ion-icon :icon="alertCircleOutline" class="error-icon"></ion-icon>
      {{ errorMessage }}
    </div>

    <!-- Upload Progress (if needed by parent) -->
    <slot name="progress"></slot>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  IonButton,
  IonIcon
} from '@ionic/vue';
import {
  cloudUploadOutline,
  folderOpenOutline,
  closeCircleOutline,
  alertCircleOutline
} from 'ionicons/icons';
import { formatFileSize, formatDuration } from '@/utils/mediaUtils';

// Constants for validation
const MAX_FILE_SIZE = 1024 * 1024 * 1024; // 1GB in bytes (1024MB) - allows 1080p 60fps videos
const MAX_DURATION = 180; // 3 minutes in seconds
const ALLOWED_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'];
const ALLOWED_EXTENSIONS = ['.mp4', '.mov', '.avi', '.webm'];

// Props
interface Props {
  day: number; // Calendar day number for accessibility
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
});

// Emits
const emit = defineEmits<{
  'videoSelected': [file: File, duration: number];
  'uploadComplete': [response: any];
  'uploadError': [error: string];
  'remove': [];
}>();

// Reactive state
const dropZoneRef = ref<HTMLElement | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const videoPreviewRef = ref<HTMLVideoElement | null>(null);

const isDragging = ref(false);
const selectedFile = ref<File | null>(null);
const videoPreviewUrl = ref<string>('');
const videoDuration = ref<number>(0);
const errorMessage = ref<string>('');

// Computed
const isValidFile = computed(() => {
  return selectedFile.value !== null && !errorMessage.value;
});

// Validation functions
const validateFileType = (file: File): boolean => {
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();

  if (!ALLOWED_TYPES.includes(file.type) && !ALLOWED_EXTENSIONS.includes(fileExtension)) {
    errorMessage.value = 'Invalid file type. Please upload MP4, MOV, AVI, or WEBM files.';
    return false;
  }

  return true;
};

const validateFileSize = (file: File): boolean => {
  if (file.size > MAX_FILE_SIZE) {
    errorMessage.value = `File size exceeds 1GB limit. Selected file is ${formatFileSize(file.size)}.`;
    return false;
  }

  return true;
};

const validateVideoDuration = async (file: File): Promise<boolean> => {
  return new Promise((resolve) => {
    const video = document.createElement('video');
    video.preload = 'metadata';

    // Set a timeout in case metadata never loads
    let timeout: NodeJS.Timeout | null = null;
    let resolved = false;

    const cleanup = () => {
      if (timeout) clearTimeout(timeout);
      if (video.src) {
        window.URL.revokeObjectURL(video.src);
      }
    };

    const resolveOnce = (result: boolean) => {
      if (!resolved) {
        resolved = true;
        cleanup();
        resolve(result);
      }
    };

    video.onloadedmetadata = () => {
      const duration = video.duration;
      videoDuration.value = duration;

      if (isNaN(duration) || duration === 0) {
        errorMessage.value = 'Unable to read video duration. Please try a different file.';
        resolveOnce(false);
      } else if (duration > MAX_DURATION) {
        errorMessage.value = `Video duration exceeds 3 minutes. Selected video is ${formatDuration(duration)}.`;
        resolveOnce(false);
      } else {
        resolveOnce(true);
      }
    };

    video.onerror = () => {
      errorMessage.value = 'Unable to read video file. Please try a different file.';
      resolveOnce(false);
    };

    timeout = setTimeout(() => {
      errorMessage.value = 'Video validation timed out. Please try a different file.';
      resolveOnce(false);
    }, 10000);

    try {
      video.src = URL.createObjectURL(file);
    } catch (e) {
      errorMessage.value = 'Failed to process video file.';
      resolveOnce(false);
    }
  });
};

// File handling
const processFile = async (file: File) => {
  errorMessage.value = '';

  // Validate file type, size, and duration
  if (!validateFileType(file)) return;
  if (!validateFileSize(file)) return;
  if (!await validateVideoDuration(file)) return;

  // All validations passed - set file and preview
  selectedFile.value = file;
  videoPreviewUrl.value = URL.createObjectURL(file);
  emit('videoSelected', file, videoDuration.value);
};

// Event handlers
const handleDragEnter = () => {
  if (props.disabled) return;
  isDragging.value = true;
};

const handleDragOver = () => {
  if (props.disabled) return;
  isDragging.value = true;
};

const handleDragLeave = (e: DragEvent) => {
  if (props.disabled) return;
  // Only set to false if leaving the drop zone entirely
  if (e.target === dropZoneRef.value) {
    isDragging.value = false;
  }
};

const handleDrop = async (e: DragEvent) => {
  if (props.disabled) return;
  isDragging.value = false;

  // Get file from drop event (try DataTransferItem API first for better compatibility)
  let file: File | null = null;

  if (e.dataTransfer?.items?.[0]?.kind === 'file') {
    file = e.dataTransfer.items[0].getAsFile();
  } else if (e.dataTransfer?.files?.[0]) {
    file = e.dataTransfer.files[0];
  }

  if (!file) {
    errorMessage.value = 'No file detected. Please try again or use the "Browse Files" button.';
    return;
  }

  // Check for 0-byte files (macOS drag-and-drop issue)
  if (file.size === 0) {
    errorMessage.value = 'Unable to read file via drag-and-drop. Please use the "Browse Files" button instead.';
    return;
  }

  await processFile(file);
};

const triggerFileInput = () => {
  if (props.disabled) return;
  fileInputRef.value?.click();
};

const handleFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const files = target.files;

  if (files && files.length > 0) {
    await processFile(files[0]);
  }
};

const handleRemoveFile = () => {
  // Revoke object URL to free memory
  if (videoPreviewUrl.value) {
    URL.revokeObjectURL(videoPreviewUrl.value);
  }

  // Reset state
  selectedFile.value = null;
  videoPreviewUrl.value = '';
  videoDuration.value = 0;
  errorMessage.value = '';

  // Reset file input
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }

  // Emit remove event
  emit('remove');
};

const handleVideoMetadata = (e: Event) => {
  const video = e.target as HTMLVideoElement;
  videoDuration.value = video.duration;
  video.muted = false;
  video.volume = 1.0;
};

// Expose methods for parent component
defineExpose({
  clearFile: handleRemoveFile,
  getSelectedFile: () => selectedFile.value,
  isValid: () => isValidFile.value
});
</script>

<style scoped>
/* Video Upload Container */
.video-upload-container {
  width: 100%;
  max-width: 100%;
}

/* Drop Zone - Intrinsically responsive */
.drop-zone {
  position: relative;
  width: 100%;
  min-height: clamp(16rem, 40vh, 24rem);
  padding: clamp(1.5rem, 4vw, 2.5rem);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-background);
  transition: all var(--transition-base);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover {
  border-color: var(--ion-color-primary);
  background: rgba(var(--ion-color-primary-rgb), 0.05);
}

.drop-zone:focus-within {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

.drop-zone--dragging {
  border-color: var(--ion-color-primary);
  background: rgba(var(--ion-color-primary-rgb), 0.1);
  transform: scale(1.02);
}

.drop-zone--has-file {
  border-color: var(--ion-color-success);
  background: rgba(var(--ion-color-success-rgb), 0.05);
  cursor: default;
}

.drop-zone--has-file:hover {
  border-color: var(--ion-color-success);
  background: rgba(var(--ion-color-success-rgb), 0.05);
  transform: none;
}

.drop-zone--error {
  border-color: var(--ion-color-danger);
  background: rgba(var(--ion-color-danger-rgb), 0.05);
}

/* Drop Zone Content - Empty State */
.drop-zone-content {
  text-align: center;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(0.75rem, 2vh, 1.25rem);
}

.upload-icon {
  font-size: clamp(3rem, 10vw, 5rem);
  color: var(--ion-color-primary);
  opacity: 0.7;
  transition: transform var(--transition-base);
}

.drop-zone--dragging .upload-icon {
  transform: scale(1.1);
  opacity: 1;
}

.upload-title {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.upload-description {
  font-size: clamp(0.9rem, 2vw, 1rem);
  color: var(--color-text-secondary);
  margin: 0;
}

.upload-requirements {
  font-size: clamp(0.75rem, 1.8vw, 0.85rem);
  color: var(--color-text-tertiary);
  margin: 0;
  font-weight: var(--font-weight-medium);
}

/* File Input - Hidden */
.file-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 1px;
  height: 1px;
}

/* Browse Button */
.browse-button {
  margin-top: clamp(0.5rem, 1.5vh, 1rem);
  min-width: clamp(10rem, 40vw, 14rem);
  height: clamp(2.75rem, 7vh, 3rem);
  --border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
}

/* File Preview State */
.file-preview {
  display: flex;
  align-items: center;
  gap: clamp(1rem, 3vw, 1.5rem);
  width: 100%;
  padding: clamp(0.75rem, 2vw, 1rem);
}

/* Video Thumbnail */
.video-thumbnail {
  position: relative;
  flex-shrink: 0;
  width: clamp(8rem, 25vw, 12rem);
  height: clamp(8rem, 25vw, 12rem);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-background-secondary);
}

.preview-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-md);
}

/* File Information */
.file-info {
  flex: 1;
  min-width: 0; /* Enable text truncation */
}

.file-name {
  font-size: clamp(0.9rem, 2vw, 1rem);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 clamp(0.25rem, 0.5vh, 0.5rem) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-details {
  font-size: clamp(0.75rem, 1.8vw, 0.85rem);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Remove Button */
.remove-button {
  flex-shrink: 0;
  --padding-start: 0.5rem;
  --padding-end: 0.5rem;
  min-height: 44px; /* Touch-friendly */
  min-width: 44px;
}

.remove-button ion-icon {
  font-size: clamp(1.5rem, 4vw, 2rem);
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 1.5vw, 0.75rem);
  margin-top: clamp(0.75rem, 2vh, 1rem);
  padding: clamp(0.75rem, 2vw, 1rem);
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  color: var(--ion-color-danger);
  border: 1px solid rgba(var(--ion-color-danger-rgb), 0.3);
  border-radius: var(--radius-md);
  font-size: clamp(0.85rem, 2vw, 0.9rem);
  font-weight: var(--font-weight-medium);
  animation: fadeIn var(--transition-base);
}

.error-icon {
  flex-shrink: 0;
  font-size: clamp(1.25rem, 3vw, 1.5rem);
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .drop-zone,
  .upload-icon,
  .error-message {
    animation: none;
    transition: none;
  }

  .drop-zone--dragging {
    transform: none;
  }
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .file-preview {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .video-thumbnail {
    width: clamp(6rem, 30vw, 10rem);
    height: clamp(6rem, 30vw, 10rem);
  }

  .file-info {
    flex: 1;
    min-width: 8rem;
  }

  .remove-button {
    width: 100%;
    margin-top: 0.5rem;
  }
}
</style>
