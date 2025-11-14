<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Countdown Calendar</ion-title>
        <ion-buttons slot="end">
          <!-- Desktop: Create button in header -->
          <ActionButton 
            v-if="!isMobile()"
            @click="goToCreateCalendar"
            fill="solid" 
            color="light" 
            variant="secondary"
            size="small"
            icon="add"
            icon-slot="start"
            aria-label="Create new calendar"
          >
            New
          </ActionButton>
          
          <ActionButton 
            @click="handleLogout" 
            fill="clear" 
            color="light" 
            variant="secondary"
            size="small"
            aria-label="Logout from dashboard"
          >
            🚪 Logout
          </ActionButton>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>
    
    <ion-content :fullscreen="true" class="dashboard-content">
      <div class="dashboard-container">

        <!-- Loading State (NFR [P1]: Dashboard loads under 5 seconds) -->
        <div v-if="isLoading" class="loading-section">
          <div class="loading-content">
            <ion-spinner name="crescent" color="primary"></ion-spinner>
            <p>Loading your calendars...</p>
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

        <!-- Calendar Content (NFR [U1][U2]: Mobile responsive with 44px+ touch targets) -->
        <div v-else-if="hasCalendars" class="calendars-section">
          <h2>Your Calendars ({{ calendars.length }})</h2>
          
          <!-- Calendar Grid - Display All Calendars -->
          <div class="calendars-grid">
            <CalendarCard
              v-for="calendar in calendars"
              :key="calendar.id"
              :calendar="calendar"
              @click="openCalendar"
              @edit="handleEditCalendar"
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

        <!-- Secondary Actions -->
        <div class="secondary-actions">
          <ActionButton 
            @click="goToProfile"
            fill="clear"
            color="medium"
            variant="secondary"
            icon="settings"
            icon-slot="start"
          >
            Account Settings
          </ActionButton>
          
          <ActionButton 
            @click="goToHelp"
            fill="clear"
            color="medium"
            variant="secondary"
            icon="help-circle"
            icon-slot="start"
          >
            Help & Support
          </ActionButton>
        </div>
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

      <!-- Mobile: Floating Action Button (NFR [U2]: 44px+ touch target for mobile) -->
      <ion-fab
        v-if="isMobile()"
        slot="fixed"
        vertical="bottom"
        horizontal="end"
        edge
        class="fab-create"
      >
        <ion-fab-button
          @click="goToCreateCalendar"
          color="primary"
          aria-label="Create new calendar"
        >
          <ion-icon name="add"></ion-icon>
        </ion-fab-button>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue';
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
  IonFab,
  IonFabButton,
  IonIcon,
  IonSpinner
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
const { isAuthenticated, logout, redirectToLogin } = useAuth();
const { calendars, isLoading, hasCalendars, loadCalendars, getCalendar, updateCalendar } = useCalendar();
const { isMobile } = useResponsive();
const { showSuccess } = useToast();
const { showError } = useAlert();

// Error state for dashboard
const loadError = ref<string>('');

// Edit modal state
const isEditModalOpen = ref(false);
const selectedCalendar = ref<Calendar | null>(null);
const isSubmitting = ref(false);

// Lifecycle (NFR [P1]: Dashboard loads under 5 seconds)
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

// Logout functionality
const handleLogout = async () => {
  await logout();
};

// Navigation functions
const goToCreateCalendar = () => {
  router.push('/calendar/create');
};

const openCalendar = (calendarId: string) => {
  router.push(`/calendar/${calendarId}/edit`);
};

const goToProfile = () => {
  // TODO: Implement profile settings
  console.log('Navigate to profile');
};

const goToHelp = () => {
  // TODO: Implement help section
  console.log('Navigate to help');
};

// Edit calendar functionality
const handleEditCalendar = async (calendarId: string) => {
  try {
    // Fetch the full calendar object with all fields (including endDate)
    const result = await getCalendar(calendarId);

    if (result.success && result.data) {
      selectedCalendar.value = result.data;
      isEditModalOpen.value = true;
    } else {
      await showError('Failed to load calendar data');
    }
  } catch (error) {
    console.error('Failed to load calendar:', error);
    await showError('An unexpected error occurred');
  }
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
.loading-section,
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

/* Secondary actions */
.secondary-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-2xl);
}

/* Floating Action Button (NFR [U2]: Mobile-optimized touch target) */
.fab-create {
  --background: var(--brand-primary);
  --color: white;

  /* Positioning & spacing - safe from screen edges */
  margin-bottom: 20px;  /* Space from bottom edge */
  margin-right: 16px;   /* Space from right edge */

  /* Ensure FAB stays on top of all content */
  z-index: 999;

  /* Enhanced visibility with shadow */
  --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.10);
}

/* FAB button size optimization for thumb reach */
.fab-create ion-fab-button {
  --size: 56px;  /* Standard Material Design FAB size (44px+ for NFR [U2]) */

  /* Smooth interactions */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* Active state feedback */
.fab-create ion-fab-button:active {
  transform: scale(0.95);
}

/* Ensure adequate spacing from secondary actions */
@media (max-width: 480px) {
  .fab-create {
    margin-bottom: 80px;  /* Extra space to avoid overlapping secondary actions */
  }
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
  
  .secondary-actions {
    flex-direction: row;
    gap: var(--spacing-md);
    justify-content: center;
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