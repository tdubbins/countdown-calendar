<template>
  <ion-modal :is-open="isOpen" @didDismiss="handleClose">
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Change Password</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleClose" color="light">
            <strong>Close</strong>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="modal-content">
      <div class="form-container">
        <form @submit.prevent="handleSubmit">
          <!-- Current Password Field -->
          <PasswordField
            v-model="formData.currentPassword"
            label="Current Password"
            placeholder="Enter your current password"
            :required="true"
            :error-message="errors.currentPassword"
            autocomplete="current-password"
            @blur="validateCurrentPassword"
          />

          <!-- New Password Field -->
          <PasswordField
            v-model="formData.newPassword"
            label="New Password"
            placeholder="Enter your new password"
            :required="true"
            :error-message="errors.newPassword"
            autocomplete="new-password"
            requirements-id="password-requirements"
            @blur="validateNewPassword"
          />

          <!-- Password Requirements (replaces custom strength bar) -->
          <PasswordRequirements
            ref="passwordRequirementsRef"
            :password="formData.newPassword"
          />

          <!-- Confirm New Password Field -->
          <PasswordField
            v-model="formData.confirmPassword"
            label="Confirm New Password"
            placeholder="Confirm your new password"
            :required="true"
            :error-message="errors.confirmPassword"
            autocomplete="new-password"
            @blur="validateConfirmPassword"
          />

          <!-- Security Notice -->
          <div class="security-notice">
            <ion-icon :icon="informationCircle" color="primary"></ion-icon>
            <p>
              For your security, you will be logged out after changing your password.
              You will need to log in again with your new password.
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="button-group">
            <ActionButton
              type="submit"
              fill="solid"
              color="primary"
              variant="primary"
              :disabled="isSubmitting || !isFormValid"
              aria-label="Change password"
            >
              {{ isSubmitting ? 'Changing Password...' : 'Change Password' }}
            </ActionButton>

            <ActionButton
              type="button"
              @click="handleClose"
              fill="outline"
              color="medium"
              variant="secondary"
              :disabled="isSubmitting"
              aria-label="Cancel password change"
            >
              Cancel
            </ActionButton>
          </div>
        </form>
      </div>
    </ion-content>
  </ion-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonButton,
  IonIcon,
} from '@ionic/vue';
import { informationCircle } from 'ionicons/icons';
import PasswordField from '@/components/PasswordField.vue';
import PasswordRequirements from '@/components/PasswordRequirements.vue';
import ActionButton from '@/components/ActionButton.vue';

// Props
interface Props {
  isOpen: boolean;
  isSubmitting?: boolean;
}

withDefaults(defineProps<Props>(), {
  isSubmitting: false,
});

// Emits
const emit = defineEmits<{
  close: [];
  submit: [data: { currentPassword: string; newPassword: string; confirmPassword: string }];
}>();

// Form data
const formData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// Form errors
const errors = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// Reference to PasswordRequirements component
const passwordRequirementsRef = ref<InstanceType<typeof PasswordRequirements> | null>(null);

// Validation functions
const validateCurrentPassword = () => {
  if (!formData.value.currentPassword) {
    errors.value.currentPassword = 'Current password is required';
  } else {
    errors.value.currentPassword = '';
  }
};

const validateNewPassword = () => {
  const password = formData.value.newPassword;

  if (!password) {
    errors.value.newPassword = 'New password is required';
  } else if (passwordRequirementsRef.value && !passwordRequirementsRef.value.isValid) {
    errors.value.newPassword = 'Please meet all password requirements';
  } else {
    errors.value.newPassword = '';
  }

  // Re-validate confirm password if it's already filled
  if (formData.value.confirmPassword) {
    validateConfirmPassword();
  }
};

const validateConfirmPassword = () => {
  if (!formData.value.confirmPassword) {
    errors.value.confirmPassword = 'Please confirm your new password';
  } else if (formData.value.confirmPassword !== formData.value.newPassword) {
    errors.value.confirmPassword = 'Passwords do not match';
  } else {
    errors.value.confirmPassword = '';
  }
};

// Form validation
const isFormValid = computed(() => {
  return (
    formData.value.currentPassword &&
    formData.value.newPassword &&
    formData.value.confirmPassword &&
    !errors.value.currentPassword &&
    !errors.value.newPassword &&
    !errors.value.confirmPassword
  );
});

// Handlers
const handleSubmit = () => {
  // Validate all fields before submission
  validateCurrentPassword();
  validateNewPassword();
  validateConfirmPassword();

  if (!isFormValid.value) {
    return;
  }

  // Emit submit event with form data
  emit('submit', {
    currentPassword: formData.value.currentPassword,
    newPassword: formData.value.newPassword,
    confirmPassword: formData.value.confirmPassword,
  });
};

const handleClose = () => {
  // Reset form and errors when closing
  formData.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  };
  errors.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  };
  emit('close');
};
</script>

<style scoped>
.modal-content {
  --padding-top: var(--spacing-md);
  --padding-bottom: var(--spacing-md);
  --padding-start: var(--spacing-md);
  --padding-end: var(--spacing-md);
}

.form-container {
  max-width: 500px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* Security Notice */
.security-notice {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background-color: rgba(var(--ion-color-primary-rgb), 0.1);
  border: 1px solid rgba(var(--ion-color-primary-rgb), 0.3);
  border-radius: var(--radius-md);
  margin-top: var(--spacing-sm);
}

.security-notice ion-icon {
  flex-shrink: 0;
  font-size: 20px;
  margin-top: 2px;
}

.security-notice p {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

@media (min-width: 768px) {
  .button-group {
    flex-direction: row;
    justify-content: flex-end;
  }

  .button-group > * {
    min-width: 160px;
  }
}
</style>
