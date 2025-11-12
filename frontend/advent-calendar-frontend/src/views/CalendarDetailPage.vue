<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-back-button
            color="light"
            default-href="/dashboard"
            text="Dashboard"
            aria-label="Back to dashboard"
          ></ion-back-button>
        </ion-buttons>
        <ion-title v-if="calendar">{{ calendar.title }}</ion-title>
        <ion-title v-else>Calendar Details</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div class="calendar-detail-container">
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-section">
          <ion-spinner name="crescent" color="primary"></ion-spinner>
          <p>Loading calendar...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="loadError" class="error-section">
          <ion-icon :icon="alertCircleOutline" class="error-icon"></ion-icon>
          <p class="error-message">{{ loadError }}</p>
          <ion-button @click="loadCalendarData" fill="outline" color="primary">
            Try Again
          </ion-button>
        </div>

        <!-- Calendar Content -->
        <div v-else-if="calendar" class="calendar-content">
          <!-- Calendar Info -->
          <div class="calendar-info">
            <h2>{{ calendar.title }}</h2>
            <p class="date-range">{{ calendar.dateRange }}</p>
            <p class="duration">{{ calendar.duration }} days</p>
            <p class="video-count">
              Videos: {{ calendar.videoCount }} / {{ calendar.duration }}
            </p>

            <!-- Share Calendar Button (Issue #78) -->
            <ion-button
              expand="block"
              :color="isCalendarComplete ? 'primary' : 'medium'"
              @click="handleShareButtonClick"
              class="share-button"
              :class="{ 'share-button--disabled': !isCalendarComplete }"
              :aria-label="isCalendarComplete ? 'Share calendar' : 'Complete all videos to enable sharing'"
            >
              <ion-icon slot="start" :icon="shareSocialOutline"></ion-icon>
              Share Calendar
            </ion-button>
          </div>

          <!-- Day Grid Component (Issue #57, #58, #59) -->
          <div class="day-grid-section">
            <h3>Upload Videos</h3>
            <CalendarDayGrid
              :calendar-id="calendarId"
              :duration="calendar.duration"
              @uploadComplete="handleUploadComplete"
              @uploadError="handleUploadError"
              @videoDeleted="handleVideoDeleted"
            />
          </div>
        </div>
      </div>
    </ion-content>

    <!-- Share Modal (Issue #78) -->
    <ShareModal
      v-if="calendar"
      ref="shareModalRef"
      :is-open="shareModal.isOpen.value"
      :calendar-id="calendarId"
      :existing-share-token="calendar.shareToken || null"
      @close="shareModal.close()"
      @token-generated="handleTokenGeneration"
    />
  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonButtons,
  IonBackButton,
  IonIcon,
  IonSpinner
} from '@ionic/vue';
import { alertCircleOutline, shareSocialOutline } from 'ionicons/icons';
import CalendarDayGrid from '@/components/CalendarDayGrid.vue';
import ShareModal from '@/components/ShareModal.vue';
import { useCalendar } from '@/composables/useCalendar';
import { useModal } from '@/composables/useModal';
import { useToast } from '@/composables/useToast';
import type { Calendar } from '@/types/calendar';

// Router
const route = useRoute();

// Composables
const { getCalendar, generateShareToken } = useCalendar();
const { showSuccess, showError } = useToast();
const shareModal = useModal();

// State
const calendarId = ref<string>(route.params.id as string);
const calendar = ref<Calendar | null>(null);
const isLoading = ref(true);
const loadError = ref<string>('');

// Share Modal Reference (Issue #78)
const shareModalRef = ref<InstanceType<typeof ShareModal> | null>(null);

/**
 * Computed: Check if calendar is complete (all videos uploaded)
 * Required for enabling share functionality
 */
const isCalendarComplete = computed(() => {
  if (!calendar.value) return false;
  return calendar.value.videoCount === calendar.value.duration;
});

/**
 * Load calendar data
 */
const loadCalendarData = async () => {
  try {
    isLoading.value = true;
    loadError.value = '';

    const result = await getCalendar(calendarId.value);

    if (result.success && result.data) {
      calendar.value = result.data;
    } else {
      loadError.value = result.error || 'Failed to load calendar';
    }
  } catch (error) {
    console.error('Failed to load calendar:', error);
    loadError.value = 'An unexpected error occurred';
  } finally {
    isLoading.value = false;
  }
};

/**
 * Handle upload complete
 */
const handleUploadComplete = async (day: number) => {
  console.log(`Upload complete for day ${day}`);

  await showSuccess(`Day ${day} video uploaded successfully!`);

  // Reload calendar to update video count
  await loadCalendarData();
};

/**
 * Handle upload error
 */
const handleUploadError = async (day: number, error: string) => {
  console.error(`Upload error for day ${day}:`, error);

  await showError(`Failed to upload day ${day}: ${error}`);
};

/**
 * Handle video deleted
 */
const handleVideoDeleted = async (day: number) => {
  console.log(`Video deleted for day ${day}`);

  await showSuccess(`Day ${day} video deleted`);

  // Reload calendar to update video count
  await loadCalendarData();
};

/**
 * Handle share button click (Issue #78)
 * Checks if calendar is complete before opening modal
 * Auto-generates share token on first share for streamlined UX
 */
const handleShareButtonClick = async () => {
  if (!isCalendarComplete.value) {
    // Show informative toast explaining requirement
    const missingCount = calendar.value!.duration - calendar.value!.videoCount;
    showError(
      `Upload all videos first. ${missingCount} video${missingCount !== 1 ? 's' : ''} remaining.`
    );
    return;
  }

  // Open modal immediately
  shareModal.open();

  // Auto-generate token if not already shared
  if (!calendar.value?.shareToken) {
    await handleTokenGeneration();
  }
};

/**
 * Handle share token generation (Issue #78)
 * Auto-called when opening share modal for first time
 */
const handleTokenGeneration = async () => {
  try {
    console.log('Generating share token for calendar:', calendarId.value);

    // Trigger loading state in modal
    if (shareModalRef.value) {
      shareModalRef.value.startGenerating();
    }

    const result = await generateShareToken(calendarId.value);

    if (result.success && result.data) {
      // The generateShareToken composable updates currentCalendar.shareToken
      // This automatically updates the existingShareToken prop in ShareModal
      // The computed shareUrl in ShareModal will automatically recalculate

      // Reload calendar data to get the updated shareToken
      await loadCalendarData();

      // Stop loading state
      if (shareModalRef.value) {
        shareModalRef.value.stopGenerating();
      }

      // Show success toast
      await showSuccess('Share link generated successfully!');

      console.log('Share token generated:', result.data.shareToken);
      console.log('Share URL:', result.data.shareUrl);
    } else {
      // Show error toast
      await showError(result.error || 'Failed to generate share link');

      // Notify modal of error
      if (shareModalRef.value) {
        shareModalRef.value.setGenerationError();
      }
    }
  } catch (error: any) {
    console.error('Error generating share token:', error);
    await showError('An unexpected error occurred');

    // Notify modal of error
    if (shareModalRef.value) {
      shareModalRef.value.setGenerationError();
    }
  }
};

// Lifecycle
onMounted(async () => {
  await loadCalendarData();
});
</script>

<style scoped>
/* Back Button Visibility - Ensure it's visible on both web and mobile */
ion-back-button {
  --color: var(--ion-color-light);
  --icon-font-size: 1.5rem;
  --min-width: 44px;
  --min-height: 44px;
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
}

/* Ensure back button is touch-friendly on mobile (NFR: U2) */
ion-back-button::part(native) {
  padding: 0.5rem;
  min-width: 44px;
  min-height: 44px;
}

/* Make back button text visible on web */
@media (min-width: 768px) {
  ion-back-button {
    --icon-margin-end: 0.5rem;
  }
}

/* Hide text on mobile, keep icon */
@media (max-width: 767px) {
  ion-back-button {
    --icon-margin-end: 0;
  }
}

.calendar-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: clamp(1rem, 3vw, 2rem);
}

/* Loading State */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  min-height: 300px;
}

