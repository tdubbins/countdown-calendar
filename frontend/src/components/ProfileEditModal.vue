<template>
  <ion-modal :is-open="isOpen" @didDismiss="handleClose">
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Edit Profile</ion-title>
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
          <!-- Email Field -->
          <IonFormField
            v-model="formData.email"
            label="Email"
            type="email"
            placeholder="Enter your email address"
            :required="true"
            :error-message="errors.email"
            autocomplete="email"
            @blur="validateEmail"
          />

          <!-- Display Name Field -->
          <IonFormField
            v-model="formData.display_name"
            label="Display Name"
            type="text"
            placeholder="Enter your display name (optional)"
            :required="false"
            :error-message="errors.display_name"
            autocomplete="name"
            :maxlength="50"
          />

          <p class="helper-text">
            Your display name is optional and can be used instead of your email for a more personal touch.
          </p>

          <!-- Action Buttons -->
          <div class="button-group">
            <ActionButton
              type="submit"
              fill="solid"
              color="primary"
              variant="primary"
              :disabled="isSubmitting || !isFormValid"
              aria-label="Save profile changes"
            >
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </ActionButton>

            <ActionButton
              type="button"
              @click="handleClose"
              fill="outline"
              color="medium"
              variant="secondary"
              :disabled="isSubmitting"
              aria-label="Cancel profile edit"
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
import { ref, computed, watch } from 'vue';
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonButton,
} from '@ionic/vue';
import IonFormField from '@/components/IonFormField.vue';
import ActionButton from '@/components/ActionButton.vue';
import type { UserProfile } from '@/types/user';

// Props
interface Props {
  isOpen: boolean;
  profile: UserProfile | null;
  isSubmitting?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isSubmitting: false,
});

// Emits
const emit = defineEmits<{
  close: [];
  submit: [data: { email: string; display_name: string | null }];
}>();

// Form data
const formData = ref({
  email: '',
  display_name: '',
});

// Form errors
const errors = ref({
  email: '',
  display_name: '',
});

// Watch for profile changes to populate form
watch(
  () => props.profile,
  (newProfile) => {
    if (newProfile) {
      formData.value.email = newProfile.email;
      formData.value.display_name = newProfile.display_name || '';
    }
  },
  { immediate: true }
);

// Validation
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!formData.value.email) {
    errors.value.email = 'Email is required';
  } else if (!emailRegex.test(formData.value.email)) {
    errors.value.email = 'Please enter a valid email address';
  } else {
    errors.value.email = '';
  }
};

// Form validation
const isFormValid = computed(() => {
  return (
    formData.value.email &&
    !errors.value.email &&
    !errors.value.display_name
  );
});

// Handlers
const handleSubmit = () => {
  // Validate all fields before submission
  validateEmail();

  if (!isFormValid.value) {
    return;
  }

  // Emit submit event with form data
  emit('submit', {
    email: formData.value.email.trim(),
    display_name: formData.value.display_name.trim() || null,
  });
};

const handleClose = () => {
  // Reset errors when closing
  errors.value = {
    email: '',
    display_name: '',
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

.helper-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: calc(var(--spacing-sm) * -1) 0 0 0;
  padding: 0 var(--spacing-xs);
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
    min-width: 120px;
  }
}
</style>
