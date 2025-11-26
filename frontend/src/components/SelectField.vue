<template>
  <div class="form-group">
    <!-- Modern ion-select with label prop (Ionic 7+) -->
    <ion-select
      :label="labelWithRequired"
      label-placement="floating"
      :value="modelValue"
      @ionChange="handleSelectionChange"
      @ionBlur="handleBlur"
      :placeholder="placeholder"
      :class="{'ion-invalid': hasError, 'ion-touched': true}"
      :aria-invalid="hasError ? 'true' : 'false'"
      :aria-describedby="hasError ? errorId : undefined"
      interface="popover"
      fill="outline"
    >
      <ion-select-option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </ion-select-option>
    </ion-select>

    <!-- Error message -->
    <div
      v-if="hasError"
      class="error-text"
      :id="errorId"
      role="alert"
      aria-live="polite"
    >
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonSelect, IonSelectOption } from '@ionic/vue';

// Option interface for type safety
export interface SelectOption {
  value: any;
  label: string;
}

// Props
interface Props {
  modelValue: any;
  label: string;
  options: SelectOption[];
  placeholder?: string;
  required?: boolean;
  errorMessage?: string;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Select an option',
  required: false,
  errorMessage: ''
});

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: any];
  'blur': [];
}>();

// Computed
const hasError = computed(() => !!props.errorMessage);
const errorId = computed(() => `${props.label.toLowerCase().replace(/\s+/g, '-')}-error`);
const labelWithRequired = computed(() => {
  return props.required ? `${props.label} *` : props.label;
});

// Event handlers
const handleSelectionChange = (event: any) => {
  const value = event.detail?.value ?? event.target?.value;
  emit('update:modelValue', value);
};

const handleBlur = () => {
  emit('blur');
};
</script>

<style scoped>
/**
 * SelectField - Modern Ionic 7 Select Component
 *
 * Migrated from legacy ion-item + ion-label pattern to modern ion-select with label prop.
 * Matches IonFormField.vue styling for consistency.
 */

.form-group {
  margin-bottom: var(--spacing-lg, 24px);
  width: 100%;
}

/* Modern Ionic select with outline fill */
ion-select {
  --border-color: var(--color-border, #e9ecef);
  --border-width: 2px;
  --border-radius: var(--radius-md, 12px);
  --placeholder-color: var(--color-text-secondary, #6c757d);
  --placeholder-opacity: 0.6;

  /* Prevent iOS zoom on focus (16px+ font size) */
  font-size: max(1rem, 16px);
  min-height: 56px; /* Touch-friendly target size */
}

/* Focus state */
ion-select:focus-within {
  --border-color: var(--color-focus, var(--ion-color-primary));
  --highlight-color-focused: var(--ion-color-primary);
}

/* Error state - Ionic uses ion-invalid + ion-touched */
ion-select.ion-invalid.ion-touched {
  --border-color: var(--ion-color-danger);
  --highlight-color-focused: var(--ion-color-danger);
  --background: rgba(var(--ion-color-danger-rgb), 0.02);
}

/* Label styling (controlled by Ionic, but we can customize) */
ion-select::part(label) {
  color: var(--color-text-secondary, #495057);
  font-weight: var(--font-weight-semibold, 600);
  font-size: var(--font-size-sm, 0.9rem);
}

/* Focused label color */
ion-select:focus-within::part(label) {
  color: var(--color-focus, var(--ion-color-primary));
}

/* Error label color */
ion-select.ion-invalid.ion-touched::part(label) {
  color: var(--ion-color-danger);
}

/* Error message styling - matches IonFormField.vue */
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

/* Accessibility: High contrast mode support */
@media (prefers-contrast: high) {
  ion-select {
    --border-width: 3px;
  }

  ion-select::part(label) {
    font-weight: var(--font-weight-bold, 700);
  }

  .error-text {
    font-weight: var(--font-weight-bold, 700);
  }
}

/* Accessibility: Reduced motion support */
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
  ion-select:hover:not(:focus-within) {
    --border-color: var(--color-focus, var(--ion-color-primary));
  }

  ion-select.ion-invalid.ion-touched:hover {
    --border-color: var(--ion-color-danger);
  }
}
</style>