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
            <div class="logo-icon">📅</div>
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
            @blur="validateEmail"
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

// Router for navigation
const router = useRouter();

// Authentication composable
const { login, isLoading } = useAuth();

// Form data
const email = ref('');
const password = ref('');

// Error states
const emailError = ref('');
const passwordError = ref('');
const errorMessage = ref('');
const successMessage = ref('');

// Form validation
const isFormValid = computed(() => {
  return email.value && 
         password.value &&
         !emailError.value &&
         !passwordError.value;
});

// Validation functions
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email.value) {
    emailError.value = 'Email is required';
  } else if (!emailRegex.test(email.value)) {
    emailError.value = 'Please enter a valid email address';
  } else {
    emailError.value = '';
  }
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
  
  // Validate all fields
  validateEmail();
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
    }
    
  } catch (error: any) {
    errorMessage.value = 'An unexpected error occurred';
  }
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
  font-size: 3.5rem;
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
    font-size: 3rem;
  }
}
</style>