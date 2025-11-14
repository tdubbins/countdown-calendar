<template>
  <button
    class="door-card"
    :class="[doorStateClass, { 'door-card--clickable': isClickable, 'door-card--playing-video': isPlayingVideo }]"
    :aria-label="ariaLabel"
    :aria-disabled="!isClickable"
    :disabled="!isClickable"
    :tabindex="isClickable ? 0 : -1"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
    role="button"
  >
    <!-- Day Number Badge with Debug Info -->
    <div class="door-number" aria-hidden="true">
      <div>Day {{ day.dayNumber }}</div>
      <div class="debug-state">State: {{ state }}</div>
      <div class="debug-state">Unlocked: {{ day.isUnlocked ? 'YES' : 'NO' }}</div>
      <div v-if="day.hasVideo" class="debug-state">Has Video: YES</div>
      <div v-if="day.thumbnailUrl" class="debug-state">Has Thumb: YES</div>
    </div>

    <!-- Door Content (icons for locked/unlocked states) -->
    <div class="door-content" v-if="!isPlayingVideo">
      <!-- State Icon -->
      <ion-icon
        :icon="stateIcon"
        class="door-icon"
        :class="`door-icon--${state}`"
        aria-hidden="true"
      ></ion-icon>

      <!-- Opened State: Show Checkmark -->
      <ion-icon
        v-if="state === 'opened'"
        :icon="checkmarkCircle"
        class="door-checkmark"
        aria-hidden="true"
      ></ion-icon>

      <!-- Locked State: Show Lock Icon -->
      <ion-icon
        v-if="state === 'locked'"
        :icon="lockClosedOutline"
        class="door-lock"
        aria-hidden="true"
      ></ion-icon>
    </div>

    <!-- Thumbnail for unlocked/opened doors (show if not playing video) -->
    <div
      v-if="state !== 'locked' && day.thumbnailUrl && !isPlayingVideo"
      class="door-thumbnail"
      :class="{ 'has-play-button': day.hasVideo && state === 'opened' }"
    >
      <MediaPlayer
        :src="thumbnailUrl"
        mediaType="image"
        :requireAuth="isOwner"
        :alt="`Thumbnail for day ${day.dayNumber}`"
      />

      <!-- Play button overlay if video exists -->
      <ion-icon
        v-if="day.hasVideo && state === 'opened'"
        :icon="playCircleOutline"
        class="play-button-overlay"
        aria-hidden="true"
      />
    </div>

    <!-- Video Player (shown when playing) -->
    <div v-if="isPlayingVideo" class="door-video">
      <MediaPlayer
        ref="videoMediaRef"
        :src="videoUrl"
        mediaType="video"
        :requireAuth="isOwner"
        :autoplay="true"
        @ended="onVideoEnded"
      />
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue';
import { IonIcon } from '@ionic/vue';
import {
  lockClosedOutline,
  giftOutline,
  checkmarkCircle,
  playCircleOutline
} from 'ionicons/icons';
import { SharedCalendarDay } from '@/composables/useSharedCalendar';
import {
  useDoorState,
  getDoorStateClass,
  isDoorClickable,
  getDoorAriaLabel,
  getDoorStateIcon
} from '@/composables/useDoorState';
import MediaPlayer from '@/components/MediaPlayer.vue';

// Props
interface Props {
  day: SharedCalendarDay;
  calendarId: string; // Calendar ID for constructing media URLs
  startDate?: string; // Optional to handle loading state
  isDayOpened: (dayNumber: number) => boolean;
  isOwner?: boolean; // Whether viewer is the calendar owner
}

const props = withDefaults(defineProps<Props>(), {
  isOwner: false
});

// Emits
const emit = defineEmits<{
  doorClick: [dayNumber: number];
}>();

// State
const isPlayingVideo = ref(false);
const videoMediaRef = ref<InstanceType<typeof MediaPlayer>>();

// Composables
const state = useDoorState(props.day, props.isDayOpened);

// Computed Properties
const doorStateClass = computed(() => getDoorStateClass(state.value));
const isClickable = computed(() => isDoorClickable(state.value));
const ariaLabel = computed(() =>
  getDoorAriaLabel(props.day.dayNumber, state.value, props.startDate)
);

