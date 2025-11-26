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
      <div v-else-if="calendar" class="calendar-view calendar-container" :class="themeClass">
        <!-- Calendar content wrapper -->
        <div class="calendar-content">
        <!-- Header -->
        <header class="calendar-header">
          <h1 class="calendar-title">{{ calendar.title }}</h1>

          <!-- Calendar Description (centered for viewer) -->
          <CalendarDescription
            :description="calendar.description"
            :centered="true"
            :theme="calendar.theme || 'christmas'"
          />

          <!-- Owner Controls - Only visible to calendar owner -->
          <div v-if="calendar.isOwner" class="owner-controls">
            <p class="owner-label">
              <ion-icon :icon="personCircleOutline" aria-hidden="true"></ion-icon>
              You are viewing as owner
            </p>

            <!-- Toggle between "See All" and "Viewer Mode" -->
            <div class="view-mode-toggle">
              <ion-button
                :color="showAllDoors ? 'primary' : 'medium'"
                fill="solid"
                size="default"
                @click="showAllDoors = true"
                class="mode-button"
                :class="{ 'active': showAllDoors }"
              >
                <ion-icon :icon="lockOpenOutline" slot="start" aria-hidden="true"></ion-icon>
                See All Doors
              </ion-button>

              <ion-button
                :color="!showAllDoors ? 'primary' : 'medium'"
                fill="solid"
                size="default"
                @click="showAllDoors = false"
                class="mode-button"
                :class="{ 'active': !showAllDoors }"
              >
                <ion-icon :icon="eyeOutline" slot="start" aria-hidden="true"></ion-icon>
                Viewer Mode
              </ion-button>
            </div>

            <p class="owner-info">
              <strong>{{ showAllDoors ? 'Showing all doors' : 'Showing viewer experience' }}</strong>
              {{ showAllDoors ? ' - You can see locked content' : ' - Only unlocked doors visible' }}
            </p>

            <!-- Re-close All Doors Button -->
            <ion-button
              color="warning"
              fill="outline"
              size="small"
              @click="handleResetDoors"
              class="reset-doors-button"
            >
              <ion-icon :icon="refreshOutline" slot="start" aria-hidden="true"></ion-icon>
              Re-close All Doors
            </ion-button>
          </div>
        </header>

        <!-- Door Grid -->
        <div class="door-grid" role="grid" aria-label="Calendar days grid">
          <DoorCard
            v-for="dayNumber in doorDisplayOrder"
            :key="`${dayNumber}-${showAllDoors}`"
            :day="getDayData(dayNumber)"
            :calendar-id="calendarId"
            :is-owner="calendar?.isOwner || false"
            :start-date="calendar?.startDate"
            :is-day-opened="isDayOpened"
            :theme="calendar?.theme || 'christmas'"
            @door-click="handleDoorClick"
            role="gridcell"
          />
        </div>
        </div> <!-- Close calendar-content wrapper -->
      </div> <!-- Close calendar-view -->
    </ion-content>

    <!-- Video Modal -->
    <VideoModal
      :is-open="videoModal.isOpen.value"
      :calendar-id="calendarId"
      :day-number="videoModal.selectedItem.value || 1"
      :require-auth="calendar?.isOwner || false"
      :theme="calendar?.theme || 'christmas'"
      @close="videoModal.close()"
      @video-ended="handleVideoEnded"
    />
  </ion-page>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { IonPage, IonContent, IonSpinner, IonIcon, IonButton } from '@ionic/vue';
import { alertCircleOutline, personCircleOutline, lockOpenOutline, eyeOutline, refreshOutline } from 'ionicons/icons';
import { useSharedCalendar, SharedCalendarDay } from '@/composables/useSharedCalendar';
import { useOpenedTracking } from '@/composables/useOpenedTracking';
import { useModal } from '@/composables/useModal';
import { getThemeConfig } from '@/utils/themeConfig';
import DoorCard from '@/components/sharing/DoorCard.vue';
import CalendarDescription from '@/components/CalendarDescription.vue';
import VideoModal from '@/components/VideoModal.vue';

const route = useRoute();
const { calendar, loading, error, fetchSharedCalendar, getDoorDisplayOrder } = useSharedCalendar();

// Get calendar ID from route
const calendarId = computed(() => route.params.id as string);

// Owner view mode toggle (frontend-only, doesn't affect database)
// When true: Owner sees all doors (backend allows access via owner permission check)
// When false: Owner sees what viewers see (respects lock dates)
const showAllDoors = ref(true); // Default to showing all for owners

// Initialize opened tracking with calendar ID
const { isDayOpened, markDayAsOpened, clearOpenedDays } = useOpenedTracking(calendarId.value);

// Video modal state management (day number)
const videoModal = useModal<number>();

// Computed: Door display order based on sequential or random
const doorDisplayOrder = computed(() => getDoorDisplayOrder());

// Computed: Theme class based on calendar theme
const themeClass = computed(() => {
  const themeId = calendar.value?.theme || 'christmas';
  return getThemeConfig(themeId).cssClass;
});

