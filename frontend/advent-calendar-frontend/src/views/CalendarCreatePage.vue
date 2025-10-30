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
          :is-submitting="isLoading"
          @submit="handleFormSubmit"
          @cancel="handleCancel"
        />
        
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-overlay">
          <ion-spinner name="crescent" color="primary"></ion-spinner>
          <p>Creating your calendar...</p>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
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
import { useResponsive } from '@/composables/useResponsive';
import CalendarForm from '@/components/CalendarForm.vue';
import type { CalendarCreateData } from '@/types/calendar';

// Composables
const router = useRouter();
const { isAuthenticated, redirectToLogin } = useAuth();
const { isMobile } = useResponsive();

// Reactive state
const isLoading = ref(false);

// Form submission handler
const handleFormSubmit = async (formData: CalendarCreateData) => {
  try {
    isLoading.value = true;
    
    // TODO: Replace with actual API call to create calendar
    console.log('Creating calendar with data:', formData);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Show success alert
    const alert = await alertController.create({
      header: 'Success! 🎉',
      message: `Your calendar "${formData.title}" has been created successfully!`,
      buttons: [
        {
          text: 'View Calendar',
          handler: () => {
            // TODO: Navigate to the specific calendar view
            console.log('Navigate to calendar view');
            router.push('/dashboard');
          }
        },
        {
          text: 'Back to Dashboard',
          handler: () => {
            router.push('/dashboard');
          }
        }
      ]
    });
    
    await alert.present();
    
  } catch (error) {
    console.error('Failed to create calendar:', error);
    
    // Show error alert
    const alert = await alertController.create({
      header: 'Creation Failed',
      message: 'Sorry, we couldn\'t create your calendar. Please try again.',
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
  router.push('/dashboard');
};

// Authentication check
if (!isAuthenticated.value) {
  redirectToLogin();
}
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