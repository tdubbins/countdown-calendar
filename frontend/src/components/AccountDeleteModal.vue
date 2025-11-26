<template>
  <ion-modal :is-open="isOpen" @didDismiss="handleClose">
    <ion-header>
      <ion-toolbar color="danger">
        <ion-title>Delete Account</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleClose" color="light">
            <strong>Close</strong>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="modal-content">
      <div class="form-container">
        <!-- Danger Warning -->
        <div class="danger-warning">
          <ion-icon :icon="warningOutline" class="warning-icon"></ion-icon>
          <h2>Permanently Delete Account?</h2>
          <p class="warning-text">
            This action <strong>cannot be undone</strong>. All your data will be permanently deleted.
          </p>
        </div>

        <!-- What Will Be Deleted -->
        <div class="deletion-details">
          <h3>The following will be permanently deleted:</h3>
          <ul>
            <li>
              <ion-icon :icon="personOutline"></ion-icon>
              Your account and profile information
            </li>
            <li>
              <ion-icon :icon="calendarOutline"></ion-icon>
              All {{ calendarCount }} calendar{{ calendarCount !== 1 ? 's' : '' }}
            </li>
            <li>
              <ion-icon :icon="videocamOutline"></ion-icon>
              All uploaded videos and media files
            </li>
            <li>
              <ion-icon :icon="documentsOutline"></ion-icon>
              All calendar metadata and settings
            </li>
          </ul>
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Password Confirmation -->
          <div class="password-section">
            <p class="password-instruction">
              Enter your password to confirm account deletion:
            </p>
            <PasswordField
              v-model="password"
              label="Password"
              placeholder="Enter your password"
              :required="true"
              :error-message="errorMessage"
              autocomplete="current-password"
            />
          </div>

          <!-- Action Buttons -->
          <div class="button-group">
            <ActionButton
              type="submit"
              fill="solid"
              color="danger"
              variant="primary"
              :disabled="!password || isSubmitting"
              aria-label="Confirm account deletion"
            >
              {{ isSubmitting ? 'Deleting Account...' : 'Delete Account Permanently' }}
            </ActionButton>

            <ActionButton
              type="button"
              @click="handleClose"
              fill="outline"
              color="medium"
              variant="secondary"
              :disabled="isSubmitting"
              aria-label="Cancel account deletion"
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
import { ref } from 'vue';
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
import {
  warningOutline,
  personOutline,
  calendarOutline,
  videocamOutline,
  documentsOutline,
} from 'ionicons/icons';
import PasswordField from '@/components/PasswordField.vue';
import ActionButton from '@/components/ActionButton.vue';

// Props
interface Props {
  isOpen: boolean;
  calendarCount?: number;
  isSubmitting?: boolean;
}

withDefaults(defineProps<Props>(), {
  calendarCount: 0,
  isSubmitting: false,
});

// Emits
const emit = defineEmits<{
  close: [];
  submit: [password: string];
}>();

// Form data
const password = ref('');
const errorMessage = ref('');

// Handlers
const handleSubmit = () => {
  if (!password.value) {
    errorMessage.value = 'Password is required';
    return;
  }

  errorMessage.value = '';
  emit('submit', password.value);
};

const handleClose = () => {
  // Reset form when closing
  password.value = '';
  errorMessage.value = '';
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

/* Danger Warning */
.danger-warning {
  background: rgba(var(--ion-color-danger-rgb), 0.1);
  border: 2px solid var(--ion-color-danger);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.warning-icon {
  font-size: 64px;
  color: var(--ion-color-danger);
  margin-bottom: var(--spacing-sm);
}

.danger-warning h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--ion-color-danger);
  margin: 0 0 var(--spacing-sm) 0;
}

.warning-text {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.5;
}

.warning-text strong {
  color: var(--ion-color-danger);
  font-weight: var(--font-weight-bold);
}

/* Deletion Details */
.deletion-details {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.deletion-details h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.deletion-details ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.deletion-details li {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.deletion-details li ion-icon {
  font-size: 20px;
  color: var(--ion-color-danger);
  flex-shrink: 0;
}

/* Password Section */
.password-section {
  margin-bottom: var(--spacing-lg);
}

.password-instruction {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

/* Button Group */
.button-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-xl);
}

@media (min-width: 768px) {
  .button-group {
    flex-direction: row-reverse;
    justify-content: flex-start;
  }

  .button-group > * {
    min-width: 200px;
  }
}
</style>
