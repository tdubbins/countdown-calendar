<!--
  VideoModal Component

  Displays calendar day videos in a modal overlay (larger view, not fullscreen).
  Opens when user clicks an unlocked/opened door card.

  Features:
  - Modal backdrop with click-to-close
  - Keyboard controls (ESC to close)
  - Reuses MediaPlayer component for video playback
  - Responsive sizing (80% mobile, 70% desktop, max 900px)
  - Accessible with ARIA labels and focus management

  NFR Compliance:
  - [U5] WCAG 2.1 AA - Keyboard navigation, ARIA labels, focus trap
  - [U2] Touch-friendly - Close button 44px minimum
  - [U1] Responsive - Works on 320px+ screens
  - [SC3] Modular - Reuses MediaPlayer component
-->

<template>
  <!-- Desktop: Full Ionic Modal with tree decorations -->
  <ion-modal
    v-if="!isMobile"
    :is-open="isOpen"
    :backdrop-dismiss="true"
    @didDismiss="handleClose"
    class="video-modal-fullscreen"
  >
    <ion-page class="video-modal-page">
      <ion-content class="video-modal-content">
        <!-- Modal Container (no backdrop) -->
        <div
          class="video-modal-container"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="`video-title-${dayNumber}`"
          @click.stop
          @keydown.esc="handleClose"
        >
          <!-- Close Button -->
          <ion-button
            class="close-button"
            fill="clear"
            color="light"
            @click="handleClose"
            aria-label="Close video modal"
          >
            <ion-icon slot="icon-only" :icon="closeOutline"></ion-icon>
          </ion-button>

          <!-- Video Title (screen reader only) -->
          <h2 :id="`video-title-${dayNumber}`" class="sr-only">
            Day {{ dayNumber }} Video
          </h2>

          <!-- Video Player -->
          <div class="video-player-wrapper" :class="themeClass">
            <MediaPlayer
              v-if="videoUrl"
              :src="videoUrl"
              mediaType="video"
              :requireAuth="requireAuth"
              :autoplay="shouldAutoplay"
              @ended="handleVideoEnded"
            />
          </div>
        </div>
      </ion-content>
    </ion-page>
  </ion-modal>

  <!-- Mobile: Simple Overlay with Native Video Player -->
  <MobileVideoOverlay
    v-if="isMobile"
    :is-open="isOpen"
    :video-url="videoUrl"
    @close="handleClose"
    @video-ended="handleMobileVideoEnded"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonModal, IonPage, IonContent, IonButton, IonIcon, isPlatform } from '@ionic/vue';
import { closeOutline } from 'ionicons/icons';
import MediaPlayer from './MediaPlayer.vue';
import MobileVideoOverlay from './MobileVideoOverlay.vue';
import { API_ENDPOINTS } from '@/config/api';

/**
 * Component Props
 */
interface Props {
  /** Whether modal is visible */
  isOpen: boolean;

  /** Calendar ID for video URL construction */
  calendarId: string;

  /** Day number for video playback */
  dayNumber: number;

  /** Whether viewer is calendar owner (affects auth) */
  requireAuth: boolean;

  /** Theme ID for styling letterbox decorations */
  theme?: string;
}

/**
 * Component Emits
 */
interface Emits {
  /** Emitted when modal should close */
  (e: 'close'): void;

