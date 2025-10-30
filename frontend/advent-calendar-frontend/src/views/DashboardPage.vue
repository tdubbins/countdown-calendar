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

        <!-- Calendar Content -->
        <div v-if="userCalendars.length > 0" class="calendars-section">
          <h2>Your Calendars</h2>
          
          <!-- Calendar Grid -->
          <div class="calendars-grid">
            <CalendarCard
              v-for="calendar in displayedCalendars" 
              :key="calendar.id"
              :calendar="calendar"
              @click="openCalendar"
            />
          </div>
          
          <!-- View All Button (if more than displayed) -->
          <div v-if="hasMoreCalendars" class="view-all-section">
            <ActionButton 
              @click="goToMyCalendars"
              fill="outline"
              color="primary"
              variant="secondary"
            >
              View All Calendars ({{ userCalendars.length }})
            </ActionButton>
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
      
      <!-- Mobile: Floating Action Button -->
      <ion-fab 
        v-if="isMobile()" 
        slot="fixed" 
        vertical="bottom" 
        horizontal="end"
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
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonFab,
  IonFabButton,
  IonIcon
} from '@ionic/vue';
import { useAuth } from '@/composables/useAuth';
import { useResponsive } from '@/composables/useResponsive';
import ActionButton from '@/components/ActionButton.vue';
import CalendarCard from '@/components/CalendarCard.vue';
import EmptyState from '@/components/EmptyState.vue';
import type { CalendarSummary } from '@/types/calendar';

// Composables
const router = useRouter();
const { isAuthenticated, logout, redirectToLogin } = useAuth();
const { calendarDisplayLimit, isMobile } = useResponsive();

// Calendar data (typed with interface)
const userCalendars = ref<CalendarSummary[]>([
  // Empty for now - will be populated from API
  // Example structure matches CalendarSummary interface
]);

// Computed properties
const displayedCalendars = computed(() => {
  return userCalendars.value.slice(0, calendarDisplayLimit.value);
});

const hasMoreCalendars = computed(() => {
  return userCalendars.value.length > calendarDisplayLimit.value;
});

// Lifecycle
onMounted(() => {
  if (!isAuthenticated.value) {
    redirectToLogin();
  }
  
  // Load user's calendars from API
  loadUserCalendars();
});

// API Functions
const loadUserCalendars = async () => {
  try {
    // TODO: Replace with actual API call
    // For now, showing empty state to demonstrate the design
    userCalendars.value = [];
    
    // Example of how real data would look:
    // userCalendars.value = await calendarService.getUserCalendars();
  } catch (error) {
    console.error('Failed to load calendars:', error);
    // Handle error state
  }
};

// Logout functionality
const handleLogout = async () => {
  await logout();
};

// Navigation functions
const goToCreateCalendar = () => {
  router.push('/dashboard/create-calendar');
};

const goToMyCalendars = () => {
  // TODO: Navigate to full calendar list
  console.log('Navigate to all calendars');
};

const openCalendar = (calendarId: string) => {
  // TODO: Navigate to specific calendar
  console.log('Open calendar:', calendarId);
};

const goToProfile = () => {
  // TODO: Implement profile settings
  console.log('Navigate to profile');
};

const goToHelp = () => {
  // TODO: Implement help section
  console.log('Navigate to help');
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

/* View all section */
.view-all-section {
  text-align: center;
}

/* Secondary actions */
.secondary-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-2xl);
}

/* Floating Action Button */
.fab-create {
  --background: var(--brand-primary);
  --color: white;
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