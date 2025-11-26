<template>
  <button
    class="door-card"
    :class="[
      doorStateClass,
      themeClass,
      state,
      {
        'door-card--clickable': isClickable,
        'door-card--opening': isOpening
      }
    ]"
    :aria-label="ariaLabel"
    :aria-disabled="!isClickable"
    :disabled="!isClickable"
    :tabindex="isClickable ? 0 : -1"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
    role="button"
  >
    <!-- Day Number -->
    <div class="door-number" aria-hidden="true">
      {{ day.dayNumber }}
    </div>

    <!-- Door Content (icons for locked/unlocked states) -->
    <div class="door-content">
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

    <!-- Thumbnail for unlocked/opened doors -->
    <div
      v-if="state !== 'locked' && day.thumbnailUrl"
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
  </button>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { IonIcon } from '@ionic/vue';
import { API_ENDPOINTS } from '@/config/api';
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
  theme?: string; // Theme identifier (e.g., 'christmas', 'birthday', 'generic')
}

const props = withDefaults(defineProps<Props>(), {
  isOwner: false,
  theme: 'christmas'
});

// Emits
const emit = defineEmits<{
  doorClick: [dayNumber: number];
}>();

// Animation state
const isOpening = ref(false);

// Composables
const state = useDoorState(props.day, props.isDayOpened);

// Computed Properties
const doorStateClass = computed(() => getDoorStateClass(state.value));
const isClickable = computed(() => isDoorClickable(state.value));
const ariaLabel = computed(() =>
  getDoorAriaLabel(props.day.dayNumber, state.value, props.startDate)
);
const themeClass = computed(() => `theme-${props.theme}`);

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

// Thumbnail URL (constructed from calendar ID and day number)
// Uses centralized API config for proper URL construction
const thumbnailUrl = computed(() =>
  API_ENDPOINTS.VIDEO_THUMBNAIL(props.calendarId, props.day.dayNumber)
);

/**
 * Handle door click
 * Door opens fully, video grows from tiny to large
 *
 * Animation Timeline:
 * 0ms:     Door starts opening (smooth, to 90 degrees)
 * 700ms:   Door opening, emit event (video starts growing from tiny)
 * 1800ms:  Door fully open, reset animation state
 * 1900ms:  Video fully grown and playing
 */
const handleClick = () => {
  if (!isClickable.value || isOpening.value) return;

  // Skip animation for already-opened doors (just open modal immediately)
  if (state.value === 'opened') {
    emit('doorClick', props.day.dayNumber);
    return;
  }

  // Start door opening animation
  isOpening.value = true;

  // Emit event early so video starts growing as door opens
  setTimeout(() => {
    emit('doorClick', props.day.dayNumber);
  }, 700);

  // Reset animation state after complete
  setTimeout(() => {
    isOpening.value = false;
  }, 1800);
};
</script>

<style scoped>
/* Import all theme styles (doors, backgrounds, text, letterbox) */
@import '@/theme/themes/index.css';

/**
 * Base Door Card Styles
 *
 * MINIMAL STRUCTURAL CSS ONLY - No colors, shadows, or decorative styling!
 * Themes control ALL visual appearance via door-themes.css
 *
 * This file only handles:
 * - Layout (flexbox, positioning, sizing)
 * - Interactions (cursor, animations, pointer events)
 * - Accessibility (focus, reduced motion, touch targets)
 */

/* Base card structure */
.door-card {
  /* Layout */
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 1;

  /* Sizing with theme variable fallbacks */
  padding: var(--door-padding, var(--spacing-md));
  border-radius: var(--door-border-radius, var(--radius-md));

  /* Touch-friendly minimum size */
  /* Use clamp for fluid sizing that works in all orientations */
  min-width: clamp(44px, 12vmin, 160px);
  min-height: clamp(44px, 12vmin, 160px);

  /* Interaction */
  cursor: default;
  border: none;
  transition: all var(--transition-base);

  /* Remove button defaults */
  font-family: inherit;
}

/* Focus indicator for keyboard navigation */
.door-card:focus-visible {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* State: Locked Door - Structure only */
.door-card--locked {
  cursor: not-allowed;
  pointer-events: none;
}

/* State: Unlocked Door - Structure only */
.door-card--unlocked {
  cursor: pointer;
}

.door-card--unlocked:active {
  transform: scale(0.98);
}

/* State: Opened Door - Structure only */
.door-card--opened {
  cursor: pointer;
}

/* Door Opening Animation (3D swing) */
@keyframes swingOpenLeft {
  0% {
    transform: perspective(1200px) rotateY(0deg);
    opacity: 1;
  }
  100% {
    transform: perspective(1200px) rotateY(-90deg);
    opacity: 0.1;
  }
}

.door-card--unlocked.door-card--opening {
  animation: swingOpenLeft 1.8s ease-out forwards;
  transform-origin: left center;
  will-change: transform, opacity;
  pointer-events: none;
}

/* Day Number Badge - Position only, theme handles styling */
.door-number {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  z-index: 10;
  line-height: 1;
  /* Font size and colors controlled by theme */
  font-size: var(--door-number-size, 1.5rem);
  font-weight: var(--door-number-weight, var(--font-weight-bold));
}

/* Door Content Container - Icons and content positioning */
.door-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
}

/* Thumbnail Display - Layout only */
.door-thumbnail {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
  border-radius: inherit;
}

.door-thumbnail :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Play Button Overlay - Position only, theme handles colors */
.play-button-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: clamp(3rem, 8vw, 4rem);
  pointer-events: none;
  z-index: 10;
  transition: transform 0.2s ease;
  /* Colors controlled by theme or use white as default */
  color: rgba(255, 255, 255, 0.95);
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.5));
}

.door-thumbnail.has-play-button:hover .play-button-overlay {
  transform: translate(-50%, -50%) scale(1.15);
}

/* Hide thumbnail on unlocked (closed) doors */
.door-card--unlocked .door-thumbnail {
  display: none;
}

/* Show thumbnail on opened doors */
.door-card--opened .door-thumbnail {
  z-index: 1;
}

/* Hide door icons when showing thumbnail (opened state) */
.door-card--opened .door-content {
  opacity: 0;
  pointer-events: none;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .door-card {
    transition: none;
  }

  /* Replace 3D swing with simple fade */
  @keyframes simpleFadeOut {
    0% {
      opacity: 1;
    }
    100% {
      opacity: 0;
    }
  }

  .door-card--unlocked.door-card--opening {
    animation: simpleFadeOut 0.9s ease-out forwards;
    transform: none;
    will-change: opacity;
  }
}
</style>