/**
 * Get day data for a specific day number
 * Respects owner's view mode toggle (showAllDoors)
 *
 * @param dayNumber - The day number to retrieve
 * @returns SharedCalendarDay object
 */
const getDayData = (dayNumber: number): SharedCalendarDay => {
  if (!calendar.value || !calendar.value.days) {
    // Return a default locked day if calendar not loaded or days array missing
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

  // If owner has "See All Doors" mode enabled, show as unlocked
  // (backend will allow access via owner permission check)
  if (calendar.value.isOwner && showAllDoors.value) {
    return {
      ...day,
      isUnlocked: true // Frontend shows as unlocked
    };
  }

  // Otherwise, return day with actual unlock status from backend
  return day;
};

/**
 * Handle door click event
 * Opens video modal for the clicked day
 *
 * @param dayNumber - The day number that was clicked
 */
const handleDoorClick = (dayNumber: number) => {
  // Mark day as opened in LocalStorage
  markDayAsOpened(dayNumber);

  // Open video modal with day number
  videoModal.open(dayNumber);
};

/**
 * Handle video playback ended
 * Called when video finishes playing (modal auto-closes after 2s)
 *
 * @param dayNumber - The day number whose video ended
 */
const handleVideoEnded = (dayNumber: number) => {
  console.log(`Video for day ${dayNumber} ended`);
  // Modal will auto-close after 2 seconds (handled in VideoModal)
};

/**
 * Handle re-closing all doors (owner only)
 * Clears the opened tracking from LocalStorage, allowing owners to reset the calendar state
 */
const handleResetDoors = () => {
  if (calendar.value?.isOwner) {
    clearOpenedDays();
    console.log('All doors re-closed - opened tracking cleared');
  }
};

// Watch for view mode changes and clear opened tracking
// This ensures owners see the true state when switching modes
watch(showAllDoors, () => {
  if (calendar.value?.isOwner) {
    clearOpenedDays();
    console.log('Cleared opened doors tracking due to view mode change');
  }
});

// Lifecycle: Fetch public calendar on mount
onMounted(async () => {
  const id = calendarId.value;
  if (id) {
    await fetchSharedCalendar(id);
  } else {
    error.value = 'Invalid calendar link';
  }
});

</script>

<style scoped>
/* Import all theme styles (doors, backgrounds, text, letterbox) */
@import '@/theme/themes/index.css';

/* Page Content */
.shared-calendar-content {
  --background: transparent;
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

/* Error State */
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

/* Calendar View - Full screen background container */
.calendar-view {
  min-height: 100vh;
  width: 100%;
}

/* Calendar Content - Centered content wrapper */
.calendar-content {
  max-width: 75rem; /* 1200px */
  margin: 0 auto;
  padding: var(--spacing-lg);
  position: relative;
  z-index: 10;
}

/* Header */
.calendar-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md);
}

/* Base calendar title - theme-specific colors defined in theme files */
.calendar-title {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--spacing-sm) 0;
  /* color and text styling defined per-theme */
}

.calendar-info {
  font-size: clamp(0.9rem, 2.5vw, 1rem);
  color: var(--color-text-secondary);
  margin: 0;
  text-align: center;
}

/* Door Grid */
.door-grid {
  display: grid;
  gap: clamp(0.75rem, 2vw, 1rem);
  width: 100%;
  padding-bottom: var(--spacing-xl);
}

/* Mobile: 2 columns */
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

/* Owner Controls - Only visible to calendar owners */
.owner-controls {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background-color: var(--ion-color-light-tint);
  border-radius: var(--border-radius-md, 0.5rem);
  border: 2px solid var(--ion-color-primary);
  text-align: center;
}

.owner-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs, 0.5rem);
  font-size: 0.95rem;
  font-weight: var(--font-weight-medium, 500);
  color: var(--ion-color-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.owner-label ion-icon {
  font-size: 1.5rem;
}

.owner-info {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin: var(--spacing-sm, 0.75rem) 0 0 0;
  text-align: center;
}

/* View Mode Toggle Buttons */
.view-mode-toggle {
  display: flex;
  gap: var(--spacing-sm, 0.75rem);
  justify-content: center;
  margin-top: var(--spacing-md, 1rem);
  flex-wrap: wrap;
}

.mode-button {
  min-height: 44px;
  min-width: 140px;
  transition: all 0.2s ease;
}

.mode-button.active {
  box-shadow: 0 2px 8px rgba(var(--ion-color-primary-rgb), 0.3);
}

/* Re-close All Doors Button */
.reset-doors-button {
  margin-top: var(--spacing-md, 1rem);
  min-height: 44px;
}

/* Responsive toggle buttons */
@media (max-width: 576px) {
  .mode-button {
    min-width: 120px;
    font-size: 0.9rem;
  }

  .view-mode-toggle {
    flex-direction: column;
    align-items: center;
  }

  .mode-button {
    width: 100%;
    max-width: 280px;
  }

  .reset-doors-button {
    width: 100%;
    max-width: 280px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
    transition: none;
  }
}
</style>
