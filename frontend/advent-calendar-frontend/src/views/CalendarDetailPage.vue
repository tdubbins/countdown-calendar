<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-back-button
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
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
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
import { alertCircleOutline } from 'ionicons/icons';
import CalendarDayGrid from '@/components/CalendarDayGrid.vue';
import { useCalendar } from '@/composables/useCalendar';
import { useToast } from '@/composables/useToast';
import type { Calendar } from '@/types/calendar';

// Router
const route = useRoute();

// Composables
const { getCalendar } = useCalendar();
const { showSuccess, showError } = useToast();

// State
const calendarId = ref<string>(route.params.id as string);
const calendar = ref<Calendar | null>(null);
const isLoading = ref(true);
const loadError = ref<string>('');

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

// Lifecycle
onMounted(async () => {
  await loadCalendarData();
});
</script>

<style scoped>
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
