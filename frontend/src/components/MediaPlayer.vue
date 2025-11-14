<!--
  Media Component - Authenticated Image/Video Display

  A unified component for displaying images and videos with optional authentication.
  Fetches media from API, converts to blob URL, and displays with proper loading/error states.

  Usage:
    <Media
      src="/api/calendars/123/videos/1/thumbnail"
      mediaType="image"
      :requireAuth="true"
      alt="Day 1 thumbnail"
    />

  Features:
    - Supports both images and videos
    - Optional JWT authentication for owner access
    - Loading state while fetching
    - Error handling with user-friendly messages
    - Automatic blob URL cleanup on unmount
    - Memory management (revokes old blob URLs)

  NFR Compliance:
    - [S2] JWT authentication support
    - [U5] WCAG 2.1 AA - Accessible with ARIA labels and alt text
    - [P1] Fast loading with minimal blocking
    - [SC3] Modular, reusable component
-->

<template>
  <div class="media-container">
    <!-- Loading State: Show spinner while fetching media -->
    <div v-if="isLoading" class="media-loading" role="status" aria-live="polite">
      <ion-spinner name="circular" aria-label="Loading media" />
    </div>

    <!-- Error State: Display user-friendly error message -->
    <div
      v-else-if="error"
      class="media-error"
      role="alert"
      aria-live="assertive"
    >
      <ion-icon :icon="alertCircleOutline" aria-hidden="true" />
      <p>{{ error }}</p>
    </div>

    <!-- Image Display: Show image when loaded -->
    <img
      v-else-if="mediaType === 'image'"
      :src="blobUrl"
      :alt="alt"
      @load="onMediaLoad"
      @error="onMediaError"
    />

    <!-- Video Display: Show video player when loaded -->
    <video
      v-else-if="mediaType === 'video'"
      ref="videoRef"
      :src="blobUrl"
      controls
      @loadeddata="onMediaLoad"
      @error="onMediaError"
      @ended="handleVideoEnded"
    >
      <!-- Fallback text for browsers that don't support video -->
      Your browser does not support video playback.
    </video>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { IonSpinner, IonIcon } from '@ionic/vue'
import { alertCircleOutline } from 'ionicons/icons'
import { useMedia } from '@/composables/useMedia'

/**
 * Component Props
 */
interface Props {
  /** API endpoint URL for the media */
  src: string

  /** Type of media to display */
  mediaType: 'image' | 'video'

  /** Whether JWT authentication is required (true for owner, false for viewer) */
  requireAuth: boolean

  /** Alt text for images (accessibility) */
  alt?: string

  /** Auto-play video when loaded (only for videos) */
  autoplay?: boolean
}

/**
 * Component Emits
 */
interface Emits {
  /** Emitted when video playback ends */
  (e: 'ended'): void
}

const props = withDefaults(defineProps<Props>(), {
  alt: 'Media content',
  autoplay: false
})

const emit = defineEmits<Emits>()

// Composables
const { fetchMedia } = useMedia()

// State
const blobUrl = ref('')
const isLoading = ref(true)
const error = ref('')
const videoRef = ref<HTMLVideoElement>()

/**
 * Load media from API and create blob URL
 *
 * Fetches the media with optional authentication and converts
 * the response to a blob URL that can be displayed in the DOM.
 */
const loadMedia = async () => {
  try {
    isLoading.value = true
    error.value = ''

    // Fetch media and get blob URL
    blobUrl.value = await fetchMedia(props.src, props.requireAuth)
  } catch (err: any) {
    // Set user-friendly error message (NFR [U5]: Accessible errors)
    error.value = err.message || 'Failed to load media'
    console.error('Media loading error:', err)
  } finally {
    isLoading.value = false
  }
}

/**
 * Handle successful media load
 * Called when image loads or video metadata is loaded
 */
const onMediaLoad = () => {
  isLoading.value = false

  // Auto-play video if autoplay prop is true
  if (props.mediaType === 'video' && props.autoplay && videoRef.value) {
    videoRef.value.play().catch(err => {
      console.warn('Auto-play failed:', err)
    })
  }
}

/**
 * Handle media load error
 * Called when image or video fails to display
 */
const onMediaError = () => {
  error.value = 'Failed to display media'
  isLoading.value = false
}

/**
 * Handle video ended event
 * Forwards the event to parent component
 */
const handleVideoEnded = () => {
  emit('ended')
}

// Lifecycle: Load media on mount
onMounted(() => {
  loadMedia()
})

// Lifecycle: Clean up blob URL on unmount (prevent memory leaks)
onUnmounted(() => {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
  }
})

// Reactive: Reload media if src changes
watch(() => props.src, () => {
  // Clean up old blob URL before creating new one
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
  }
  loadMedia()
})

/**
 * Expose video element and play method to parent
 * Allows parent component to control video playback
 */
defineExpose({
  videoElement: videoRef,
  play: () => videoRef.value?.play()
})
</script>

<style scoped>
.media-container {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.media-loading,
.media-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 1rem;
  padding: 1rem;
}

.media-loading ion-spinner {
  width: 40px;
  height: 40px;
}

.media-error {
  color: var(--ion-color-danger);
  text-align: center;
}

.media-error ion-icon {
  font-size: 48px;
}

.media-error p {
  margin: 0;
  font-size: 14px;
}

img,
video {
  width: 100%;
  height: auto;
  display: block;
}

video {
  background: #000;
}
</style>
