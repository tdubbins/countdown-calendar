<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-back-button 
            default-href="/dashboard"
            :text="isMobile() ? '' : 'Dashboard'"
            aria-label="Back to dashboard"
          ></ion-back-button>
        </ion-buttons>
        <ion-title>Create Calendar</ion-title>
      </ion-toolbar>
    </ion-header>
    
    <ion-content :fullscreen="true" class="create-content">
      <div class="create-container">
        <!-- Calendar Form -->
        <CalendarForm
          ref="calendarFormRef"
          :is-submitting="isLoading"
          @submit="handleFormSubmit"
          @cancel="handleCancel"
        />
        
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-overlay" aria-live="polite" aria-label="Creating calendar">
          <ion-spinner name="crescent" color="primary" aria-hidden="true"></ion-spinner>
          <p>Creating your calendar...</p>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonBackButton,
  IonSpinner,
  alertController
} from '@ionic/vue';
import { useAuth } from '@/composables/useAuth';
import { useCalendar } from '@/composables/useCalendar';
import { useResponsive } from '@/composables/useResponsive';
import CalendarForm from '@/components/CalendarForm.vue';
import type { CalendarCreateData } from '@/types/calendar';

// Composables
const router = useRouter();
const route = useRoute();
const { isAuthenticated, redirectToLogin } = useAuth();
const { createCalendar } = useCalendar();
const { isMobile } = useResponsive();

// Reactive state
const isLoading = ref(false);

// Reference to the calendar form component
const calendarFormRef = ref<any>(null);

// Form submission handler (NFR [P3]: Calendar creation completes under 3 seconds)
const handleFormSubmit = async (formData: CalendarCreateData) => {
  try {
    isLoading.value = true;
    
    // Call the calendar service to create calendar (NFR [S4]: Input validation on API call)
    const result = await createCalendar(formData);
    
    if (result.success && result.data) {
      // Show success alert (NFR [U4]: Clear success feedback)
      const alert = await alertController.create({
        header: 'Success! 🎉',
        message: `Your calendar "${result.data.title}" has been created successfully!`,
        buttons: [
          {
            text: 'View Calendar',
            handler: () => {
              // Navigate to the calendar detail page (day grid)
              console.log('Navigate to calendar view for ID:', result.data?.id);
              // Use setTimeout to ensure proper focus management
              setTimeout(() => router.push(`/dashboard/calendar/${result.data?.id}`), 100);
            }
          },
          {
            text: 'Back to Dashboard',
            handler: () => {
              // Use setTimeout to ensure proper focus management
              setTimeout(() => router.push('/dashboard'), 100);
            }
          }
        ]
      });

      await alert.present();
      
    } else {
      // Enhanced error handling with specific messaging for uniqueness errors
      const isUniquenessError = result.error?.toLowerCase().includes('already have a calendar named');
      
      const alert = await alertController.create({
        header: isUniquenessError ? 'Calendar Name Already Used' : 'Creation Failed',
        message: result.error || 'Sorry, we couldn\'t create your calendar. Please try again.',
        buttons: [
          {
            text: isUniquenessError ? 'Choose Different Name' : 'Try Again',
            role: 'cancel'
          }
        ]
      });
      
      await alert.present();
    }
    
  } catch (error) {
    console.error('Failed to create calendar:', error);
    
    // Show generic error alert (NFR [U4]: Clear error feedback)
    const alert = await alertController.create({
      header: 'Creation Failed',
      message: 'Sorry, we couldn\'t create your calendar. Please check your connection and try again.',
      buttons: [
        {
          text: 'Try Again',
          role: 'cancel'
        }
      ]
    });
    
    await alert.present();
  } finally {
    isLoading.value = false;
  }
};

// Cancel handler
const handleCancel = () => {
  // Use setTimeout to ensure proper focus management
  setTimeout(() => router.push('/dashboard'), 100);
};

// Helper function to reset form
const resetFormData = async () => {
  // Wait for next tick to ensure component is fully mounted
  await nextTick();
  
  // Reset form to ensure clean state for new calendar creation
  if (calendarFormRef.value && calendarFormRef.value.resetForm) {
    calendarFormRef.value.resetForm();
  }
};

// Watch for route changes to reset form
watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/dashboard/create-calendar') {
      resetFormData();
    }
  },
  { immediate: false }
);

// Lifecycle
onMounted(async () => {
  // Check authentication
  if (!isAuthenticated.value) {
    redirectToLogin();
    return;
  }
  
  // Reset form on initial mount
  await resetFormData();
});
</script>

<style scoped>
/* Professional page styling using theme system */
.create-content {
  --background: var(--color-background);
}

.create-container {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-md);
  position: relative;
  min-height: 100vh;
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  backdrop-filter: blur(4px);
}

.loading-overlay ion-spinner {
  --color: var(--ion-color-primary);
  width: 48px;
  height: 48px;
  margin-bottom: var(--spacing-md);
}

.loading-overlay p {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  margin: 0;
}

/* Responsive design */
@media (max-width: 480px) {
  .create-container {
    padding: var(--spacing-sm);
  }
}

@media (min-width: 768px) {
  .create-container {
    padding: var(--spacing-lg);
  }
}

@media (min-width: 1024px) {
  .create-container {
    max-width: 800px;
    padding: var(--spacing-xl);
  }
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .loading-overlay {
    background: rgba(26, 26, 26, 0.9);
  }
}

/* Page animation */
.create-container {
  animation: slideInUp var(--transition-slow);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>