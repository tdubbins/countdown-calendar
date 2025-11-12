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
          <div
            v-for="dayNumber in doorDisplayOrder"
            :key="dayNumber"
            class="door-card"
            role="gridcell"
            :aria-label="`Day ${dayNumber}`"
          >
            <div class="door-number">{{ dayNumber }}</div>
            <div class="door-placeholder">
              <ion-icon :icon="giftOutline" class="door-icon" aria-hidden="true"></ion-icon>
            </div>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { IonPage, IonContent, IonSpinner, IonIcon } from '@ionic/vue';
import { alertCircleOutline, giftOutline } from 'ionicons/icons';
import { useSharedCalendar } from '@/composables/useSharedCalendar';

const route = useRoute();
const { calendar, loading, error, fetchSharedCalendar, getDoorDisplayOrder } = useSharedCalendar();

// Computed: Door display order based on sequential or random
const doorDisplayOrder = computed(() => getDoorDisplayOrder());

// Lifecycle: Fetch shared calendar on mount
onMounted(async () => {
  const token = route.params.token as string;
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

/* Door Card - Basic placeholder for Issue #79 */
.door-card {
  position: relative;
  aspect-ratio: 1;
  min-height: 9rem;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
  transition: transform var(--transition-base);

  /* NFR [U2]: Touch-friendly minimum size */
  min-width: 44px;
  min-height: 44px;
}

/* Door Number */
.door-number {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.9);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  z-index: 2;
}

@media (prefers-color-scheme: dark) {
  .door-number {
    background: rgba(0, 0, 0, 0.7);
  }
}

/* Door Placeholder Content */
.door-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.door-icon {
  font-size: clamp(2rem, 6vw, 3rem);
  color: var(--ion-color-medium);
  opacity: 0.4;
}

/* Accessibility - NFR [U5]: Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .door-card,
  .loading-spinner {
    animation: none;
    transition: none;
  }
}

/* High contrast mode - NFR [U5] */
@media (prefers-contrast: high) {
  .door-card {
    border-width: 3px;
  }

  .door-number {
    font-weight: var(--font-weight-black);
  }
}

/* Container queries for very small screens */
@container (max-width: 20rem) {
  .door-number {
    font-size: 0.75rem;
    padding: 0.15rem 0.35rem;
  }

  .door-icon {
    font-size: 1.5rem;
  }
}
</style>
