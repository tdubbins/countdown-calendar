<!--
  MobileVideoOverlay Component

  Simple fullscreen video overlay for mobile devices.
  Uses native video element without Ionic modal to allow native fullscreen player.

  Features:
  - Direct video element with native controls
  - Simple backdrop overlay
  - Touch-friendly close button (44px minimum)
  - No aspect-ratio constraints for natural video display

  Optimized for mobile with accessible controls.
-->

<template>
  <div
    v-if="isOpen"
    class="mobile-video-overlay"
    @click="handleClose"
  >
    <div class="mobile-video-container" @click.stop>
      <!-- Close Button -->
      <button
        class="mobile-close-button"
        @click="handleClose"
        aria-label="Close video"
      >
        ✕
      </button>

      <!-- Direct Video Element - No wrappers for native playback -->
      <video
        :src="videoUrl"
        controls
        playsinline
        autoplay
        class="mobile-video"
        @ended="handleVideoEnded"
      >
        Your browser does not support video playback.
      </video>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Component Props
 */
interface Props {
  /** Whether overlay is visible */
  isOpen: boolean;

  /** Direct video URL */
  videoUrl: string;
}

/**
 * Component Emits
 */
interface Emits {
  /** Emitted when overlay should close */
  (e: 'close'): void;

  /** Emitted when video playback ends */
  (e: 'video-ended'): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

/**
 * Handle overlay close
 * Emits close event to parent
 */
const handleClose = () => {
  emit('close');
};

/**
 * Handle video playback ended
 * Emits video-ended event to parent
 */
const handleVideoEnded = () => {
  emit('video-ended');
};
</script>

<style scoped>
/* Mobile Video Overlay - Simple fullscreen video without Ionic modal */
.mobile-video-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.mobile-video-container {
  position: relative;
  width: 100%;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-close-button {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 10;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  /* Touch-friendly minimum size */
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.mobile-close-button:active {
  background: rgba(0, 0, 0, 0.9);
}

/* Focus indicator for keyboard navigation */
.mobile-close-button:focus-visible {
  outline: 2px solid white;
  outline-offset: 2px;
}

.mobile-video {
  width: 100%;
  max-width: 100%;
  height: auto;
  max-height: 90vh;
  display: block;
  background: #000;
}
</style>
