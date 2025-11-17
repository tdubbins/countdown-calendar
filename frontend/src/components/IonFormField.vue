<template>
  <div class="form-group">
    <!-- Textarea variant with character counter -->
    <ion-textarea
      v-if="type === 'textarea'"
      :label="labelWithRequired"
      label-placement="floating"
      :value="modelValue"
      @ionInput="handleInput"
      @ionBlur="handleBlur"
      @ionFocus="handleFocus"
      :placeholder="placeholder"
      :required="required"
      :maxlength="maxlength"
      :rows="rows"
      :counter="showCharCount"
      :auto-grow="true"
      :class="{'ion-invalid': hasError, 'ion-touched': true}"
      :aria-invalid="hasError ? 'true' : 'false'"
      :aria-describedby="hasError ? errorId : (showCharCount ? charCountId : undefined)"
      fill="outline"
    ></ion-textarea>

    <!-- Standard input variant -->
    <ion-input
      v-else
      :label="labelWithRequired"
      label-placement="floating"
      :type="type"
      :value="modelValue"
      @ionInput="handleInput"
      @ionBlur="handleBlur"
      @ionFocus="handleFocus"
      :placeholder="placeholder"
      :required="required"
      :maxlength="maxlength"
      :class="{'ion-invalid': hasError, 'ion-touched': true}"
      :aria-invalid="hasError ? 'true' : 'false'"
      :aria-describedby="hasError ? errorId : undefined"
      :autocomplete="autocomplete"
      fill="outline"
    ></ion-input>

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
import { IonInput, IonTextarea } from '@ionic/vue';

// Props - matches FormField.vue API for easy migration
interface Props {
  modelValue: string;
  label: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  errorMessage?: string;
  autocomplete?: string;
  maxlength?: number;
  rows?: number;
  showCharCount?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  required: false,
  errorMessage: '',
  autocomplete: 'off',
  maxlength: undefined,
  rows: 4,
  showCharCount: false
});

// Emits - matches FormField.vue API
const emit = defineEmits<{
  'update:modelValue': [value: string];
  'blur': [];
  'focus': [];
}>();

// Computed properties
const hasError = computed(() => !!props.errorMessage);
const errorId = computed(() => `${props.label.toLowerCase().replace(/\s+/g, '-')}-error`);
const charCountId = computed(() => `${props.label.toLowerCase().replace(/\s+/g, '-')}-char-count`);

// Label with required indicator
const labelWithRequired = computed(() => {
  return props.required ? `${props.label} *` : props.label;
});

// Event handlers
const handleInput = (event: any) => {
  // Ion events provide value in event.target.value or event.detail.value
  const value = event.target?.value ?? event.detail?.value ?? '';
  emit('update:modelValue', value);
};

const handleBlur = () => {
  emit('blur');
};

const handleFocus = () => {
  emit('focus');
};
</script>

<style scoped>
/**
 * IonFormField - Modern Ionic 7 Form Component
 *
 * Uses native ion-input/ion-textarea with label prop (modern pattern)
 * Replaces legacy ion-item + ion-label pattern
 *
 * Benefits:
 * - No deprecation warnings (Ionic 7+ modern API)
 * - Built-in floating labels via labelPlacement="floating"
 * - Built-in character counter for textareas
 * - Better mobile keyboard handling
 * - Consistent with Ionic design system
 *
 * NFR Compliance:
 * - [U1] Mobile responsive (320px+)
 * - [U2] Touch-friendly (44px+ targets via Ionic defaults)
 * - [U5] WCAG 2.1 AA accessibility (ARIA labels, error handling)
 */

.form-group {
  margin-bottom: var(--spacing-lg, 24px);
  width: 100%;
}

/* Modern Ionic inputs/textareas with outline fill */
ion-input,
ion-textarea {
  --border-color: var(--color-border, #e9ecef);
  --border-width: 2px;
  --border-radius: var(--radius-md, 12px);
  --placeholder-color: var(--color-text-secondary, #6c757d);
  --placeholder-opacity: 0.6;

  /* Prevent iOS zoom on focus (16px+ font size) */
  font-size: max(1rem, 16px);
}

/* Focus state */
ion-input:focus-within,
ion-textarea:focus-within {
  --border-color: var(--color-focus, var(--ion-color-primary));
  --highlight-color-focused: var(--ion-color-primary);
}

/* Error state - Ionic uses ion-invalid + ion-touched */
ion-input.ion-invalid.ion-touched,
ion-textarea.ion-invalid.ion-touched {
  --border-color: var(--ion-color-danger);
  --highlight-color-focused: var(--ion-color-danger);
  --background: rgba(var(--ion-color-danger-rgb), 0.02);
}

/* Label styling (controlled by Ionic, but we can customize) */
ion-input::part(label),
ion-textarea::part(label) {
  color: var(--color-text-secondary, #495057);
  font-weight: var(--font-weight-semibold, 600);
  font-size: var(--font-size-sm, 0.9rem);
}

/* Focused label color */
ion-input:focus-within::part(label),
ion-textarea:focus-within::part(label) {
  color: var(--color-focus, var(--ion-color-primary));
}

/* Error label color */
ion-input.ion-invalid.ion-touched::part(label),
ion-textarea.ion-invalid.ion-touched::part(label) {
  color: var(--ion-color-danger);
}

/* Error message styling - matches previous FormField.vue */
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

/* Textarea specific */
ion-textarea {
  min-height: 120px;
}

/* Accessibility: High contrast mode support */
@media (prefers-contrast: high) {
  ion-input,
  ion-textarea {
    --border-width: 3px;
  }

  ion-input::part(label),
  ion-textarea::part(label) {
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
  ion-input:hover:not(:focus-within),
  ion-textarea:hover:not(:focus-within) {
    --border-color: var(--color-focus, var(--ion-color-primary));
  }

  ion-input.ion-invalid.ion-touched:hover,
  ion-textarea.ion-invalid.ion-touched:hover {
    --border-color: var(--ion-color-danger);
  }
}
</style>
