<template>
  <div
    class="day-card"
    :class="dayCardClasses"
    :draggable="isDraggable"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @dragover.prevent="handleDragOver"
    @dragleave="handleDragLeave"
    @drop.prevent="handleDrop"
    tabindex="0"
    role="button"
    :aria-label="ariaLabel"
    :aria-describedby="errorMessage ? `error-${day}` : undefined"
    :aria-grabbed="isDragging ? 'true' : undefined"
  >
    <!-- Day Number -->
    <div class="day-number">{{ day }}</div>

    <!-- Status Content -->
    <div class="status-content">
      <!-- Empty State -->
      <div v-if="status === 'empty'" class="status-empty">
        <ion-icon :icon="addCircleOutline" class="status-icon" aria-hidden="true"></ion-icon>
        <span class="sr-only">Empty - Click to upload</span>
      </div>

      <!-- Uploading State -->
      <div v-else-if="status === 'uploading'" class="status-uploading">
        <ion-icon :icon="cloudUploadOutline" class="status-icon animated-pulse" aria-hidden="true"></ion-icon>
        <ion-progress-bar
          v-if="progress !== undefined"
          :value="progress / 100"
          color="primary"
          class="upload-progress-bar"
        ></ion-progress-bar>
        <span class="status-text">{{ progress }}%</span>
        <span class="sr-only">Uploading - {{ progress }}% complete</span>
      </div>

      <!-- Processing State - Show thumbnail if available, otherwise spinner -->
      <div v-else-if="status === 'processing'" class="status-processing">
        <!-- Thumbnail available - show it with processing indicator -->
        <div v-if="thumbnailUrl" class="status-completed">
          <img
            :src="thumbnailUrl"
            :alt="`Day ${day} video thumbnail`"
            class="thumbnail-image"
            loading="lazy"
          />
          <ion-spinner name="crescent" class="processing-badge" aria-hidden="true"></ion-spinner>
          <span class="sr-only">Video uploaded, compression in progress</span>
        </div>
        <!-- No thumbnail yet - show spinner -->
        <div v-else class="processing-spinner-container">
          <ion-spinner name="crescent" class="status-spinner" aria-hidden="true"></ion-spinner>
          <span class="status-text">Processing</span>
          <span class="sr-only">Processing video</span>
        </div>
      </div>

      <!-- Completed State -->
      <div v-else-if="status === 'completed'" class="status-completed">
        <img
          v-if="thumbnailUrl"
          :src="thumbnailUrl"
          :alt="`Day ${day} video thumbnail`"
          class="thumbnail-image"
          loading="lazy"
        />
        <div v-else class="thumbnail-placeholder">
          <ion-icon :icon="videocamOutline" class="placeholder-icon" aria-hidden="true"></ion-icon>
        </div>
        <div class="completed-overlay">
          <ion-icon :icon="playCircleOutline" class="play-icon" aria-hidden="true"></ion-icon>
        </div>
        <ion-icon :icon="checkmarkCircle" class="status-badge" aria-hidden="true"></ion-icon>
        <span class="sr-only">Completed - Click to view</span>
      </div>

      <!-- Failed State -->
      <div v-else-if="status === 'failed'" class="status-failed">
        <ion-icon :icon="closeCircleOutline" class="status-icon" aria-hidden="true"></ion-icon>
        <span class="status-text">Failed</span>
        <span class="sr-only">Upload failed - Click to retry</span>
      </div>
    </div>

    <!-- Error Message (Screen Reader) -->
    <div v-if="errorMessage" :id="`error-${day}`" class="sr-only" role="alert">
      Error: {{ errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonIcon, IonSpinner, IonProgressBar } from '@ionic/vue';
import {
  addCircleOutline,
  cloudUploadOutline,
  videocamOutline,
  playCircleOutline,
  checkmarkCircle,
  closeCircleOutline
} from 'ionicons/icons';

// Props
interface Props {
  day: number;
  status: 'empty' | 'uploading' | 'processing' | 'completed' | 'failed';
  thumbnailUrl?: string;
  progress?: number;
  errorMessage?: string;
  isDragging?: boolean;  // True if this card is being dragged
  isDragOver?: boolean;  // True if a dragged item is over this card
}

const props = withDefaults(defineProps<Props>(), {
  status: 'empty',
  progress: 0,
  isDragging: false,
  isDragOver: false
});

// Emits
const emit = defineEmits<{
  'click': [day: number];
  'dragstart': [day: number];
  'dragend': [];
  'dragover': [day: number];
  'dragleave': [day: number];
  'drop': [day: number];
}>();

// Computed: Can this card be dragged?
const isDraggable = computed(() => props.status === 'completed');

// Computed: Can this card receive drops?
const canReceiveDrop = computed(() =>
  props.status === 'empty' ||
  props.status === 'completed' ||
  props.status === 'failed'
);

// Computed: Does processing state have thumbnail?
const processingWithThumbnail = computed(() =>
  props.status === 'processing' && !!props.thumbnailUrl
);

// Computed classes for status styling
const dayCardClasses = computed(() => ({
  'day-card--empty': props.status === 'empty',
  'day-card--uploading': props.status === 'uploading',
  'day-card--processing': props.status === 'processing' && !props.thumbnailUrl,
  'day-card--processing-with-thumb': processingWithThumbnail.value,
  'day-card--completed': props.status === 'completed',
  'day-card--failed': props.status === 'failed',
  'day-card--interactive': props.status === 'empty' || props.status === 'failed' || props.status === 'completed' || processingWithThumbnail.value,
  'day-card--dragging': props.isDragging,
  'day-card--drag-over': props.isDragOver && canReceiveDrop.value,
  'day-card--draggable': isDraggable.value
}));

// Accessible label
const ariaLabel = computed(() => {
  const statusDescriptions = {
    empty: 'empty, click to upload video',
    uploading: `uploading, ${props.progress}% complete`,
    processing: 'processing video',
    completed: 'video uploaded, click to view or drag to move',
    failed: 'upload failed, click to retry'
  };

  let label = `Day ${props.day}, ${statusDescriptions[props.status]}`;

  if (props.isDragging) {
    label += '. Currently being dragged';
  }
  if (props.isDragOver && canReceiveDrop.value) {
    label += '. Drop here to ' + (props.status === 'completed' ? 'swap videos' : 'move video');
  }

  return label;
});

// Handle click/keyboard interaction
const handleClick = () => {
  emit('click', props.day);
};

// Drag and drop handlers
const handleDragStart = (e: DragEvent) => {
  if (!isDraggable.value) {
    e.preventDefault();
    return;
  }

  // Set drag data
  if (e.dataTransfer) {
    e.dataTransfer.setData('text/plain', props.day.toString());
    e.dataTransfer.effectAllowed = 'move';
  }

  emit('dragstart', props.day);
};

const handleDragEnd = () => {
  emit('dragend');
};

const handleDragOver = (e: DragEvent) => {
  if (!e.dataTransfer) return;

  if (!canReceiveDrop.value) {
    e.dataTransfer.dropEffect = 'none';
    return;
  }

  e.dataTransfer.dropEffect = 'move';
  emit('dragover', props.day);
};

const handleDragLeave = () => {
  emit('dragleave', props.day);
};

const handleDrop = () => {
  if (!canReceiveDrop.value) return;
  emit('drop', props.day);
};
</script>

<style scoped>
/* Day Card Base Styles - Intrinsically Responsive */
.day-card {
  position: relative;
  aspect-ratio: 1; /* Square cards */
  min-width: clamp(7rem, 22vw, 12rem);
  min-height: clamp(7rem, 22vw, 12rem);
  padding: clamp(0.75rem, 2.5vw, 1rem);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-base);
  container-type: inline-size;
  overflow: hidden;

  /* Touch-friendly minimum size */
  min-height: 44px;
  min-width: 44px;
}

