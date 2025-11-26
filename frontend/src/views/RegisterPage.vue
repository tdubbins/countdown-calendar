<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Create Account</ion-title>
      </ion-toolbar>
    </ion-header>
    
    <ion-content :fullscreen="true" class="register-content">
      <div class="register-container">
        <div class="register-header">
          <div class="logo-section">
            <img src="@/assets/logo.png" alt="Countdown Calendar Logo" class="logo-icon" />
            <h1>Countdown Calendar</h1>
          </div>
          <p class="subtitle">Create your account to start building engaging countdown experiences</p>
        </div>

        <form @submit.prevent="handleSubmit" class="register-form">
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
            autocomplete="new-password"
            requirements-id="password-requirements"
            @blur="validatePasswordField"
            @update:model-value="clearPasswordError"
          />

          <!-- Password Requirements -->
          <PasswordRequirements
            ref="passwordRequirementsRef"
            :password="password"
          />

          <!-- Confirm Password Field -->
          <PasswordField
            v-model="confirmPassword"
            label="Confirm Password"
            placeholder="Confirm your password"
            :required="true"
            :error-message="confirmPasswordError"
            autocomplete="new-password"
            @blur="validateConfirmPasswordField"
            @update:model-value="clearConfirmPasswordError"
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
              aria-label="Creating account"
            ></ion-spinner>
            <span v-else>✨ Create Account</span>
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
        </form>

        <!-- Login Link -->
        <div class="login-link">
          <p>Already have an account?</p>
          <ion-button fill="clear" @click="goToLogin" class="link-button">
            Sign In →
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
import PasswordRequirements from '@/components/PasswordRequirements.vue';
import { useAuth } from '@/composables/useAuth';
import { validateEmail, validatePassword, validatePasswordsMatch, checkPasswordRequirements } from '@/utils/validators';

// Router for navigation
const router = useRouter();

// Form data
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

// UI state
const isLoading = ref(false);

// Error states
const emailError = ref('');
const passwordError = ref('');
const confirmPasswordError = ref('');
const errorMessage = ref('');
const successMessage = ref('');

// Component refs
const passwordRequirementsRef = ref();

// Password validation logic using utility
const passwordChecks = computed(() => checkPasswordRequirements(password.value));
const isPasswordValid = computed(() => passwordChecks.value.isValid);

// Form validation
const isFormValid = computed(() => {
  return email.value && 
         isPasswordValid.value && 
         confirmPassword.value && 
         password.value === confirmPassword.value &&
         !emailError.value &&
         !passwordError.value &&
         !confirmPasswordError.value;
});

// Validation functions
const validateEmailField = () => {
  const result = validateEmail(email.value);
  emailError.value = result.error;
};

const validatePasswordField = () => {
  const result = validatePassword(password.value);
  passwordError.value = result.error;

  // Re-validate confirm password if it exists
  if (confirmPassword.value) {
    validateConfirmPasswordField();
  }
};

const validateConfirmPasswordField = () => {
  const result = validatePasswordsMatch(password.value, confirmPassword.value);
  confirmPasswordError.value = result.error;
};

// Clear error functions
const clearEmailError = () => {
  emailError.value = '';
};

const clearPasswordError = () => {
  passwordError.value = '';
};

const clearConfirmPasswordError = () => {
  confirmPasswordError.value = '';
};

// Authentication composable
const { register } = useAuth();

// Form submission
const handleSubmit = async () => {
  // Clear previous messages
  errorMessage.value = '';
  successMessage.value = '';

  // Validate all fields
  validateEmailField();
  validatePasswordField();
  validateConfirmPasswordField();
  
  // Check if form is valid
  if (!isFormValid.value) {
    errorMessage.value = 'Please fix the errors above';
    return;
  }
  
  isLoading.value = true;
  
  try {
    const result = await register(email.value, password.value, confirmPassword.value);
    
    if (result.success) {
      // Clear form first
      email.value = '';
      password.value = '';
      confirmPassword.value = '';
      
      // Clear any existing errors
      emailError.value = '';
      passwordError.value = '';
      confirmPasswordError.value = '';
      
      // Show success message
      successMessage.value = '✅ Account created successfully! Please check your email to verify your account.';
      
      // Redirect to login page after 3 seconds
      setTimeout(() => {
        successMessage.value = '';
        goToLogin();
      }, 3000);
    } else {
      errorMessage.value = result.message;
    }
    
  } catch (error: any) {
    errorMessage.value = 'An unexpected error occurred';
  } finally {
    isLoading.value = false;
  }
};

// Navigation
const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
/* Main container and layout */
.register-content {
  --background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-container {
  max-width: 420px;
  margin: 0 auto;
  padding: 32px 24px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Header styling */
.register-header {
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

.register-header h1 {
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
.register-form {
  background: var(--color-surface);
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
  background: var(--color-success-bg);
  color: var(--color-success-text);
  border: 1px solid var(--color-success-border);
}

.error-message {
  background: var(--color-error-bg);
  color: var(--color-error-text);
  border: 1px solid var(--color-error-border);
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

/* Login link */
.login-link {
  text-align: center;
  margin-top: 20px;
}

.login-link p {
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
  .register-container {
    padding: 20px 16px;
  }
  
  .register-form {
    padding: 24px 20px;
  }
  
  .register-header h1 {
    font-size: 1.8rem;
  }
}

@media (max-width: 320px) {
  .register-container {
    padding: 16px 12px;
  }
  
  .register-header h1 {
    font-size: 1.6rem;
  }

  .logo-icon {
    width: 150px;
  }
}
</style>