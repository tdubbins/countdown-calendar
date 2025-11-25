<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Sign In</ion-title>
      </ion-toolbar>
    </ion-header>
    
    <ion-content :fullscreen="true" class="login-content">
      <div class="login-container">
        <div class="login-header">
          <div class="logo-section">
            <img src="@/assets/logo.png" alt="Countdown Calendar Logo" class="logo-icon" />
            <h1>Countdown Calendar</h1>
          </div>
          <p class="subtitle">Welcome back! Sign in to continue building your countdown experiences</p>
        </div>

        <form @submit.prevent="handleSubmit" class="login-form">
          <!-- Email Field -->
          <IonFormField
            v-model="email"
            label="Email Address"
            type="email"
            placeholder="Enter your email"
            :required="true"
            :error-message="emailError"
            autocomplete="email"
            @blur="validateEmailField"
            @update:model-value="clearEmailError"
          />

          <!-- Password Field -->
          <PasswordField
            v-model="password"
            label="Password"
            placeholder="Enter your password"
            :required="true"
            :error-message="passwordError"
            autocomplete="current-password"
            @blur="validatePassword"
            @update:model-value="clearPasswordError"
          />

          <!-- Submit Button -->
          <ion-button 
            type="submit" 
            expand="block" 
            :disabled="!isFormValid || isLoading"
            class="submit-button"
            size="large"
            color="primary"
            :aria-describedby="errorMessage ? 'form-error' : (successMessage ? 'form-success' : undefined)"
          >
            <ion-spinner 
              v-if="isLoading" 
              name="crescent"
              aria-label="Signing in"
            ></ion-spinner>
            <span v-else>🔑 Sign In</span>
          </ion-button>

          <!-- Success/Error Messages -->
          <div
            v-if="successMessage"
            class="message success-message"
            id="form-success"
            role="status"
            aria-live="polite"
          >
            <ion-icon :icon="checkmarkCircle" class="message-icon" aria-hidden="true"></ion-icon>
            <p>{{ successMessage }}</p>
          </div>

          <div
            v-if="errorMessage"
            class="message error-message"
            id="form-error"
            role="alert"
            aria-live="assertive"
          >
            <ion-icon :icon="alertCircle" class="message-icon" aria-hidden="true"></ion-icon>
            <p>{{ errorMessage }}</p>
          </div>

          <!-- Resend Verification Button (shown only for verification errors) -->
          <div
            v-if="showResendVerification"
            class="resend-section"
          >
            <p class="resend-text">Didn't receive the verification email?</p>
            <ion-button
              expand="block"
              fill="outline"
              color="primary"
              @click="handleResendVerification"
              :disabled="isLoading || isResending"
              class="resend-button"
              aria-label="Resend verification email"
            >
              <ion-spinner
                v-if="isResending"
                name="crescent"
                aria-label="Sending email"
              ></ion-spinner>
              <span v-else>📧 Resend Verification Email</span>
            </ion-button>

            <!-- Resend Message -->
            <div
              v-if="resendMessage"
              :class="['message', resendMessageType === 'success' ? 'resend-success-message' : 'resend-error-message']"
              role="status"
              aria-live="polite"
            >
              <ion-icon :icon="resendMessageType === 'success' ? checkmarkCircle : alertCircle" class="message-icon" aria-hidden="true"></ion-icon>
              <p>{{ resendMessage }}</p>
            </div>
          </div>
        </form>

        <!-- Register Link -->
        <div class="register-link">
          <p>Don't have an account?</p>
          <ion-button fill="clear" @click="goToRegister" class="link-button">
            Create Account →
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonIcon,
  IonSpinner
} from '@ionic/vue';
import { checkmarkCircle, alertCircle } from 'ionicons/icons';
import IonFormField from '@/components/IonFormField.vue';
import PasswordField from '@/components/PasswordField.vue';
import { useAuth } from '@/composables/useAuth';
import { useResendVerification } from '@/composables/useResendVerification';
import { validateEmail } from '@/utils/validators';

// Router for navigation
const router = useRouter();

// Authentication composable
const { login, isLoading } = useAuth();

// Resend verification composable
const {
  isResending,
  message: resendMessage,
  messageType: resendMessageType,
  resend: resendVerification
} = useResendVerification();

// Form data
const email = ref('');
const password = ref('');

// Error states
const emailError = ref('');
const passwordError = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const showResendVerification = ref(false);

// Form validation
const isFormValid = computed(() => {
  return email.value && 
         password.value &&
         !emailError.value &&
         !passwordError.value;
});

