<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary" class="accessible-toolbar">
        <ion-title class="accessible-title">Email Verification</ion-title>
      </ion-toolbar>
    </ion-header>
    
    <ion-content :fullscreen="true" class="verification-content">
      <div class="verification-container">
        <!-- Loading State -->
        <StatusCard
          v-if="isLoading"
          status="loading"
          title="Verifying your email..."
          message="Please wait while we verify your account."
          loading-text="Verifying email"
        />

        <!-- Success State -->
        <StatusCard
          v-else-if="verificationStatus === 'success'"
          status="success"
          title="Email Verified Successfully!"
          :message="successMessage"
        >
          <template #actions>
            <ActionButton
              variant="primary"
              @click="goToLogin"
              aria-label="Continue to sign in page"
            >
              ✨ Continue to Sign In
            </ActionButton>
            
            <ActionButton
              variant="secondary"
              fill="clear"
              color="medium"
              @click="goToHome"
              aria-label="Return to home page"
            >
              Return to Home
            </ActionButton>
          </template>
        </StatusCard>

        <!-- Error State -->
        <StatusCard
          v-else-if="verificationStatus === 'error'"
          status="error"
          title="Verification Failed"
          :message="errorMessage"
        >
          <template #additional-content>
            <ErrorHelp
              :suggestions="errorSuggestions"
              help-title="What can you do?"
            />
          </template>
          
          <template #actions>
            <ActionButton
              variant="primary"
              @click="goToRegister"
              aria-label="Try registration again"
            >
              Try Registration Again
            </ActionButton>
            
            <ActionButton
              variant="secondary"
              fill="clear"
              color="medium"
              @click="goToHome"
              aria-label="Return to home page"
            >
              Return to Home
            </ActionButton>
          </template>
        </StatusCard>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent
} from '@ionic/vue';
import StatusCard from '@/components/StatusCard.vue';
import ActionButton from '@/components/ActionButton.vue';
import ErrorHelp from '@/components/ErrorHelp.vue';
import { API_ENDPOINTS } from '@/config/api';

// Router and route
const route = useRoute();
const router = useRouter();

// Component state
const isLoading = ref(true);
const verificationStatus = ref<'loading' | 'success' | 'error'>('loading');
const successMessage = ref('');
const errorMessage = ref('');
const isTokenExpired = ref(false);
const isTokenUsed = ref(false);

// Computed error suggestions
const errorSuggestions = computed(() => {
  const suggestions = [];
  
  if (isTokenExpired.value) {
    suggestions.push('Request a new verification email from your account settings');
  } else if (isTokenUsed.value) {
    suggestions.push('This link has already been used - your email may already be verified');
  } else {
    suggestions.push('Check that you clicked the correct link from your email');
  }
  
  suggestions.push('Contact support if you continue having issues');
  return suggestions;
});

// Get token from URL parameters
const token = route.params.token as string;

// API call to verify email
const verifyEmail = async (verificationToken: string) => {
  try {
    const response = await fetch(API_ENDPOINTS.VERIFY_EMAIL(verificationToken), {
      method: 'GET',
    });
    
    const data = await response.json();
    
    if (response.ok && data.success) {
      verificationStatus.value = 'success';
      successMessage.value = data.message || 'Your account is now active!';
    } else {
      verificationStatus.value = 'error';
      errorMessage.value = data.error || 'Verification failed';
      
      // Check for specific error types
      const errorLower = errorMessage.value.toLowerCase();
      isTokenExpired.value = errorLower.includes('expired');
      isTokenUsed.value = errorLower.includes('already been used');
    }
  } catch (error) {
    verificationStatus.value = 'error';
    errorMessage.value = 'Network error. Please check your connection and try again.';
    console.error('Verification error:', error);
  } finally {
    isLoading.value = false;
  }
};

// Navigation functions
const goToLogin = () => {
  router.push('/login');
};

const goToHome = () => {
  router.push('/login');
};

const goToRegister = () => {
  router.push('/register');
};

// Component lifecycle
onMounted(() => {
  // Validate token exists
  if (!token || typeof token !== 'string') {
    verificationStatus.value = 'error';
    errorMessage.value = 'Invalid verification link. Please check your email and try again.';
    isLoading.value = false;
    return;
  }
  
  // Perform verification
  verifyEmail(token);
});
</script>

<style scoped>
/* Accessible toolbar styling */
.accessible-toolbar {
  --background: #4c51bf;
  --color: white;
}

.accessible-title {
  --color: white;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* Main container layout */
.verification-content {
  --background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.verification-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* Responsive design */
@media (max-width: 480px) {
  .verification-container {
    padding: 16px;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .accessible-toolbar {
    --background: #000000;
    --color: #ffffff;
  }
  
  .accessible-title {
    --color: #ffffff;
    font-weight: 700;
  }
}
</style>