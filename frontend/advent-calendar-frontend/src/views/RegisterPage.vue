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
            <div class="logo-icon">📅</div>
            <h1>Countdown Calendar</h1>
          </div>
          <p class="subtitle">Create your account to start building engaging countdown experiences</p>
        </div>

        <form @submit.prevent="handleSubmit" class="register-form">
          <!-- Email Field -->
          <FormField
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
            autocomplete="new-password"
            requirements-id="password-requirements"
            @blur="validatePassword"
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
            @blur="validateConfirmPassword"
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
            <ion-icon name="checkmark-circle" class="message-icon" aria-hidden="true"></ion-icon>
            <p>{{ successMessage }}</p>
          </div>
          
          <div 
            v-if="errorMessage" 
            class="message error-message"
            id="form-error"
            role="alert"
            aria-live="assertive"
          >
            <ion-icon name="alert-circle" class="message-icon" aria-hidden="true"></ion-icon>
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
import FormField from '@/components/FormField.vue';
import PasswordField from '@/components/PasswordField.vue';
import PasswordRequirements from '@/components/PasswordRequirements.vue';

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

// Password validation logic (duplicated from component for consistency)
const hasMinLength = computed(() => password.value.length >= 8);
const hasUppercase = computed(() => /[A-Z]/.test(password.value));
const hasLowercase = computed(() => /[a-z]/.test(password.value));
const hasNumber = computed(() => /\d/.test(password.value));
const isPasswordValid = computed(() => 
  hasMinLength.value && hasUppercase.value && hasLowercase.value && hasNumber.value
);

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
  } else if (!isPasswordValid.value) {
    passwordError.value = 'Password does not meet requirements';
  } else {
    passwordError.value = '';
  }
  // Re-validate confirm password if it exists
  if (confirmPassword.value) {
    validateConfirmPassword();
  }
};

const validateConfirmPassword = () => {
  if (!confirmPassword.value) {
    confirmPasswordError.value = 'Please confirm your password';
  } else if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = 'Passwords do not match';
  } else {
    confirmPasswordError.value = '';
  }
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

// API call function (placeholder for now)
const registerUser = async (userData: any) => {
  const response = await fetch('http://localhost:5001/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Registration failed');
  }
  
  return await response.json();
};

// Form submission
const handleSubmit = async () => {
  // Clear previous messages
  errorMessage.value = '';
  successMessage.value = '';
  
  // Validate all fields
  validateEmail();
  validatePassword();
  validateConfirmPassword();
  
  // Check if form is valid
  if (!isFormValid.value) {
    errorMessage.value = 'Please fix the errors above';
    return;
  }
  
  isLoading.value = true;
  
  try {
    const userData = {
      email: email.value,
      password: password.value,
      confirmPassword: confirmPassword.value,
    };
    
    await registerUser(userData);
    
    // Clear form first
    email.value = '';
    password.value = '';
    confirmPassword.value = '';
    
    // Clear any existing errors
    emailError.value = '';
    passwordError.value = '';
    confirmPasswordError.value = '';
    
    // Show success message
    successMessage.value = '✅ Account created successfully! Redirecting to sign in...';
    
    // Redirect to login page after 3 seconds
    setTimeout(() => {
      successMessage.value = '';
      goToLogin();
    }, 3000);
    
  } catch (error: any) {
    errorMessage.value = error.message;
  } finally {
    isLoading.value = false;
  }
};

// Navigation
const goToLogin = () => {
  // TODO: Navigate to login page when it exists
  router.push('/tabs/tab1');
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
  font-size: 3.5rem;
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
    font-size: 3rem;
  }
}
</style>