// State icon based on door state
const stateIcon = computed(() => {
  const iconName = getDoorStateIcon(state.value);
  switch (iconName) {
    case 'lock-closed-outline':
      return lockClosedOutline;
    case 'checkmark-circle-outline':
      return checkmarkCircle;
    case 'gift-outline':
    default:
      return giftOutline;
  }
});

// Media URLs (constructed from calendar ID and day number)
// Use absolute URLs with API base to ensure correct backend endpoint
const thumbnailUrl = computed(() =>
  `http://localhost:5001/api/calendars/${props.calendarId}/videos/${props.day.dayNumber}/thumbnail`
);

const videoUrl = computed(() =>
  `http://localhost:5001/api/calendars/${props.calendarId}/videos/${props.day.dayNumber}/stream`
);

/**
 * Handle door click
 *
 * Flow:
 * 1. Check current state before parent updates it
 * 2. Emit doorClick event to parent to mark as opened
 * 3. Show video player (autoplay will handle starting playback)
 */
const handleClick = async () => {
  if (!isClickable.value) return;

  // Capture current state before parent updates it
  const wasUnlocked = state.value === 'unlocked';
  const isAlreadyOpened = state.value === 'opened';

  // Emit door click to mark as opened in parent
  emit('doorClick', props.day.dayNumber);

  // If door has video, show video player
  if (props.day.hasVideo) {
    // If opening door for first time (was unlocked), show video player (autoplay enabled)
    if (wasUnlocked) {
      // Wait for parent to update isDayOpened state
      await nextTick();
      // Wait for state to recompute
      await nextTick();

      // Show video player (autoplay prop will start playback automatically)
      isPlayingVideo.value = true;
    }

    // If door already opened, toggle video playback on thumbnail click
    if (isAlreadyOpened && !isPlayingVideo.value) {
      // Show video player (autoplay prop will start playback automatically)
      isPlayingVideo.value = true;
    }
  }
};

/**
 * Handle video ended
 * Return to thumbnail view when video finishes playing
 */
const onVideoEnded = () => {
  isPlayingVideo.value = false;
};
</script>

<style scoped>
/* Base Door Card Styles */
.door-card {
  position: relative;
  aspect-ratio: 1;
  min-height: 9rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
  transition: all var(--transition-base);
  border: none;
  cursor: default;

  /* NFR [U2]: Touch-friendly minimum size (44px+) */
  min-width: 44px;
  min-height: 140px;

  /* Remove button defaults */
  font-family: inherit;
  width: 100%;
}

/* NFR [U5]: Focus indicator for keyboard navigation */
.door-card:focus-visible {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* State 1: Locked Door 🔒 */
.door-card--locked {
  background: linear-gradient(135deg, #4a5568, #2d3748);
  cursor: not-allowed;
  pointer-events: none;
  position: relative;
  z-index: 1;
}

/* Ensure locked doors are opaque (no thumbnail should show) */
.door-card--locked::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #4a5568, #2d3748);
  opacity: 1;
  z-index: 0;
  border-radius: var(--radius-md);
}

.door-card--locked .door-icon {
  color: #9ca3af;
  font-size: clamp(2rem, 6vw, 3rem);
}

.door-card--locked .door-lock {
  position: absolute;
  font-size: clamp(1.5rem, 4vw, 2rem);
  color: #6b7280;
  margin-top: 0.5rem;
}

/* State 2: Unlocked Door (Ready to Open) */
.door-card--unlocked {
  background: linear-gradient(135deg, #c41e3a 0%, #165b33 100%);
  border: 2px solid #ffd700;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  position: relative;
}

/* Add opaque overlay to unlocked doors so thumbnail doesn't bleed through too much */
.door-card--unlocked::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(196, 30, 58, 0.85) 0%, rgba(22, 91, 51, 0.85) 100%);
  z-index: 0;
  border-radius: var(--radius-md);
  pointer-events: none;
}

.door-card--unlocked:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

.door-card--unlocked:active {
  transform: scale(0.98);
}