  /** Emitted when video playback ends */
  (e: 'video-ended', dayNumber: number): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Reactive video URL - updates when dayNumber prop changes
// Uses centralized API config for proper URL construction
const videoUrl = computed(() =>
  API_ENDPOINTS.VIDEO_STREAM(props.calendarId, props.dayNumber)
);

// Theme class for letterbox decorations
const themeClass = computed(() => {
  return props.theme ? `theme-${props.theme}` : 'theme-christmas';
});

/**
 * Detect mobile/tablet device using Ionic's Platform API
 * Use simple overlay for mobile/tablet, full modal for desktop
 *
 * Ionic's isPlatform() is the professional, maintained solution that:
 * - Handles iOS 13+ iPad detection properly
 * - Works across all devices and browsers
 * - Automatically maintained by Ionic team
 * - More reliable than user agent sniffing
 */
const isMobile = computed(() => {
  return isPlatform('mobile') || isPlatform('tablet') || isPlatform('ipad');
});

/**
 * Enable autoplay for all devices
 * Note: Mobile browsers may still block autoplay with sound due to browser policies
 * If blocked, user must tap to play
 */
const shouldAutoplay = computed(() => {
  return true; // Attempt autoplay on all devices
});

/**
 * Handle modal close
 * Emits close event to parent
 */
const handleClose = () => {
  emit('close');
};

/**
 * Handle video playback ended (Desktop)
 * Keep modal open briefly so user sees the completed state
 */
const handleVideoEnded = () => {
  emit('video-ended', props.dayNumber);

  // Auto-close after 2 seconds (so user sees video ended state)
  setTimeout(() => {
    handleClose();
  }, 2000);
};

/**
 * Handle video playback ended (Mobile)
 * Close immediately on mobile (simpler UX)
 */
const handleMobileVideoEnded = () => {
  emit('video-ended', props.dayNumber);
  handleClose();
};
</script>

<style scoped>
/* Override Ionic Modal defaults - Make it completely transparent */
.video-modal-fullscreen {
  --background: transparent;
  --width: 100%;
  --height: 100%;
  --border-radius: 0;
  --box-shadow: none;
}

.video-modal-page {
  background: transparent;
}

/* Modal Content - Full viewport */
.video-modal-content {
  --background: transparent;
  pointer-events: none; /* Allow clicking through to close */
}

/* Modal Container - Just the video, no backgrounds */
.video-modal-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 900px;
  z-index: 2;
  background: transparent;
  border-radius: var(--radius-lg, 12px);
  overflow: visible;
  pointer-events: auto; /* Re-enable for video interaction */

  /* Video grows from tiny (emerging from door) */
  animation: videoGrowFromDoor 1.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes videoGrowFromDoor {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.08);
  }
  20% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

/* Close Button - Top-right corner */
.close-button {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 10;
  --background: rgba(0, 0, 0, 0.6);
  --background-hover: rgba(0, 0, 0, 0.8);
  --color: white;
  --padding: 0.5rem;

  /* NFR [U2]: Touch-friendly minimum size */
  min-width: 44px;
  min-height: 44px;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full, 50%);
  backdrop-filter: blur(8px);
}

.close-button ion-icon {
  font-size: 1.5rem;
}

/* NFR [U5]: Focus indicator for keyboard navigation */
.close-button:focus-visible {
  outline: 2px solid white;
  outline-offset: 2px;
}

/* Video Player Wrapper - 16:9 aspect ratio with black background */
/* Theme-specific letterbox decorations are defined in theme files */
.video-player-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000000; /* Black bars for vertical videos, covered by horizontal videos */
  overflow: hidden;
}

.video-player-wrapper :deep(video) {
  position: relative;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: transparent;
  z-index: 1; /* Ensure video is always above theme decorations */
}

/* Screen Reader Only */
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

/* NFR [U1]: Responsive - Mobile - Only applies to desktop modal when shown on smaller screens */
@media (max-width: 640px) {
  .video-modal-container {
    width: 95%;
    max-width: none;
  }

  .close-button {
    top: 0.25rem;
    right: 0.25rem;
  }
}

/* Desktop - Narrower width */
@media (min-width: 1024px) {
  .video-modal-container {
    width: 70%;
  }
}

/* NFR [U5]: Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .video-modal-container {
    animation: none;
  }
}

/* NFR [U5]: High contrast mode */
@media (prefers-contrast: high) {
  .close-button {
    border: 2px solid white;
  }
}
</style>