// Validation functions
const validateEmailField = () => {
  const result = validateEmail(email.value);
  emailError.value = result.error;
};

const validatePassword = () => {
  if (!password.value) {
    passwordError.value = 'Password is required';
  } else {
    passwordError.value = '';
  }
};

// Clear error functions
const clearEmailError = () => {
  emailError.value = '';
};

const clearPasswordError = () => {
  passwordError.value = '';
};

// Form submission
const handleSubmit = async () => {
  // Clear previous messages
  errorMessage.value = '';
  successMessage.value = '';
  showResendVerification.value = false;

  // Validate all fields
  validateEmailField();
  validatePassword();

  // Check if form is valid
  if (!isFormValid.value) {
    errorMessage.value = 'Please fix the errors above';
    return;
  }

  try {
    const result = await login(email.value, password.value);

    if (result.success) {
      // Show success message
      successMessage.value = '✅ Login successful! Redirecting to dashboard...';

      // Clear form
      email.value = '';
      password.value = '';
      emailError.value = '';
      passwordError.value = '';

      // Redirect to calendar overview after 2 seconds
      setTimeout(() => {
        successMessage.value = '';
        router.push('/calendar');
      }, 2000);
    } else {
      errorMessage.value = result.message;

      // Check if error is about email verification
      if (result.message.toLowerCase().includes('verify your email')) {
        showResendVerification.value = true;
      }
    }

  } catch (error: any) {
    errorMessage.value = 'An unexpected error occurred';
  }
};

// Handle resend verification email
const handleResendVerification = async () => {
  await resendVerification(email.value);
};

// Navigation
const goToRegister = () => {
  router.push('/register');
};
</script>

<style scoped>
/* Main container and layout */
.login-content {
  --background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  max-width: 420px;
  margin: 0 auto;
  padding: 32px 24px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Header styling */
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-section {
  margin-bottom: 16px;
}

.logo-icon {
  width: 200px;
  height: auto;
  margin-bottom: 12px;
}

.login-header h1 {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  line-height: 1.4;
  margin: 0;
}

/* Form styling */
.login-form {
  background: white;
  padding: 32px 24px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  margin-bottom: 24px;
}

/* Submit button */
.submit-button {
  margin-top: 24px;
  height: 56px;
  font-weight: 700;
  font-size: 1.1rem;
  --border-radius: 12px;
  --box-shadow: 0 4px 15px rgba(var(--ion-color-primary-rgb), 0.4);
  text-transform: none;
  letter-spacing: 0.5px;
}

.submit-button:not(.button-disabled):hover {
  transform: translateY(-2px);
  --box-shadow: 0 6px 20px rgba(var(--ion-color-primary-rgb), 0.5);
}

.submit-button:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* Messages */
.message {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
  padding: 16px;
  border-radius: 12px;
  font-weight: 500;
  text-align: left;
}

.success-message {
  background: #d1f2d1;
  color: #0f5132;
  border: 1px solid #a3d977;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.message p {
  margin: 0;
  font-size: 1rem;
  line-height: 1.4;
}

/* Resend verification section */
.resend-section {
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

.resend-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  margin: 0 0 12px 0;
  text-align: center;
}

.resend-button {
  margin-top: 0;
  height: 48px;
  font-weight: 600;
  font-size: 1rem;
  --border-radius: 10px;
  text-transform: none;
}

.resend-button:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

.resend-success-message {
  margin-top: 12px;
  background: rgba(209, 242, 209, 0.95);
  color: #0f5132;
  border: 1px solid #a3d977;
  font-size: 0.9rem;
  padding: 12px;
}

.resend-error-message {
  margin-top: 12px;
  background: rgba(248, 215, 218, 0.95);
  color: #721c24;
  border: 1px solid #f5c6cb;
  font-size: 0.9rem;
  padding: 12px;
}

/* Register link */
.register-link {
  text-align: center;
  margin-top: 20px;
}

.register-link p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  margin-bottom: 8px;
}

.link-button {
  --color: white;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: underline;
}

.link-button:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* Responsive design */
@media (max-width: 480px) {
  .login-container {
    padding: 20px 16px;
  }
  
  .login-form {
    padding: 24px 20px;
  }
  
  .login-header h1 {
    font-size: 1.8rem;
  }
}

@media (max-width: 320px) {
  .login-container {
    padding: 16px 12px;
  }
  
  .login-header h1 {
    font-size: 1.6rem;
  }

  .logo-icon {
    width: 150px;
  }
}
</style>