/* Interactive states */
.day-card--interactive {
  cursor: pointer;
}

.day-card--interactive:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--ion-color-primary);
}

.day-card--interactive:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* Draggable state - show grab cursor on completed cards */
.day-card--draggable {
  cursor: grab;
}

.day-card--draggable:active {
  cursor: grabbing;
}

/* Dragging state - visual feedback when card is being dragged */
.day-card--dragging {
  opacity: 0.5;
  border-style: dashed;
  border-color: var(--ion-color-primary);
  transform: scale(0.95);
}

/* Drag over state - highlight valid drop targets */
.day-card--drag-over {
  border-color: var(--ion-color-tertiary);
  border-width: 3px;
  background: rgba(var(--ion-color-tertiary-rgb), 0.15);
  transform: scale(1.02);
  box-shadow: 0 0 12px rgba(var(--ion-color-tertiary-rgb), 0.4);
}

/* Swap indicator - show different style when hovering over another completed card */
.day-card--completed.day-card--drag-over {
  border-color: var(--ion-color-warning);
  background: rgba(var(--ion-color-warning-rgb), 0.15);
  box-shadow: 0 0 12px rgba(var(--ion-color-warning-rgb), 0.4);
}

/* Day Number */
.day-number {
  position: absolute;
  top: clamp(0.25rem, 1vw, 0.5rem);
  left: clamp(0.25rem, 1vw, 0.5rem);
  font-size: clamp(0.75rem, 2vw, 0.9rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  z-index: 2;
  background: rgba(255, 255, 255, 0.9);
  padding: clamp(0.1rem, 0.5vw, 0.25rem) clamp(0.25rem, 1vw, 0.4rem);
  border-radius: var(--radius-sm);
}

/* Dark mode day number */
@media (prefers-color-scheme: dark) {
  .day-number {
    background: rgba(0, 0, 0, 0.7);
    color: var(--color-text-primary);
  }
}

/* Status Content Container */
.status-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(0.25rem, 1vw, 0.5rem);
}

/* Common Status Icon Styling */
.status-icon {
  font-size: clamp(1.5rem, 5vw, 2.5rem);
  transition: transform var(--transition-base);
}

.day-card--interactive:hover .status-icon {
  transform: scale(1.1);
}

