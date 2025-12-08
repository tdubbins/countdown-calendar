<!--
  Media Component - Authenticated Image/Video Display

  A unified component for displaying images and videos with optional authentication.

  For videos without auth (public viewers): Uses direct URL for native browser streaming.
  This allows the browser to efficiently buffer and stream video without loading
  the entire file into memory - critical for low-storage devices like iPads.

  For videos with auth (owners) and images: Uses blob URL approach to include
  authentication headers in the request.
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
      <ion-icon :icon="giftOutline" aria-hidden="true" />
      <p>{{ error }}</p>
    </div>

    <!-- Image Display: Show image when loaded -->
    <img
      v-else-if="mediaType === 'image'"
      :src="mediaUrl"
      :alt="alt"
      loading="lazy"
      @load="onMediaLoad"
      @error="onMediaError"
    />

    <!-- Video Display: Show video player when loaded -->
    <video
      v-else-if="mediaType === 'video'"
      ref="videoRef"
      :src="mediaUrl"
      controls
      preload="metadata"
      playsinline
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
import { giftOutline } from 'ionicons/icons'
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
const mediaUrl = ref('')
const isLoading = ref(true)
const error = ref('')
const videoRef = ref<HTMLVideoElement>()
const usingDirectUrl = ref(false)

/**
 * Load media from API or set direct URL
 *
 * For public videos (requireAuth=false): Uses direct URL for native browser streaming.
 * This allows efficient buffering without loading the entire video into memory.
 *
 * For authenticated videos/images: Uses blob URL approach to include auth headers.
 */
const loadMedia = async () => {
  error.value = ''

  // Public videos: use direct URL for native browser streaming
  // This is critical for low-storage devices (e.g., iPads) that can't hold
  // entire video files in memory
  if (props.mediaType === 'video' && !props.requireAuth) {
    isLoading.value = true  // Will be set false by loadeddata event
    mediaUrl.value = props.src
    usingDirectUrl.value = true
    return
  }

  // Authenticated videos or images: use blob URL approach
  try {
    isLoading.value = true
    mediaUrl.value = await fetchMedia(props.src, props.requireAuth)
    usingDirectUrl.value = false
  } catch (err: any) {
    // Set user-friendly error message
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
  // Only revoke if we created a blob URL (not for direct URLs)
  if (mediaUrl.value && !usingDirectUrl.value) {
    URL.revokeObjectURL(mediaUrl.value)
  }
})

// Reactive: Reload media if src changes
watch(() => props.src, () => {
  // Clean up old blob URL before creating new one (only if it's a blob URL)
  if (mediaUrl.value && !usingDirectUrl.value) {
    URL.revokeObjectURL(mediaUrl.value)
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
  color: white;
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
  background: transparent;
}
</style>