.loading-section ion-spinner {
  --color: var(--ion-color-primary);
  width: 3rem;
  height: 3rem;
}

/* Error State */
.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  min-height: 300px;
  padding: 2rem;
  background: rgba(var(--ion-color-danger-rgb), 0.05);
  border: 1px solid rgba(var(--ion-color-danger-rgb), 0.2);
  border-radius: var(--radius-lg);
}

.error-icon {
  font-size: 3rem;
  color: var(--ion-color-danger);
}

.error-message {
  font-size: 1rem;
  color: var(--ion-color-danger);
  text-align: center;
  margin: 0;
}

/* Calendar Info */
.calendar-info {
  margin-bottom: clamp(1.5rem, 4vw, 2rem);
  padding: clamp(1rem, 3vw, 1.5rem);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.calendar-info h2 {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 clamp(0.5rem, 1.5vw, 0.75rem) 0;
}

.date-range,
.duration,
.video-count {
  font-size: clamp(0.9rem, 2vw, 1rem);
  color: var(--color-text-secondary);
  margin: clamp(0.25rem, 1vw, 0.5rem) 0;
}

.video-count {
  font-weight: var(--font-weight-semibold);
  color: var(--ion-color-primary);
}

/* Share Button (Issue #78) - Touch-friendly (NFR: U2) */
.share-button {
  --min-height: 48px;
  margin-top: clamp(1rem, 2vw, 1.5rem);
  font-weight: var(--font-weight-semibold);
}

.share-button ion-icon {
  font-size: 1.25rem;
}

/* Share button - dynamic color based on completion state */
.share-button {
  transition: all 0.3s ease;
}

/* Visual disabled state - less prominent when incomplete */
.share-button--disabled {
  opacity: 0.7;
  cursor: pointer; /* Still clickable to show toast */
}

.share-button--disabled ion-icon {
  opacity: 0.8;
}

/* Day Grid Section */
.day-grid-section {
  margin-top: clamp(1.5rem, 4vw, 2rem);
}

.day-grid-section h3 {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: clamp(1rem, 2vw, 1.5rem);
}

/* Responsive */
@media (max-width: 768px) {
  .calendar-detail-container {
    padding: 1rem;
  }
}
</style>
