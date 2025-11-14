<template>
  <ion-modal
    :is-open="isOpen"
    @didDismiss="handleClose"
  >
    <ion-page>
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>Share Calendar</ion-title>
          <ion-buttons slot="end">
            <ion-button
              @click="handleClose"
              aria-label="Close share modal"
            >
              <ion-icon :icon="close" slot="icon-only"></ion-icon>
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>

      <ion-content class="ion-padding">
        <!-- Loading State -->
        <div v-if="isGenerating" class="loading-state">
          <ion-spinner name="crescent" color="primary"></ion-spinner>
          <p>Generating share link...</p>
        </div>

        <!-- Share URL Display (shows when token exists) -->
        <div v-else-if="shareUrl" class="shared-state">
          <ion-icon :icon="checkmarkCircle" class="success-icon" color="success"></ion-icon>
          <h2>Calendar Shared!</h2>
          <p class="description">
            Anyone with this link can view your calendar.
          </p>

          <!-- Share URL Display -->
          <div class="url-container">
            <ion-input
              :value="shareUrl"
              readonly
              class="share-url-input"
              aria-label="Share URL"
            ></ion-input>
          </div>

          <!-- Copy Button -->
          <ion-button
            expand="block"
            color="success"
            size="large"
            @click="handleCopyToClipboard"
            class="copy-button"
            :disabled="isCopying"
            aria-label="Copy share link to clipboard"
          >
            <ion-icon
              :icon="isCopied ? checkmarkOutline : copyOutline"
              slot="start"
            ></ion-icon>
            {{ isCopied ? 'Copied!' : 'Copy Link' }}
          </ion-button>

          <p v-if="isCopied" class="copy-success-message" role="status" aria-live="polite">
            Link copied to clipboard!
          </p>
        </div>
      </ion-content>
    </ion-page>
  </ion-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  IonModal,
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonButtons,
  IonIcon,
  IonInput,
  IonSpinner
} from '@ionic/vue';
import {
  close,
  // shareSocialOutline, // Reserved for future social sharing feature
  // linkOutline, // Reserved for future use
  checkmarkCircle,
  copyOutline,
  checkmarkOutline
} from 'ionicons/icons';

/**
 * ShareModal Component (Issue #78)
 *
 * A modal for sharing calendars with two states:
 * 1. Not Shared: Shows "Generate Share Link" button
 * 2. Already Shared: Shows share URL with copy functionality
 *
 * Features:
 * - Lazy share token generation
 * - Copy to clipboard with fallback support
 * - Loading states during API calls
 * - Accessible keyboard navigation
 * - Touch-friendly buttons (44px+ targets)
 */

interface Props {
  isOpen: boolean;
  calendarId: string;
  existingShareToken?: string | null;
}

interface Emits {
  (e: 'close'): void;
  (e: 'tokenGenerated', token: string, url: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// State
const isGenerating = ref(false);
const isCopying = ref(false);
const isCopied = ref(false);

/**
 * Computed share URL based on existing token
 * If calendar is already shared, constructs the full share URL
 * More Vue-idiomatic than watch for derived state
 */
const shareUrl = computed<string>(() => {
  if (props.existingShareToken) {
    return `${window.location.origin}/shared/${props.existingShareToken}`;
  }
  return '';
});

/**
 * Watch for modal opening
 * Reset copied state when modal opens
 */
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      isCopied.value = false;
    }
  }
);

/**
 * Handle modal close
 */
const handleClose = () => {
  emit('close');
};

/**
 * Start generating state (called by parent)
 */
const startGenerating = () => {
  isGenerating.value = true;
};

/**
 * Stop loading state after token generation
 * Called by parent after updating calendar data
 */
const stopGenerating = () => {
  isGenerating.value = false;
};

/**
 * Set error state (called by parent if generation fails)
 */
const setGenerationError = () => {
  isGenerating.value = false;
};

/**
 * Copy share URL to clipboard
 * Uses modern Clipboard API with fallback for older browsers
 */
const handleCopyToClipboard = async () => {
  if (!shareUrl.value) return;

  isCopying.value = true;

  try {
    // Modern Clipboard API (requires HTTPS or localhost)
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(shareUrl.value);
      isCopied.value = true;
      // Reset copied state after 3 seconds
      setTimeout(() => {
        isCopied.value = false;
      }, 3000);
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = shareUrl.value;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();

      const success = document.execCommand('copy');
      document.body.removeChild(textarea);

      if (success) {
        isCopied.value = true;
        setTimeout(() => {
          isCopied.value = false;
        }, 3000);
      } else {
        throw new Error('Copy command failed');
      }
    }
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    // Parent will show error toast
  } finally {
    isCopying.value = false;
  }
};

// Expose methods for parent component
defineExpose({
  startGenerating,
  stopGenerating,
  setGenerationError
});
</script>

<style scoped>
/* Modal Container */
.share-modal {
  --width: 90%;
  --max-width: 500px;
  --height: auto;
  --max-height: 80vh;
  --border-radius: 16px;
}

/* Content Container */
.share-modal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 0;
  min-height: 300px;
}

/* State Containers */
.not-shared-state,
.shared-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
  gap: 1rem;
}

/* Icons */
.share-icon,
.success-icon {
  font-size: 4rem;
  margin-bottom: 0.5rem;
}

.share-icon {
  color: var(--ion-color-primary);
}

/* Typography */
.share-modal-content h2 {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.description {
  font-size: clamp(0.9rem, 2vw, 1rem);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
  max-width: 400px;
}

/* URL Container */
.url-container {
  width: 100%;
  margin: 0.5rem 0;
}

.share-url-input {
  --background: var(--color-surface);
  --color: var(--color-text-primary);
  --padding-start: 12px;
  --padding-end: 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-family: 'Courier New', monospace;
}

/* Buttons - Touch-friendly (NFR: U2 - 44px minimum) */
.generate-button,
.copy-button {
  --min-height: 48px;
  margin-top: 0.5rem;
  font-weight: var(--font-weight-semibold);
}

.generate-button {
  max-width: 300px;
}

/* Loading State */
.loading-state {
  min-height: 200px;
  justify-content: center;
}

.loading-state ion-spinner {
  --color: var(--ion-color-primary);
  width: 3rem;
  height: 3rem;
}

.loading-state p {
  color: var(--color-text-secondary);
  font-size: 1rem;
}

/* Copy Success Message */
.copy-success-message {
  color: var(--ion-color-success);
  font-size: 0.875rem;
  font-weight: var(--font-weight-semibold);
  margin: 0.5rem 0 0 0;
}

/* Responsive - Mobile */
@media (max-width: 640px) {
  .share-modal {
    --width: 95%;
  }

  .share-modal-content {
    padding: 0.5rem 0;
  }

  .description {
    font-size: 0.875rem;
  }
}

/* Accessibility - Focus Indicators */
ion-button:focus-visible {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* Keyboard Navigation */
.share-url-input:focus-within {
  border-color: var(--ion-color-primary);
  box-shadow: 0 0 0 2px rgba(var(--ion-color-primary-rgb), 0.2);
}
</style>
