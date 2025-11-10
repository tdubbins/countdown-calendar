<template>
  <div
    class="day-card"
    :class="dayCardClasses"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    tabindex="0"
    role="button"
    :aria-label="ariaLabel"
    :aria-describedby="errorMessage ? `error-${day}` : undefined"
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
        <div v-if="progress !== undefined" class="progress-indicator">
          <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
        </div>
        <span class="status-text">{{ progress }}%</span>
        <span class="sr-only">Uploading - {{ progress }}% complete</span>
      </div>

      <!-- Processing State -->
      <div v-else-if="status === 'processing'" class="status-processing">
        <ion-spinner name="crescent" class="status-spinner" aria-hidden="true"></ion-spinner>
        <span class="status-text">Processing</span>
        <span class="sr-only">Processing video</span>
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
import { IonIcon, IonSpinner } from '@ionic/vue';
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
}

const props = withDefaults(defineProps<Props>(), {
  status: 'empty',
  progress: 0
});

// Emits
const emit = defineEmits<{
  'click': [day: number];
}>();

// Computed classes for status styling
const dayCardClasses = computed(() => ({
  'day-card--empty': props.status === 'empty',
  'day-card--uploading': props.status === 'uploading',
  'day-card--processing': props.status === 'processing',
  'day-card--completed': props.status === 'completed',
  'day-card--failed': props.status === 'failed',
  'day-card--interactive': props.status === 'empty' || props.status === 'failed' || props.status === 'completed'
}));

// Accessible label
const ariaLabel = computed(() => {
  const statusDescriptions = {
    empty: 'empty, click to upload video',
    uploading: `uploading, ${props.progress}% complete`,
    processing: 'processing video',
    completed: 'video uploaded, click to view',
    failed: 'upload failed, click to retry'
  };

  return `Day ${props.day}, ${statusDescriptions[props.status]}`;
});

// Handle click/keyboard interaction
const handleClick = () => {
  emit('click', props.day);
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

  /* NFR [U2]: Touch-friendly minimum size */
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

.progress-indicator {
  width: 80%;
  height: clamp(0.25rem, 1vw, 0.375rem);
  background: rgba(var(--ion-color-primary-rgb), 0.2);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--ion-color-primary);
  transition: width 0.3s ease;
  border-radius: var(--radius-full);
}

/* Processing State */
.day-card--processing {
  background: rgba(var(--ion-color-warning-rgb), 0.1);
  border-color: var(--ion-color-warning);
  cursor: default;
  pointer-events: none;
}

.status-processing {
  text-align: center;
}

.status-spinner {
  --color: var(--ion-color-warning);
  width: clamp(1.5rem, 5vw, 2rem);
  height: clamp(1.5rem, 5vw, 2rem);
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
  background: white;
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
  .progress-bar {
    animation: none;
    transition: none;
  }

  .day-card--interactive:hover {
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
