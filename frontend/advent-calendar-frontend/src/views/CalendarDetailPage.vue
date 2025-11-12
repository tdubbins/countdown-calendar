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
          <!-- Calendar Info Header -->
          <div class="calendar-header-card">
            <h1 class="calendar-title">{{ calendar.title }}</h1>

            <!-- Info Chips - Clickable to edit (before sharing only) -->
            <div class="info-chips">
              <ion-chip
                color="primary"
                outline
                :class="calendar.shareToken ? 'info-chip-readonly' : 'info-chip-clickable'"
                @click="!calendar.shareToken && openEditModal()"
                :aria-label="calendar.shareToken ? 'Calendar dates: ' + dateRangeFormatted : 'Edit calendar dates: ' + dateRangeFormatted"
              >
                <ion-icon :icon="calendarOutline" aria-hidden="true"></ion-icon>
                <ion-label>{{ dateRangeFormatted }}</ion-label>
              </ion-chip>

              <ion-chip
                color="secondary"
                outline
                :class="calendar.shareToken ? 'info-chip-readonly' : 'info-chip-clickable'"
                @click="!calendar.shareToken && openEditModal()"
                :aria-label="calendar.shareToken ? 'Calendar duration: ' + calendar.duration + ' days' : 'Edit calendar duration: ' + calendar.duration + ' days'"
              >
                <ion-icon :icon="timeOutline" aria-hidden="true"></ion-icon>
                <ion-label>{{ calendar.duration }} {{ calendar.duration === 1 ? 'day' : 'days' }}</ion-label>
              </ion-chip>

              <ion-chip
                :color="isCalendarComplete ? 'success' : 'medium'"
                outline
                class="info-chip-readonly"
              >
                <ion-icon :icon="videocamOutline" aria-hidden="true"></ion-icon>
                <ion-label>{{ calendar.videoCount }}/{{ calendar.duration }}</ion-label>
              </ion-chip>
            </div>

            <!-- Door Ordering Toggle (Issue #81) -->
            <DoorOrderToggle
              :door-order="calendar.doorOrder"
              :door-positions="calendar.doorPositions"
              :duration="calendar.duration"
              :is-locked="!!calendar.shareToken"
              @update="handleDoorOrderUpdate"
            />

            <!-- Share Button - Using ActionButton component -->
            <ActionButton
              expand="block"
              :disabled="!isCalendarComplete"
              @click="handleShareButtonClick"
              :class="{ 'share-button--ready': isCalendarComplete }"
              :aria-label="isCalendarComplete ? 'Share calendar' : 'Complete all videos to enable sharing'"
              :fill="isCalendarComplete ? 'solid' : 'outline'"
              :color="isCalendarComplete ? 'success' : 'medium'"
              :icon="shareSocialOutline"
              icon-slot="start"
            >
              {{ isCalendarComplete ? 'Share Calendar' : 'Upload all videos to share' }}
            </ActionButton>
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

    <!-- Edit Calendar Modal - Same pattern as Dashboard -->
    <ion-modal :is-open="editModal.isOpen.value" @didDismiss="editModal.close()">
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>Edit Calendar</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="editModal.close()" color="light">
              <strong>Close</strong>
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="modal-content">
        <CalendarForm
          v-if="calendar"
          :calendar="calendar"
          :is-submitting="isSubmittingEdit"
          @submit="handleEditSubmit"
          @cancel="editModal.close()"
        />
      </ion-content>
    </ion-modal>
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
  IonSpinner,
  IonChip,
  IonLabel,
  IonModal
} from '@ionic/vue';
import { alertCircleOutline, shareSocialOutline, calendarOutline, timeOutline, videocamOutline, closeOutline } from 'ionicons/icons';
import CalendarDayGrid from '@/components/CalendarDayGrid.vue';
import ShareModal from '@/components/ShareModal.vue';
import DoorOrderToggle from '@/components/DoorOrderToggle.vue';
import ActionButton from '@/components/ActionButton.vue';
import CalendarForm from '@/components/CalendarForm.vue';
import { useCalendar } from '@/composables/useCalendar';
import { useModal } from '@/composables/useModal';
import { useToast } from '@/composables/useToast';
import type { Calendar, DoorOrder, CalendarCreateData } from '@/types/calendar';

// Router
const route = useRoute();

// Composables
const { getCalendar, updateCalendar, generateShareToken } = useCalendar();
const { showSuccess, showError } = useToast();
const shareModal = useModal();
const editModal = useModal();

// State
const calendarId = ref<string>(route.params.id as string);
const calendar = ref<Calendar | null>(null);
const isLoading = ref(true);
const loadError = ref<string>('');
const isSubmittingEdit = ref(false);