.door-card--unlocked .door-icon {
  color: #ffd700;
  font-size: clamp(2.5rem, 7vw, 3.5rem);
}

/* State 3: Opened Door (Already Watched) ✅ */
.door-card--opened {
  background: #2c5f2d;
  opacity: 0.85;
  border: 2px solid #165b33;
  cursor: pointer;
}

.door-card--opened:hover {
  opacity: 1;
  transform: scale(1.02);
}

.door-card--opened .door-icon {
  color: #a3e635;
  font-size: clamp(2rem, 6vw, 2.5rem);
}

.door-card--opened .door-checkmark {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  color: #4ade80;
  z-index: 2;
}

/* Day Number Badge */
.door-number {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.95);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  z-index: 2;
  /* NFR [U5]: Color contrast 4.5:1 */
  text-shadow: none;
  /* Debug mode: Make badge larger for extra info */
  line-height: 1.3;
  max-width: 90%;
}

@media (prefers-color-scheme: dark) {
  .door-number {
    background: rgba(0, 0, 0, 0.8);
    color: #ffffff;
  }
}

/* Debug State Display */
.debug-state {
  font-size: 0.65rem;
  font-weight: normal;
  color: #dc2626; /* Red color for visibility */
  line-height: 1.2;
  margin-top: 0.1rem;
}

@media (prefers-color-scheme: dark) {
  .debug-state {
    color: #fca5a5; /* Lighter red for dark mode */
  }
}

/* Door Content Container */
.door-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1; /* Above the gradient overlay */
}

/* Door Icon */
.door-icon {
  transition: all var(--transition-base);
}

/* Thumbnail Display (only for unlocked/opened doors) */
.door-thumbnail {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  z-index: 0;
  /* Note: Locked doors never show thumbnail (v-if prevents rendering) */
}

.door-thumbnail :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Play Button Overlay */
.play-button-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: clamp(3rem, 8vw, 4rem);
  color: rgba(255, 255, 255, 0.95);
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.5));
  pointer-events: none;
  z-index: 10;
  transition: transform 0.2s ease, color 0.2s ease;
}

/* Play button hover effect (when parent door card is hovered) */
.door-thumbnail.has-play-button:hover .play-button-overlay {
  transform: translate(-50%, -50%) scale(1.15);
  color: rgba(255, 255, 255, 1);
}

/* Unlocked state: Hide thumbnail completely (door is closed) */
.door-card--unlocked .door-thumbnail {
  display: none;
}

/* Opened state: Show thumbnail at full opacity (primary content) */
.door-card--opened .door-thumbnail {
  opacity: 1.0;
  z-index: 1; /* Bring thumbnail above door-content */
}

/* Opened state: Hide icons when thumbnail is showing */
.door-card--opened .door-content {
  opacity: 0;
  pointer-events: none;
}

/* Video Display */
.door-video {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  z-index: 10; /* Above everything else */
  background: #000;
}

.door-video :deep(video) {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* Playing video state: Hide all other content */
.door-card--playing-video .door-content,
.door-card--playing-video .door-thumbnail {
  display: none;
}

/* NFR [U5]: Accessibility - Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .door-card {
    transition: none;
  }

  .door-card--unlocked:hover,
  .door-card--opened:hover {
    transform: none;
  }
}

/* NFR [U5]: High contrast mode */
@media (prefers-contrast: high) {
  .door-card--locked {
    border: 3px solid #6b7280;
  }

  .door-card--unlocked {
    border-width: 3px;
  }

  .door-card--opened {
    border-width: 3px;
  }

  .door-number {
    font-weight: var(--font-weight-black);
    border: 1px solid currentColor;
  }
}

/* Responsive adjustments for very small screens */
@media (max-width: 640px) {
  .door-card {
    min-height: 140px;
    padding: var(--spacing-sm);
  }

  .door-number {
    font-size: 0.8rem;
    padding: 0.2rem 0.4rem;
  }
}

/* Container queries for extra small screens */
@container (max-width: 20rem) {
  .door-number {
    font-size: 0.75rem;
    padding: 0.15rem 0.35rem;
  }

  .door-icon {
    font-size: 1.5rem !important;
  }
}
</style>
