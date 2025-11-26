<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Countdown Calendar</ion-title>
        <ion-buttons slot="end">
          <!-- Desktop: New button in header -->
          <ActionButton
            v-if="!isMobile()"
            @click="goToCreateCalendar"
            fill="solid"
            color="light"
            variant="secondary"
            size="small"
            :icon="add"
            icon-slot="start"
            aria-label="Create new calendar"
          >
            New
          </ActionButton>

          <!-- Desktop only: Profile and Help (mobile uses tab bar) -->
          <ion-button
            v-if="!isMobile()"
            @click="goToProfile"
            fill="clear"
            color="light"
            aria-label="View profile"
          >
            <ion-icon slot="icon-only" :icon="personCircle"></ion-icon>
          </ion-button>

          <ion-button
            v-if="!isMobile()"
            @click="goToHelp"
            fill="clear"
            color="light"
            aria-label="Help and support"
          >
            <ion-icon slot="icon-only" :icon="helpCircle"></ion-icon>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>
    
    <ion-content :fullscreen="true" class="dashboard-content">
      <!-- Pull-to-Refresh (Mobile UX Enhancement) -->
      <ion-refresher slot="fixed" @ionRefresh="handleRefresh">
        <ion-refresher-content
          :pulling-icon="chevronDownCircleOutline"
          pulling-text="Pull to refresh calendars"
          refreshing-spinner="circles"
          refreshing-text="Refreshing..."
        ></ion-refresher-content>
      </ion-refresher>

      <div class="dashboard-container">

        <!-- Loading State with Skeleton -->
        <div v-if="isLoading" class="loading-section">
          <h2><ion-skeleton-text animated style="width: 30%; height: 32px;"></ion-skeleton-text></h2>
          <div class="calendars-grid">
            <div v-for="n in 3" :key="n" class="skeleton-card">
              <ion-skeleton-text animated style="width: 100%; height: 200px; border-radius: 12px;"></ion-skeleton-text>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="loadError" class="error-section">
          <div class="error-content">
            <p class="error-message">{{ loadError }}</p>
            <ActionButton 
              @click="loadUserCalendars"
              fill="outline"
              color="primary"
              variant="secondary"
            >
              Try Again
            </ActionButton>
          </div>
        </div>

        <!-- Calendar Content -->
        <div v-else-if="hasCalendars" class="calendars-section">
          <h2>Your Calendars ({{ calendars.length }})</h2>

          <!-- Calendar Grid - Display All Calendars -->
          <div class="calendars-grid">
            <CalendarCard
              v-for="calendar in calendars"
              :key="calendar.id"
              :calendar="calendar"
              @click="openCalendar"
            />
          </div>
        </div>

        <!-- Empty State (No Calendars) -->
        <EmptyState
          v-else
          icon="📅"
          title="Create Your First Calendar"
          :on-action="goToCreateCalendar"
          action-text="Create Your First Calendar"
        >
          <template #description>
            <p>📅 Create custom countdown calendars with video content</p>
            <p>🎬 Upload videos for each day (max 3 min, 50MB)</p>
            <p>🔗 Share privately with secure links</p>
          </template>
        </EmptyState>

      </div>

      <!-- Edit Calendar Modal - Same for Desktop & Mobile -->
      <ion-modal
        :is-open="isEditModalOpen"
        @didDismiss="closeEditModal"
      >
        <ion-header>
          <ion-toolbar color="primary">
            <ion-title>Edit Calendar</ion-title>
            <ion-buttons slot="end">
              <ion-button @click="closeEditModal" color="light">
                <strong>Close</strong>
              </ion-button>
            </ion-buttons>
          </ion-toolbar>
        </ion-header>
        <ion-content class="modal-content">
          <CalendarForm
            v-if="selectedCalendar"
            :calendar="selectedCalendar"
            :is-submitting="isSubmitting"
            @submit="handleEditSubmit"
            @cancel="closeEditModal"
          />
        </ion-content>
      </ion-modal>

    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue';
import { chevronDownCircleOutline, add, helpCircle, personCircle } from 'ionicons/icons';
import { useRouter, useRoute } from 'vue-router';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonButton,
  IonModal,
  IonIcon,
  IonRefresher,
  IonRefresherContent,
  IonSkeletonText
} from '@ionic/vue';
import { useAuth } from '@/composables/useAuth';
import { useCalendar } from '@/composables/useCalendar';
import { useResponsive } from '@/composables/useResponsive';
import { useToast } from '@/composables/useToast';
import { useAlert } from '@/composables/useAlert';
import ActionButton from '@/components/ActionButton.vue';
import CalendarCard from '@/components/CalendarCard.vue';
import CalendarForm from '@/components/CalendarForm.vue';
import EmptyState from '@/components/EmptyState.vue';
import type { Calendar, CalendarCreateData } from '@/types/calendar';