// Share Modal Reference (Issue #78)
const shareModalRef = ref<InstanceType<typeof ShareModal> | null>(null);

/**
 * Format date to European format (DD.MM.YYYY)
 * @param dateString ISO date string (YYYY-MM-DD)
 * @returns Formatted date string
 */
const formatEuropeanDate = (dateString: string): string => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
};

/**
 * Computed: Format date range with European format
 * Uses backend-provided startDate and endDate, formats to DD.MM.YYYY - DD.MM.YYYY
 * @returns Formatted date range string
 */
const dateRangeFormatted = computed(() => {
  if (!calendar.value) return '';
  const startFormatted = formatEuropeanDate(calendar.value.startDate);
  const endFormatted = formatEuropeanDate(calendar.value.endDate);
  return `${startFormatted} - ${endFormatted}`;
});

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
  if (!isCalendarComplete.value || !calendar.value) {
    // Show informative toast explaining requirement
    if (calendar.value) {
      const missingCount = calendar.value.duration - calendar.value.videoCount;
      showError(
        `Upload all videos first. ${missingCount} video${missingCount !== 1 ? 's' : ''} remaining.`
      );
    }
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

/**
 * Open edit calendar modal
 */
const openEditModal = () => {
  editModal.open();
};

/**
 * Handle edit form submission
 * Same pattern as Dashboard
 */
const handleEditSubmit = async (data: CalendarCreateData) => {
  try {
    isSubmittingEdit.value = true;

    const result = await updateCalendar(calendarId.value, data);

    if (result.success) {
      // Show success toast
      await showSuccess('Calendar updated successfully!');

      // Close modal and reload calendar data
      editModal.close();
      await loadCalendarData();
    } else {
      // Show error toast
      await showError(result.error || 'Failed to update calendar');
    }
  } catch (error) {
    console.error('Failed to update calendar:', error);
    await showError('An unexpected error occurred');
  } finally {
    isSubmittingEdit.value = false;
  }
};

/**
 * Handle door order update (Issue #81)
 * Called when user changes door ordering settings via DoorOrderToggle component
 * Updates calendar's doorOrder and doorPositions fields
 *
 * @param data Object containing doorOrder and doorPositions
 */
const handleDoorOrderUpdate = async (data: { doorOrder: DoorOrder; doorPositions: number[] | null }) => {
  if (!calendar.value) return;

  try {
    console.log('Updating door order:', data);

    // Call API to update calendar with new door ordering
    const result = await updateCalendar(calendarId.value, {
      doorOrder: data.doorOrder,
      doorPositions: data.doorPositions
    });

    if (result.success && result.data) {
      // Update local calendar state with new values
      calendar.value.doorOrder = result.data.doorOrder;
      calendar.value.doorPositions = result.data.doorPositions;

      // Show success feedback
      await showSuccess(
        data.doorOrder === 'sequential'
          ? 'Door ordering set to sequential'
          : 'Door ordering shuffled successfully'
      );

      console.log('Door order updated successfully:', result.data);
    } else {
      // Show error feedback
      await showError(result.error || 'Failed to update door ordering');
      console.error('Door order update failed:', result.error);
    }
  } catch (error) {
    console.error('Failed to update door ordering:', error);
    await showError('An unexpected error occurred while updating door ordering');
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
/* Calendar Header Card - Minimal Design */
.calendar-header-card {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
}

.calendar-title {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

/* Info Chips - Horizontal Layout */
.info-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

/* Clickable info chips - date and duration */
.info-chip-clickable {
  cursor: pointer !important;
  transition: all 0.2s ease;
}

.info-chip-clickable:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.info-chip-clickable:active {
  transform: translateY(0);
}

/* Read-only chip - video count (non-interactive) */
.info-chip-readonly {
  cursor: default !important;
  pointer-events: none !important;
}

/* Edit modal content */
.modal-content {
  --padding-top: var(--spacing-md);
  --padding-bottom: var(--spacing-md);
  --padding-start: var(--spacing-md);
  --padding-end: var(--spacing-md);
}

/* Share Button - Extends ActionButton with ready state animation */
.share-button--ready {
  animation: pulse-glow 2s ease-in-out infinite;
  margin-top: var(--spacing-md);
}

/* Pulse glow animation for ready state */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(var(--ion-color-success-rgb), 0.3);
  }
  50% {
    box-shadow: 0 6px 20px rgba(var(--ion-color-success-rgb), 0.5);
  }
}

/* Remove animation on mobile to conserve battery */
@media (prefers-reduced-motion: reduce) {
  .share-button--ready {
    animation: none;
  }
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
