<template>
  <div class="date-picker-field">
    <!-- Native date input wrapper with Ionic styling -->
    <div
      class="date-input-container"
      :class="{'has-error': hasError, 'has-value': hasValue}"
    >
      <label
        :for="fieldId"
        class="date-label"
        :class="{'floating': hasValue || isFocused}"
      >
        {{ label }}
        <span v-if="required" aria-hidden="true"> *</span>
      </label>

      <!-- Native HTML date input (fully accessible) -->
      <input
        :id="fieldId"
        ref="dateInputRef"
        type="date"
        :value="modelValue"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @click="handleClick"
        :required="required"
        :min="min"
        :max="max"
        :aria-invalid="hasError ? 'true' : 'false'"
        :aria-describedby="hasError ? errorId : undefined"
        class="date-input"
      />

      <ion-icon
        :icon="calendarOutline"
        class="calendar-icon"
        aria-hidden="true"
      ></ion-icon>
    </div>

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
import { ref, computed } from 'vue';
import { IonIcon } from '@ionic/vue';
import { calendarOutline } from 'ionicons/icons';

// Props - matches IonFormField API for consistency
interface Props {
  modelValue: string; // ISO date string (YYYY-MM-DD)
  label: string;
  required?: boolean;
  errorMessage?: string;
  min?: string; // Minimum date (ISO format)
  max?: string; // Maximum date (ISO format)
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  errorMessage: '',
  min: undefined,
  max: undefined
});

// Emits - matches IonFormField API
const emit = defineEmits<{
  'update:modelValue': [value: string];
  'blur': [];
  'focus': [];
}>();

// State
const dateInputRef = ref<HTMLInputElement>();
const isFocused = ref(false);

// Computed properties
const hasError = computed(() => !!props.errorMessage);
const hasValue = computed(() => !!props.modelValue);
const fieldId = computed(() => `date-${props.label.toLowerCase().replace(/\s+/g, '-')}`);
const errorId = computed(() => `${fieldId.value}-error`);

// Methods
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
};

const handleFocus = () => {
  isFocused.value = true;
  emit('focus');
};

const handleBlur = () => {
  isFocused.value = false;
  emit('blur');
};

const handleClick = () => {
  // Ensure the native picker opens on click
  // Most browsers will automatically show the picker when clicking the input
  // This handler exists for any browser-specific behavior we might need
  if (dateInputRef.value) {
    try {
      // Try to show the picker if the browser supports it
      (dateInputRef.value as any).showPicker?.();
    } catch {
      // Fallback: the default click behavior will open the picker
    }
  }
};

// Expose focus method for parent components
defineExpose({
  focus: () => {
    dateInputRef.value?.focus();
  },
  blur: () => {
    dateInputRef.value?.blur();
  }
});
</script>

<style scoped>
/**
 * DatePickerField - Accessible Native Date Input with Ionic Styling
 *
 * Uses native HTML date input for maximum accessibility while maintaining
 * professional Ionic appearance.
 *
 * Accessibility First:
 * - Native date input (screen reader compatible)
 * - Keyboard accessible (Tab, Enter, Arrow keys work)
 * - ARIA labels and error announcements
 * - Floating label for clear context
 *
 * Benefits:
 * - Full keyboard navigation support
 * - Screen reader compatible
 * - Native date pickers (platform-specific)
 * - Min/max constraints enforced by browser
 * - WCAG 2.1 AA compliant
 *
 */

.date-picker-field {
  margin-bottom: var(--spacing-lg, 24px);
  width: 100%;
}

/* Date input container - matches IonFormField styling */
.date-input-container {
  position: relative;
  background: var(--color-surface, #ffffff);
  border: 2px solid var(--color-border, #e9ecef);
  border-radius: var(--radius-md, 12px);
  transition: all var(--transition-base, 0.3s ease);
  min-height: 56px;
  display: flex;
  align-items: center;
  padding: var(--spacing-md, 16px);
  padding-top: calc(var(--spacing-lg, 24px) + var(--spacing-xs, 8px)); /* Space for floating label */
}

/* Focus state */
.date-input-container:focus-within {
  border-color: var(--color-focus, var(--ion-color-primary));
  box-shadow: 0 0 0 3px rgba(var(--ion-color-primary-rgb), 0.1);
  background: var(--color-surface, white);
}

/* Error state */
.date-input-container.has-error {
  border-color: var(--ion-color-danger);
  background: rgba(var(--ion-color-danger-rgb), 0.02);
}

/* Floating label - matches IonFormField */
.date-label {
  position: absolute;
  left: var(--spacing-md, 16px);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-base, 1rem);
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-text-secondary, #6c757d);
  transition: all var(--transition-base, 0.3s ease);
  pointer-events: none;
  background: var(--color-surface, white);
  padding: 0 var(--spacing-xs, 4px);
  white-space: nowrap;
}

/* Floating label animation */
.date-label.floating {
  top: 0;
  transform: translateY(-50%);
  font-size: var(--font-size-sm, 0.875rem);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-focus, var(--ion-color-primary));
}

/* Error label color */
.date-input-container.has-error .date-label {
  color: var(--ion-color-danger);
}

/* Focus label color */
.date-input-container:focus-within .date-label {
  color: var(--color-focus, var(--ion-color-primary));
}

/* Native date input */
.date-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: max(1rem, 16px); /* Prevent iOS zoom */
  font-weight: var(--font-weight-normal, 400);
  color: var(--color-text-primary, #212529);
  outline: none;
  cursor: pointer;
  width: 100%;
  min-height: 24px;
}

/* Hide date input placeholder/empty state for clean floating label */
.date-input:not(:focus):not(.has-value) {
  color: transparent;
}

.date-input::-webkit-calendar-picker-indicator {
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
}

.date-input-container.has-value .date-input {
  color: var(--color-text-primary, #212529);
}

.date-input:focus {
  color: var(--color-text-primary, #212529);
}

/* Calendar icon */
.calendar-icon {
  color: var(--color-text-secondary, #6c757d);
  font-size: 1.25rem;
  flex-shrink: 0;
  pointer-events: none;
  margin-left: var(--spacing-xs, 8px);
}

.date-input-container:focus-within .calendar-icon {
  color: var(--color-focus, var(--ion-color-primary));
}

/* Error message styling */
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
  .date-input-container {
    border-width: 3px;
  }

  .date-input-container:focus-within {
    border-width: 3px;
    box-shadow: 0 0 0 2px var(--color-focus);
  }

  .date-label,
  .error-text {
    font-weight: var(--font-weight-bold, 700);
  }
}

/* Accessibility: Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .date-input-container,
  .date-label {
    transition: none;
  }

  .date-picker-field {
    animation: none;
  }
}

/* Hover support for desktop */
@media (hover: hover) {
  .date-input-container:hover:not(:focus-within) {
    border-color: var(--color-focus, var(--ion-color-primary));
  }

  .date-input-container.has-error:hover {
    border-color: var(--ion-color-danger);
  }
}

/* Animation - entrance effect */
.date-picker-field {
  animation: fadeInUp var(--transition-slow, 0.6s) ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
