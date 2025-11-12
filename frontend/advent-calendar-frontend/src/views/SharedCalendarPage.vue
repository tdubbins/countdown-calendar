<template>
  <ion-page>
    <ion-content :fullscreen="true" class="shared-calendar-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <ion-spinner name="crescent" class="loading-spinner"></ion-spinner>
        <p class="loading-text">Loading calendar...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-container">
        <ion-icon :icon="alertCircleOutline" class="error-icon" aria-hidden="true"></ion-icon>
        <h1 class="error-title">Calendar Not Found</h1>
        <p class="error-message">{{ error }}</p>
      </div>

      <!-- Calendar Loaded Successfully -->
      <div v-else-if="calendar" class="calendar-container">
        <!-- Header -->
        <header class="calendar-header">
          <h1 class="calendar-title">{{ calendar.title }}</h1>
          <p class="calendar-info">
            {{ calendar.duration }} {{ calendar.duration === 1 ? 'day' : 'days' }}
          </p>
          <p v-if="calendar.description" class="calendar-description">
            {{ calendar.description }}
          </p>
        </header>

        <!-- Door Grid -->
        <div class="door-grid" role="grid" aria-label="Calendar days grid">
          <DoorCard
            v-for="dayNumber in doorDisplayOrder"
            :key="dayNumber"
            :day="getDayData(dayNumber)"
            :start-date="calendar?.startDate"
            :is-day-opened="isDayOpened"
            @door-click="handleDoorClick"
            role="gridcell"
          />
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { IonPage, IonContent, IonSpinner, IonIcon } from '@ionic/vue';
import { alertCircleOutline } from 'ionicons/icons';
import { useSharedCalendar, SharedCalendarDay } from '@/composables/useSharedCalendar';
import { useOpenedTracking } from '@/composables/useOpenedTracking';
import DoorCard from '@/components/sharing/DoorCard.vue';

const route = useRoute();
const { calendar, loading, error, fetchSharedCalendar, getDoorDisplayOrder } = useSharedCalendar();

// Get share token from route
const shareToken = computed(() => route.params.token as string);

// Initialize opened tracking with share token
const { isDayOpened, markDayAsOpened } = useOpenedTracking(shareToken.value);

// Computed: Door display order based on sequential or random
const doorDisplayOrder = computed(() => getDoorDisplayOrder());

/**
 * Get day data for a specific day number
 * @param dayNumber - The day number to retrieve
 * @returns SharedCalendarDay object
 */
const getDayData = (dayNumber: number): SharedCalendarDay => {
  if (!calendar.value) {
    // Return a default locked day if calendar not loaded
    return {
      dayNumber: dayNumber,
      isUnlocked: false
    };
  }

  // Find the day in the calendar's days array
  const day = calendar.value.days.find(d => d.dayNumber === dayNumber);

  if (!day) {
    // If day not found, return a default locked day
    return {
      dayNumber: dayNumber,
      isUnlocked: false
    };
  }

  return day;
};

/**
 * Handle door click event
 * @param dayNumber - The day number that was clicked
 */
const handleDoorClick = (dayNumber: number) => {
  // Mark day as opened in LocalStorage
  markDayAsOpened(dayNumber);

  // TODO (Issue #85): Open video modal with day's video
  console.log(`Door ${dayNumber} clicked - video modal will be implemented in Issue #85`);
};

// Lifecycle: Fetch shared calendar on mount
onMounted(async () => {
  const token = shareToken.value;
  if (token) {
    await fetchSharedCalendar(token);
  } else {
    error.value = 'Invalid share link';
  }
});

</script>

<style scoped>
/* Page Content */
.shared-calendar-content {
  --background: var(--ion-color-light);
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--spacing-lg);
}

.loading-spinner {
  --color: var(--ion-color-primary);
  width: 3rem;
  height: 3rem;
  margin-bottom: var(--spacing-md);
}

.loading-text {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Error State - NFR [U5]: Accessible error messaging */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--spacing-xl);
  text-align: center;
}

.error-icon {
  font-size: 4rem;
  color: var(--ion-color-danger);
  margin-bottom: var(--spacing-md);
}

.error-title {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.error-message {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 32rem;
}

/* Calendar Container */
.calendar-container {
  max-width: 75rem; /* 1200px */
  margin: 0 auto;
  padding: var(--spacing-lg);
  min-height: 100vh;
}

/* Header */
.calendar-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md);
}

.calendar-title {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.calendar-description {
  font-size: clamp(0.95rem, 2.5vw, 1.1rem);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-md) 0;
  max-width: 40rem;
  line-height: 1.5;
  text-align: center;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.calendar-info {
  font-size: clamp(0.9rem, 2.5vw, 1rem);
  color: var(--color-text-secondary);
  margin: 0;
  text-align: center;
}

/* Door Grid - NFR [U1]: Responsive 320px+ */
.door-grid {
  display: grid;
  gap: clamp(0.75rem, 2vw, 1rem);
  width: 100%;
  padding-bottom: var(--spacing-xl);
}

/* Mobile: 2 columns (320px+) - NFR [U1] */
@media (max-width: 640px) {
  .door-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
}

/* Tablet: 3 columns (641-1024px) */
@media (min-width: 641px) and (max-width: 1024px) {
  .door-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Desktop: 4 columns (1025px+) */
@media (min-width: 1025px) {
  .door-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Door cards are now handled by DoorCard.vue component */

/* Accessibility - NFR [U5]: Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
    transition: none;
  }
}
</style>
