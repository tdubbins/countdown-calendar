<!--
  MobileVideoOverlay Component

  Simple fullscreen video overlay for mobile devices.
  Uses native video element without Ionic modal to allow native fullscreen player.

  Features:
  - Direct video element with native controls
  - Simple backdrop overlay
  - Touch-friendly close button (44px minimum)
  - No aspect-ratio constraints for natural video display
  - Direct URL streaming for public videos (memory efficient)

  For public videos (requireAuth=false): Uses direct URL for native browser streaming.
  For authenticated videos (requireAuth=true): Uses blob URL to include auth headers.

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

      <!-- Loading State -->
      <div v-if="isLoading" class="mobile-video-loading">
        <ion-spinner name="crescent" color="light"></ion-spinner>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="mobile-video-error">
        <p>{{ error }}</p>
      </div>

      <!-- Video Element - Direct URL for public, blob URL for authenticated -->
      <video
        v-else-if="mediaUrl"
        :src="mediaUrl"
        controls
        playsinline
        autoplay
        preload="metadata"
        class="mobile-video"
        @ended="handleVideoEnded"
        @loadeddata="onVideoLoaded"
        @error="onVideoError"
      >
        Your browser does not support video playback.
      </video>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { IonSpinner } from '@ionic/vue';
import { useMedia } from '@/composables/useMedia';

/**
 * Component Props
 */
interface Props {
  /** Whether overlay is visible */
  isOpen: boolean;

  /** Direct video URL */
  videoUrl: string;

  /** Whether JWT authentication is required (true for owner) */
  requireAuth?: boolean;
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

const props = withDefaults(defineProps<Props>(), {
  requireAuth: false
});
const emit = defineEmits<Emits>();

// Composables
const { fetchMedia } = useMedia();

// State
const mediaUrl = ref('');
const isLoading = ref(false);
const error = ref('');
const usingDirectUrl = ref(false);

/**
 * Load video - direct URL for public, blob for authenticated
 *
 * For public videos: Uses direct URL for native browser streaming.
 * This is critical for low-storage devices that can't hold entire videos in memory.
 *
 * For authenticated videos: Uses blob URL to include auth headers.
 */
const loadVideo = async () => {
  if (!props.isOpen || !props.videoUrl) return;

  error.value = '';

  // Public videos: use direct URL for native browser streaming
  if (!props.requireAuth) {
    isLoading.value = true;  // Will be set false by loadeddata event
    mediaUrl.value = props.videoUrl;
    usingDirectUrl.value = true;
    return;
  }

  // Authenticated videos: use blob URL approach
  try {
    isLoading.value = true;
    mediaUrl.value = await fetchMedia(props.videoUrl, props.requireAuth);
    usingDirectUrl.value = false;
  } catch (err: any) {
    error.value = err.message || 'Failed to load video';
    console.error('Mobile video loading error:', err);
  } finally {
    isLoading.value = false;
  }
};

/**
 * Handle video loaded event (for direct URL loading state)
 */
const onVideoLoaded = () => {
  isLoading.value = false;
};

/**
 * Handle video error event
 */
const onVideoError = () => {
  error.value = 'Failed to load video';
  isLoading.value = false;
};

/**
 * Handle overlay close
 */
const handleClose = () => {
  emit('close');
};

/**
 * Handle video playback ended
 */
const handleVideoEnded = () => {
  emit('video-ended');
};

// Load video when overlay opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    loadVideo();
  } else {
    // Clean up blob URL when closing (only if it's a blob URL)
    if (mediaUrl.value && !usingDirectUrl.value) {
      URL.revokeObjectURL(mediaUrl.value);
    }
    mediaUrl.value = '';
  }
}, { immediate: true });

// Clean up on unmount
onUnmounted(() => {
  // Only revoke if we created a blob URL (not for direct URLs)
  if (mediaUrl.value && !usingDirectUrl.value) {
    URL.revokeObjectURL(mediaUrl.value);
  }
});
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

/* Loading State */
.mobile-video-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

/* Error State */
.mobile-video-error {
  color: white;
  text-align: center;
  padding: 2rem;
}

.mobile-video-error p {
  margin: 0;
  font-size: 1rem;
}
</style>
