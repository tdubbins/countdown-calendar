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

            <!-- Resend Verification Email Section -->
            <div class="resend-container">
              <p class="resend-info">Need a new verification link?</p>

              <IonFormField
                v-model="resendEmail"
                label="Email Address"
                type="email"
                placeholder="Enter your email"
                :required="true"
                :error-message="resendEmailError"
                autocomplete="email"
                @blur="validateResendEmail"
                @update:model-value="clearResendEmailError"
              />

              <ion-button
                expand="block"
                color="primary"
                @click="handleResendVerification"
                :disabled="isResending || !resendEmail"
                class="resend-action-button"
                aria-label="Resend verification email"
              >
                <ion-spinner
                  v-if="isResending"
                  name="crescent"
                  aria-label="Sending email"
                ></ion-spinner>
                <span v-else>📧 Resend Verification Email</span>
              </ion-button>

              <!-- Resend Success/Error Message -->
              <div
                v-if="resendMessage"
                :class="['resend-message', resendMessageType === 'success' ? 'success' : 'error']"
                role="status"
                aria-live="polite"
              >
                <p>{{ resendMessage }}</p>
              </div>
            </div>
          </template>

          <template #actions>
            <ActionButton
              variant="secondary"
              fill="outline"
              @click="goToLogin"
              aria-label="Go to login page"
            >
              Go to Login
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
  IonContent,
  IonButton,
  IonSpinner
} from '@ionic/vue';
import StatusCard from '@/components/StatusCard.vue';
import ActionButton from '@/components/ActionButton.vue';
import ErrorHelp from '@/components/ErrorHelp.vue';
import IonFormField from '@/components/IonFormField.vue';
import { API_ENDPOINTS } from '@/config/api';
import { useResendVerification } from '@/composables/useResendVerification';
import { validateEmail } from '@/utils/validators';

// Router and route
const route = useRoute();
const router = useRouter();

// Resend verification composable
const {
  isResending,
  message: resendMessage,
  messageType: resendMessageType,
  resend: resendVerification
} = useResendVerification();

// Component state
const isLoading = ref(true);
const verificationStatus = ref<'loading' | 'success' | 'error'>('loading');
const successMessage = ref('');
const errorMessage = ref('');
const isTokenExpired = ref(false);
const isTokenUsed = ref(false);

// Resend email input state
const resendEmail = ref('');
const resendEmailError = ref('');

// Computed error suggestions
const errorSuggestions = computed(() => {
  const suggestions = [];

  if (isTokenExpired.value) {
    suggestions.push('Use the form below to request a new verification email');
  } else if (isTokenUsed.value) {
    suggestions.push('This link has already been used - try logging in or request a new link below');
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

// Email validation for resend
const validateResendEmail = () => {
  const result = validateEmail(resendEmail.value);
  resendEmailError.value = result.error;
};

const clearResendEmailError = () => {
  resendEmailError.value = '';
};

// Handle resend verification
const handleResendVerification = async () => {
  // Validate email
  validateResendEmail();
  if (resendEmailError.value) {
    return;
  }

  // Use composable to resend, clear email field on success
  await resendVerification(resendEmail.value, () => {
    resendEmail.value = '';
  });
};

// Navigation functions
const goToLogin = () => {
  router.push('/login');
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

/* Resend verification container */
.resend-container {
  margin-top: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.resend-info {
  color: #4a5568;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  text-align: center;
}

.resend-action-button {
  margin-top: 12px;
  height: 48px;
  font-weight: 600;
  font-size: 1rem;
  --border-radius: 10px;
  text-transform: none;
}

.resend-action-button:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

.resend-message {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.resend-message.success {
  background: #d1f2d1;
  color: #0f5132;
  border: 1px solid #a3d977;
}

.resend-message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.resend-message p {
  margin: 0;
}

/* Responsive design */
@media (max-width: 480px) {
  .verification-container {
    padding: 16px;
  }

  .resend-container {
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