// Composables
const router = useRouter();
const route = useRoute();
const { isAuthenticated, redirectToLogin } = useAuth();
const { calendars, isLoading, hasCalendars, loadCalendars, updateCalendar } = useCalendar();
const { isMobile } = useResponsive();
const { showSuccess } = useToast();
const { showError } = useAlert();

// Error state for dashboard
const loadError = ref<string>('');

// Edit modal state
const isEditModalOpen = ref(false);
const selectedCalendar = ref<Calendar | null>(null);
const isSubmitting = ref(false);

// Lifecycle
onMounted(async () => {
  if (!isAuthenticated.value) {
    redirectToLogin();
    return;
  }

  // Load user's calendars from API
  await loadUserCalendars();
});

// Watch route changes to reload calendars when navigating back to dashboard
// This ensures video counts are up-to-date after editing calendars
watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/dashboard' && isAuthenticated.value) {
      loadUserCalendars();
    }
  }
);

// API Functions
const loadUserCalendars = async () => {
  try {
    loadError.value = '';
    const result = await loadCalendars();
    
    if (!result.success) {
      loadError.value = result.error || 'Failed to load calendars';
      console.error('Failed to load calendars:', result.error);
    }
  } catch (error) {
    loadError.value = 'Failed to load calendars';
    console.error('Failed to load calendars:', error);
  }
};

// Navigation functions
const goToCreateCalendar = () => {
  router.push('/calendar/create');
};

const openCalendar = (calendarId: string) => {
  router.push(`/calendar/${calendarId}/edit`);
};

const goToProfile = () => {
  router.push('/profile');
};

const goToHelp = () => {
  router.push('/help');
};

// Pull-to-refresh handler
const handleRefresh = async (event: CustomEvent) => {
  await loadUserCalendars();
  event.target.complete();
};

const handleEditSubmit = async (data: CalendarCreateData, calendarId?: string) => {
  if (!calendarId) {
    console.error('No calendar ID provided for update');
    return;
  }

  try {
    isSubmitting.value = true;

    const result = await updateCalendar(calendarId, data);

    if (result.success) {
      // Show success toast (consistent with calendar creation)
      await showSuccess('Calendar updated successfully!');

      // Close modal and reload calendars
      closeEditModal();
      await loadUserCalendars();
    } else {
      // Show error alert
      await showError(result.error || 'Failed to update calendar');
    }
  } catch (error) {
    console.error('Failed to update calendar:', error);
    await showError('An unexpected error occurred');
  } finally {
    isSubmitting.value = false;
  }
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
  selectedCalendar.value = null;
};
</script>

<style scoped>
/* Professional dashboard design using theme variables */
.dashboard-content {
  --background: var(--color-background);
}

.dashboard-container {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

/* Loading and Error States */
.loading-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  margin: var(--spacing-xl) 0;
}

.loading-section h2 {
  margin: 0 0 var(--spacing-md) 0;
  padding: 0 var(--spacing-md);
}

.skeleton-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-height: 200px;
}

.error-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  margin: var(--spacing-xl) 0;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.loading-content ion-spinner {
  --color: var(--ion-color-primary);
  width: 48px;
  height: 48px;
}

.loading-content p {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  margin: 0;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  text-align: center;
}

.error-message {
  font-size: var(--font-size-base);
  color: var(--ion-color-danger);
  font-weight: var(--font-weight-medium);
  margin: 0;
  padding: var(--spacing-md);
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  border: 1px solid rgba(var(--ion-color-danger-rgb), 0.3);
  border-radius: var(--radius-md);
}

/* Calendar sections */
.calendars-section {
  margin-bottom: var(--spacing-xl);
}

.calendars-section h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
  color: var(--color-text-primary);
}

/* Calendar grid */
.calendars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

/* Edit Modal Styling */
.modal-content {
  --padding-top: var(--spacing-md);
  --padding-bottom: var(--spacing-md);
  --padding-start: var(--spacing-md);
  --padding-end: var(--spacing-md);
}

/* Responsive design using theme breakpoints */
@media (max-width: 480px) {
  .calendars-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-container {
    padding: var(--spacing-sm);
  }
}

/* Tablet improvements */
@media (min-width: 768px) {
  .dashboard-container {
    max-width: 800px;
    padding: var(--spacing-lg);
  }
  
  .calendars-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: var(--spacing-lg);
  }
}

/* Desktop improvements */
@media (min-width: 1024px) {
  .dashboard-container {
    max-width: 1000px;
  }
  
  .calendars-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: var(--spacing-xl);
  }
}
</style>