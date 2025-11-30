<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-back-button
            color="light"
            default-href="/calendar"
            text="Calendars"
            aria-label="Back to calendar overview"
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
            <div class="title-row">
              <h1 class="calendar-title">
                {{ calendar.title }}
                <!-- Published/Unpublished Status Indicator (plain text, not clickable, inline with title) -->
                <span
                  class="status-text"
                  :class="{ 'status-text--published': isPublished }"
                  :aria-label="isPublished ? 'Calendar is published' : 'Calendar is unpublished'"
                >
                  <ion-icon
                    :icon="isPublished ? lockOpenOutline : lockClosedOutline"
                    :color="isPublished ? 'success' : 'medium'"
                    aria-hidden="true"
                  ></ion-icon>
                  {{ isPublished ? 'Published' : 'Unpublished' }}
                </span>
              </h1>
            </div>

            <!-- Info Chips - Always clickable to edit -->
            <div class="info-chips">
              <ion-chip
                color="primary"
                outline
                class="info-chip-clickable"
                @click="openEditModal()"
                :aria-label="'Edit calendar dates: ' + dateRangeFormatted"
              >
                <ion-icon :icon="calendarOutline" aria-hidden="true"></ion-icon>
                <ion-label>{{ dateRangeFormatted }}</ion-label>
              </ion-chip>

              <ion-chip
                color="secondary"
                outline
                class="info-chip-clickable"
                @click="openEditModal()"
                :aria-label="'Edit calendar duration: ' + calendar.duration + ' days'"
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

            <!-- Calendar Description (optional, clickable to edit, below chips) -->
            <CalendarDescription
              :description="calendar.description"
              :editable="true"
              @edit="openEditModal()"
            />

            <!-- Door Ordering Toggle - Always editable -->
            <DoorOrderToggle
              :door-order="calendar.doorOrder"
              :door-positions="calendar.doorPositions"
              :duration="calendar.duration"
              :is-locked="false"
              @update="handleDoorOrderUpdate"
            />

            <!-- Theme Selector - Always editable -->
            <ThemeSelector
              :theme="calendar.theme"
              :is-locked="false"
              @update="handleThemeUpdate"
            />

            <!-- Calendar Link Card - Always visible -->
            <ion-card class="calendar-link-card">
              <ion-card-content>
                <div class="link-header">
                  <ion-icon :icon="globeOutline" class="link-icon"></ion-icon>
                  <h3>Calendar Link</h3>

                  <!-- Publish/Unpublish Toggle Button -->
                  <ion-button
                    :color="isPublished ? 'danger' : 'success'"
                    fill="solid"
                    size="small"
                    class="publish-toggle-button"
                    @click="handlePublishToggle"
                    :aria-label="isPublished ? 'Click to unpublish calendar' : 'Click to publish calendar'"
                  >
                    {{ isPublished ? 'Unpublish' : 'Publish' }}
                  </ion-button>

                  <ion-button
                    @click="copyLinkToClipboard"
                    fill="solid"
                    color="primary"
                    class="copy-button"
                    :aria-label="isCopied ? 'Link copied!' : 'Copy link to clipboard'"
                  >
                    <ion-icon slot="icon-only" :icon="isCopied ? checkmarkOutline : copyOutline"></ion-icon>
                  </ion-button>
                </div>
                <a
                  :href="calendarLink"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="link-input clickable-link"
                  :aria-label="'Open calendar link in new tab: ' + calendarLink"
                >
                  {{ calendarLink }}
                </a>
              </ion-card-content>
            </ion-card>
          </div>

          <!-- Day Grid Component -->
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
  IonModal,
  IonCard,
  IonCardContent
} from '@ionic/vue';
import {
  alertCircleOutline,
  calendarOutline,
  timeOutline,
  videocamOutline,
  globeOutline,
  lockClosedOutline,
  lockOpenOutline,
  copyOutline,
  checkmarkOutline
} from 'ionicons/icons';
import CalendarDayGrid from '@/components/CalendarDayGrid.vue';
import DoorOrderToggle from '@/components/DoorOrderToggle.vue';
import ThemeSelector from '@/components/ThemeSelector.vue';
import CalendarForm from '@/components/CalendarForm.vue';
import CalendarDescription from '@/components/CalendarDescription.vue';
import { useCalendar } from '@/composables/useCalendar';
import { useModal } from '@/composables/useModal';
import { useToast } from '@/composables/useToast';
import type { Calendar, DoorOrder, CalendarCreateData } from '@/types/calendar';