/* Empty State */
.day-card--empty {
  background: rgba(var(--ion-color-medium-rgb), 0.1);
  border-color: var(--ion-color-medium);
  border-style: dashed;
}

.status-empty .status-icon {
  color: var(--ion-color-medium);
  opacity: 0.6;
}

.day-card--empty:hover {
  background: rgba(var(--ion-color-primary-rgb), 0.05);
  border-color: var(--ion-color-primary);
}

.day-card--empty:hover .status-icon {
  color: var(--ion-color-primary);
  opacity: 1;
}

/* Uploading State */
.day-card--uploading {
  background: rgba(var(--ion-color-primary-rgb), 0.1);
  border-color: var(--ion-color-primary);
  cursor: default;
  pointer-events: none;
}

.status-uploading {
  text-align: center;
}

.status-uploading .status-icon {
  color: var(--ion-color-primary);
}

.animated-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

.upload-progress-bar {
  width: 80%;
  height: clamp(0.25rem, 1vw, 0.5rem);
  border-radius: var(--radius-full);
}

/* Processing State (no thumbnail yet) */
.day-card--processing {
  background: rgba(var(--ion-color-warning-rgb), 0.1);
  border-color: var(--ion-color-warning);
  cursor: default;
  pointer-events: none;
}

/* Processing State with thumbnail - looks like completed but with indicator */
.day-card--processing-with-thumb {
  background: rgba(var(--ion-color-success-rgb), 0.05);
  border-color: var(--ion-color-success);
  padding: 0;
}

.status-processing {
  width: 100%;
  height: 100%;
}

.processing-spinner-container {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(0.25rem, 1vw, 0.5rem);
}

.status-spinner {
  --color: var(--ion-color-warning);
  width: clamp(1.5rem, 5vw, 2rem);
  height: clamp(1.5rem, 5vw, 2rem);
}

/* Processing badge - small spinner in corner when thumbnail is shown */
.processing-badge {
  position: absolute;
  top: clamp(0.25rem, 1vw, 0.5rem);
  right: clamp(0.25rem, 1vw, 0.5rem);
  --color: var(--ion-color-warning);
  width: clamp(1rem, 3vw, 1.25rem);
  height: clamp(1rem, 3vw, 1.25rem);
  background: var(--color-surface);
  border-radius: var(--radius-full);
  padding: 2px;
  z-index: 2;
}

/* Completed State */
.day-card--completed {
  background: rgba(var(--ion-color-success-rgb), 0.05);
  border-color: var(--ion-color-success);
  padding: 0;
}

.status-completed {
  position: relative;
  width: 100%;
  height: 100%;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: calc(var(--radius-md) - 2px);
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--ion-color-success-rgb), 0.1);
}

.placeholder-icon {
  font-size: clamp(2rem, 6vw, 3rem);
  color: var(--ion-color-success);
  opacity: 0.5;
}

.completed-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  opacity: 0;
  transition: opacity var(--transition-base);
  border-radius: calc(var(--radius-md) - 2px);
}

.day-card--completed:hover .completed-overlay {
  opacity: 1;
}

.play-icon {
  font-size: clamp(2rem, 6vw, 3rem);
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.status-badge {
  position: absolute;
  top: clamp(0.25rem, 1vw, 0.5rem);
  right: clamp(0.25rem, 1vw, 0.5rem);
  font-size: clamp(1rem, 3vw, 1.25rem);
  color: var(--ion-color-success);
  background: var(--color-surface);
  border-radius: var(--radius-full);
  z-index: 2;
}

/* Failed State */
.day-card--failed {
  background: rgba(var(--ion-color-danger-rgb), 0.1);
  border-color: var(--ion-color-danger);
}

.status-failed .status-icon {
  color: var(--ion-color-danger);
}

.day-card--failed:hover {
  background: rgba(var(--ion-color-danger-rgb), 0.15);
  transform: translateY(-2px);
}

/* Status Text */
.status-text {
  font-size: clamp(0.7rem, 1.8vw, 0.85rem);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  text-align: center;
}

.day-card--uploading .status-text {
  color: var(--ion-color-primary);
}

.day-card--processing .status-text {
  color: var(--ion-color-warning);
}

.day-card--failed .status-text {
  color: var(--ion-color-danger);
}

/* Screen Reader Only Content */
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

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .day-card,
  .status-icon,
  .completed-overlay,
  .upload-progress-bar {
    animation: none;
    transition: none;
  }

  .day-card--interactive:hover {
    transform: none;
  }

  .day-card--dragging {
    transform: none;
  }

  .day-card--drag-over {
    transform: none;
  }
}

@media (prefers-contrast: high) {
  .day-card {
    border-width: 3px;
  }

  .day-number {
    font-weight: var(--font-weight-black);
  }
}

/* Container queries for very small cards */
@container (max-width: 5rem) {
  .day-number {
    font-size: 0.65rem;
    padding: 0.1rem 0.2rem;
  }

  .status-icon {
    font-size: 1.25rem;
  }

  .status-text {
    font-size: 0.65rem;
  }
}
</style>
