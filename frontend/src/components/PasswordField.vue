<template>
  <div class="form-group">
    <div class="password-field-wrapper">
      <!-- Modern ion-input with label prop -->
      <ion-input
        :label="labelWithRequired"
        label-placement="floating"
        :type="showPassword ? 'text' : 'password'"
        :value="modelValue"
        @ionInput="handleInput"
        @ionBlur="handleBlur"
        :placeholder="placeholder"
        :required="required"
        :class="{'ion-invalid': hasError, 'ion-touched': true}"
        :aria-invalid="hasError ? 'true' : 'false'"
        :aria-describedby="getAriaDescribedBy()"
        :autocomplete="autocomplete"
        fill="outline"
      ></ion-input>

      <!-- Password visibility toggle button -->
      <ion-button
        fill="clear"
        @click="togglePasswordVisibility"
        :aria-label="showPassword ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`"
        class="password-toggle"
        type="button"
      >
        <ion-icon :icon="showPassword ? eyeOffOutline : eyeOutline"></ion-icon>
      </ion-button>
    </div>

    <!-- Error message -->
    <div
      v-if="hasError"
      class="error-text"
      :id="errorId"
      role="alert"
      aria-live="polite"
    >{{ errorMessage }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { IonInput, IonButton, IonIcon } from '@ionic/vue';
import { eyeOutline, eyeOffOutline } from 'ionicons/icons';

// Props
interface Props {
  modelValue: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  errorMessage?: string;
  autocomplete?: string;
  requirementsId?: string;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '',
  required: false,
  errorMessage: '',
  autocomplete: 'new-password',
  requirementsId: ''
});

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string];
  'blur': [];
}>();

// State
const showPassword = ref(false);

// Computed
const hasError = computed(() => !!props.errorMessage);
const errorId = computed(() => `${props.label.toLowerCase().replace(/\s+/g, '-')}-error`);
const labelWithRequired = computed(() => {
  return props.required ? `${props.label} *` : props.label;
});

// Methods
const handleInput = (event: any) => {
  emit('update:modelValue', event.target.value);
};

const handleBlur = () => {
  emit('blur');
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

const getAriaDescribedBy = () => {
  const ids = [];
  if (hasError.value) ids.push(errorId.value);
  if (props.requirementsId) ids.push(props.requirementsId);
  return ids.length > 0 ? ids.join(' ') : undefined;
};
</script>

<style scoped>
/**
 * PasswordField - Modern Ionic 7 Password Input
 *
 * Migrated from legacy ion-item pattern to modern ion-input with label prop
 * Includes password visibility toggle button positioned absolutely
 *
 * NFR Compliance:
 * - [U1] Mobile responsive (320px+)
 * - [U2] Touch-friendly (44px+ button targets)
 * - [U5] WCAG 2.1 AA accessibility (ARIA labels, keyboard navigation)
 */

.form-group {
  margin-bottom: var(--spacing-lg, 24px);
  width: 100%;
}

/* Wrapper for input + toggle button */
.password-field-wrapper {
  position: relative;
  width: 100%;
}

/* Modern Ionic input with outline fill */
ion-input {
  --border-color: var(--color-border, #e9ecef);
  --border-width: 2px;
  --border-radius: var(--radius-md, 12px);
  --placeholder-color: var(--color-text-secondary, #6c757d);
  --placeholder-opacity: 0.6;
  --padding-end: 52px; /* Make room for toggle button */

  /* Prevent iOS zoom on focus (16px+ font size) */
  font-size: max(1rem, 16px);
}

/* Focus state */
ion-input:focus-within {
  --border-color: var(--color-focus, var(--ion-color-primary));
  --highlight-color-focused: var(--ion-color-primary);
}

/* Error state */
ion-input.ion-invalid.ion-touched {
  --border-color: var(--ion-color-danger);
  --highlight-color-focused: var(--ion-color-danger);
  --background: rgba(var(--ion-color-danger-rgb), 0.02);
}

/* Label styling */
ion-input::part(label) {
  color: var(--color-text-secondary, #495057);
  font-weight: var(--font-weight-semibold, 600);
  font-size: var(--font-size-sm, 0.9rem);
}

/* Focused label */
ion-input:focus-within::part(label) {
  color: var(--color-focus, var(--ion-color-primary));
}

/* Error label */
ion-input.ion-invalid.ion-touched::part(label) {
  color: var(--ion-color-danger);
}

/* Password toggle button - positioned absolutely */
.password-toggle {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  --color: var(--color-text-secondary, #6c757d);
  --padding-start: 8px;
  --padding-end: 8px;
  margin: 0;
  z-index: 10;
  min-height: 44px; /* NFR: U2 - Touch-friendly */
  min-width: 44px;
}

.password-toggle:hover {
  --color: var(--ion-color-primary);
}

.password-toggle:focus-visible {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
  border-radius: var(--radius-sm, 6px);
}

/* Error message */
.error-text {
  color: var(--ion-color-danger);
  font-size: var(--font-size-sm, 0.875rem);
  margin-top: var(--spacing-xs, 8px);
  font-weight: var(--font-weight-medium, 500);
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-xs, 6px);
  line-height: var(--line-height-normal, 1.5);
}

.error-text::before {
  content: "●";
  color: var(--ion-color-danger);
  font-size: var(--font-size-xs, 0.75rem);
  margin-top: 2px;
  flex-shrink: 0;
}

/* Accessibility: High contrast mode */
@media (prefers-contrast: high) {
  ion-input {
    --border-width: 3px;
  }

  ion-input::part(label) {
    font-weight: var(--font-weight-bold, 700);
  }

  .error-text {
    font-weight: var(--font-weight-bold, 700);
  }

  .password-toggle {
    --color: var(--color-text-primary);
  }
}

/* Accessibility: Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .form-group {
    animation: none;
  }
}

/* Animation - entrance effect */
.form-group {
  animation: formFieldEnter var(--transition-slow, 0.6s) ease-out;
}

@keyframes formFieldEnter {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover support for desktop */
@media (hover: hover) {
  ion-input:hover:not(:focus-within) {
    --border-color: var(--color-focus, var(--ion-color-primary));
  }

  ion-input.ion-invalid.ion-touched:hover {
    --border-color: var(--ion-color-danger);
  }
}
</style>