// Router
const route = useRoute();

// Composables
const { getCalendar, updateCalendar, publishCalendar, unpublishCalendar } = useCalendar();
const { showSuccess, showError } = useToast();
const editModal = useModal();

// State
const calendarId = ref<string>(route.params.id as string);
const calendar = ref<Calendar | null>(null);
const isLoading = ref(true);
const loadError = ref<string>('');
const isSubmittingEdit = ref(false);
const isPublishing = ref(false);
const isCopied = ref(false);

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
 * Required for enabling publish functionality
 */
const isCalendarComplete = computed(() => {
  if (!calendar.value) return false;
  return calendar.value.videoCount === calendar.value.duration;
});

/**
 * Computed: Get the shareable calendar link
 * Format: https://domain.com/calendar/{id}
 */
const calendarLink = computed(() => {
  if (!calendar.value) return '';
  return `${window.location.origin}/calendar/${calendar.value.id}`;
});

/**
 * Computed: Check if calendar is published
 */
const isPublished = computed(() => {
  return calendar.value?.published || false;
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
 * Handle upload complete - update state locally without page reload
 */
const handleUploadComplete = (day: number) => {
  // Update video count locally (no need to reload entire calendar)
  // The CalendarDayGrid already updates its own state via polling
  if (calendar.value) {
    calendar.value.videoCount++;
  }
};

/**
 * Handle upload error
 */
const handleUploadError = async (day: number, error: string) => {
  console.error(`Upload error for day ${day}:`, error);

  await showError(`Failed to upload day ${day}: ${error}`);
};

/**
 * Handle video deleted - update state locally without page reload
 */
const handleVideoDeleted = (day: number) => {
  // Update video count locally (no need to reload entire calendar)
  // The CalendarDayGrid already shows success toast and updates its own state
  if (calendar.value && calendar.value.videoCount > 0) {
    calendar.value.videoCount--;
  }
};

/**
 * Handle publish/unpublish toggle
 * Toggles the calendar's published status
 */
const handlePublishToggle = async () => {
  if (!calendar.value) return;

  try {
    isPublishing.value = true;

    // Track what action we're taking before the API call
    const isCurrentlyPublished = isPublished.value;

    // Call appropriate API based on current state
    const result = isCurrentlyPublished
      ? await unpublishCalendar(calendarId.value)
      : await publishCalendar(calendarId.value);

    if (result.success) {
      // Update published status locally (no page reload needed)
      if (calendar.value) {
        calendar.value.published = !isCurrentlyPublished;
      }

      // Show success message
      const action = isCurrentlyPublished ? 'unpublished' : 'published';
      await showSuccess(`Calendar ${action} successfully!`);
    } else {
      await showError(result.error || 'Failed to update calendar status');
    }
  } catch (error: any) {
    console.error('Error toggling publish status:', error);
    await showError('An unexpected error occurred');
  } finally {
    isPublishing.value = false;
  }
};

/**
 * Copy calendar link to clipboard
 */
const copyLinkToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(calendarLink.value);
    isCopied.value = true;

    // Show success feedback
    await showSuccess('Link copied to clipboard!');

    // Reset copied state after 2 seconds
    setTimeout(() => {
      isCopied.value = false;
    }, 2000);
  } catch (error) {
    console.error('Failed to copy link:', error);
    await showError('Failed to copy link to clipboard');
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
 * Handle door order update.
 * @param data Object containing doorOrder and doorPositions
 */
const handleDoorOrderUpdate = async (data: { doorOrder: DoorOrder; doorPositions: number[] | null }) => {
  if (!calendar.value) return;

  try {
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

/**
 * Handle theme update.
 * @param theme Theme identifier (e.g., "christmas")
 */
const handleThemeUpdate = async (theme: string) => {
  if (!calendar.value) return;

  try {
    const result = await updateCalendar(calendarId.value, {
      theme: theme
    });

    if (result.success && result.data) {
      // Update local calendar state with new value
      calendar.value.theme = result.data.theme;

      // Show success feedback
      await showSuccess(`Theme updated to ${theme}`);
    } else {
      // Show error feedback
      await showError(result.error || 'Failed to update theme');
      console.error('Theme update failed:', result.error);
    }
  } catch (error) {
    console.error('Failed to update theme:', error);
    await showError('An unexpected error occurred while updating theme');
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

/* Title Row */
.title-row {
  margin-bottom: var(--spacing-md);
}

.calendar-title {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

/* Status Text inline with Title (plain text, not clickable) */
.status-text {
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  color: var(--ion-color-medium);
  font-weight: var(--font-weight-medium);
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  margin-left: 0.25rem;
}

.status-text--published {
  color: var(--ion-color-success);
}

.status-text ion-icon {
  font-size: 1rem;
  display: inline-block;
  vertical-align: middle;
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
  margin: 0; /* Remove default ion-chip margins */
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
  margin: 0; /* Remove default ion-chip margins */
}

/* Edit modal content */
.modal-content {
  --padding-top: var(--spacing-md);
  --padding-bottom: var(--spacing-md);
  --padding-start: var(--spacing-md);
  --padding-end: var(--spacing-md);
}

/* Publish Chip - Clickable chip for publish/unpublish */
.publish-chip {
  cursor: pointer;
  transition: all 0.2s ease;
}

.publish-chip--clickable {
  cursor: pointer !important;
}

.publish-chip--clickable:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.publish-chip--clickable:active {
  transform: translateY(0);
}

/* Ready state animation for publish chip */
.publish-chip--ready {
  animation: chip-pulse 2s ease-in-out infinite;
}

@keyframes chip-pulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(var(--ion-color-success-rgb), 0.3);
  }
  50% {
    box-shadow: 0 4px 12px rgba(var(--ion-color-success-rgb), 0.5);
  }
}

/* Remove animation on mobile to conserve battery */
@media (prefers-reduced-motion: reduce) {
  .publish-chip--ready {
    animation: none;
  }
}

/* Disabled publish chip */
.publish-chip[disabled] {
  opacity: 0.5;
  cursor: not-allowed !important;
  pointer-events: none;
}

/* Calendar Link Card */
.calendar-link-card {
  margin-top: var(--spacing-md);
  box-shadow: var(--shadow-md);
  border-radius: var(--radius-md);
}

.link-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.link-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.link-icon {
  font-size: 1.5rem;
  color: var(--ion-color-primary);
}

/* Publish Toggle Button */
.publish-toggle-button {
  margin-left: var(--spacing-sm);
  --padding-start: 1rem;
  --padding-end: 1rem;
  min-width: 100px;
  text-transform: none;
}

.link-input {
  display: block;
  width: 100%;
  font-size: 0.9rem;
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-decoration: none;
}

.link-input:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* Clickable link specific styles */
.clickable-link {
  color: var(--ion-color-primary);
  cursor: pointer;
  transition: color var(--transition-base);
}

.clickable-link:hover {
  color: var(--ion-color-primary-shade);
  text-decoration: underline;
}

.clickable-link:active {
  opacity: 0.7;
}

.copy-button {
  --padding-start: 1rem;
  --padding-end: 1rem;
  min-width: 44px;
  min-height: 44px;
  margin-left: auto;
}

.copy-button ion-icon {
  font-size: 1.3rem;
}

/* Responsive adjustments for link card */
@media (max-width: 576px) {
  .link-input {
    font-size: 0.8rem;
  }

  .link-header h3 {
    font-size: 1rem;
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
