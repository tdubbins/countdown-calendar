<template>
  <div class="native-form-field">
    <!-- Native input/textarea wrapper with consistent styling -->
    <div
      class="input-container"
      :class="{'has-error': hasError, 'has-value': hasValue, 'is-focused': isFocused}"
    >
      <label
        :for="fieldId"
        class="input-label"
        :class="{'floating': hasValue || isFocused}"
      >
        {{ label }}
        <span v-if="required" aria-hidden="true"> *</span>
      </label>

      <!-- Textarea variant -->
      <textarea
        v-if="type === 'textarea'"
        :id="fieldId"
        ref="inputRef"
        :value="modelValue"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        :placeholder="placeholder"
        :required="required"
        :maxlength="maxlength"
        :rows="rows"
        :aria-invalid="hasError ? 'true' : 'false'"
        :aria-describedby="getAriaDescribedBy()"
        :autocomplete="autocomplete"
        class="native-textarea"
      ></textarea>

      <!-- Standard text input -->
      <input
        v-else
        :id="fieldId"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        :placeholder="placeholder"
        :required="required"
        :maxlength="maxlength"
        :aria-invalid="hasError ? 'true' : 'false'"
        :aria-describedby="hasError ? errorId : undefined"
        :autocomplete="autocomplete"
        class="native-input"
      />
    </div>

    <!-- Character counter for textarea -->
    <div
      v-if="type === 'textarea' && showCharCount && maxlength"
      class="char-count"
      :id="charCountId"
      aria-live="polite"
    >
      {{ characterCount }} / {{ maxlength }}
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

// Props - matches IonFormField API for easy migration
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

// Emits - matches IonFormField API
const emit = defineEmits<{
  'update:modelValue': [value: string];
  'blur': [];
  'focus': [];
}>();

// State
const inputRef = ref<HTMLInputElement | HTMLTextAreaElement | null>(null);
const isFocused = ref(false);

// Computed properties
const fieldId = computed(() => `native-field-${props.label.toLowerCase().replace(/\s+/g, '-')}`);
const hasError = computed(() => !!props.errorMessage);
const hasValue = computed(() => !!props.modelValue);
const errorId = computed(() => `${fieldId.value}-error`);
const charCountId = computed(() => `${fieldId.value}-char-count`);
const characterCount = computed(() => props.modelValue?.length || 0);

// Event handlers
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement;
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

const getAriaDescribedBy = () => {
  const ids = [];
  if (hasError.value) ids.push(errorId.value);
  if (props.type === 'textarea' && props.showCharCount) ids.push(charCountId.value);
  return ids.length > 0 ? ids.join(' ') : undefined;
};

// Expose methods for parent components
defineExpose({
  focus: () => {
    inputRef.value?.focus();
  },
  blur: () => {
    inputRef.value?.blur();
  }
});
</script>

<style scoped>
/**
 * NativeFormField - Accessible Native Input with DatePickerField Styling
 *
 * Uses native HTML input/textarea for maximum accessibility while maintaining
 * professional appearance matching DatePickerField.
 */

.native-form-field {
  margin-bottom: var(--spacing-lg, 24px);
  width: 100%;
}

/* Input container - matches DatePickerField styling */
.input-container {
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
.input-container.is-focused {
  border-color: var(--color-focus, var(--ion-color-primary));
  box-shadow: 0 0 0 3px rgba(var(--ion-color-primary-rgb), 0.1);
  background: var(--color-surface, white);
}

/* Error state */
.input-container.has-error {
  border-color: var(--ion-color-danger);
  background: rgba(var(--ion-color-danger-rgb), 0.02);
}

/* Floating label - matches DatePickerField */
.input-label {
  position: absolute;
  left: var(--spacing-md, 16px);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-base, 1rem);
  color: var(--color-text-secondary, #6c757d);
  font-weight: var(--font-weight-medium, 500);
  pointer-events: none;
  transition: all var(--transition-base, 0.3s ease);
  background: transparent;
  padding: 0;
}

/* Floating label when active */
.input-label.floating {
  top: var(--spacing-sm, 8px);
  transform: translateY(0);
  font-size: var(--font-size-xs, 0.75rem);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-secondary, #495057);
}

/* Focused label color */
.input-container.is-focused .input-label {
  color: var(--color-focus, var(--ion-color-primary));
}

/* Error label color */
.input-container.has-error .input-label {
  color: var(--ion-color-danger);
}

/* Native input styling */
.native-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: max(1rem, 16px); /* Prevent iOS zoom */
  color: var(--color-text-primary, #1a1a1a);
  outline: none;
  width: 100%;
  padding: 0;
  margin-top: var(--spacing-xs, 4px); /* Offset for floating label */
}

/* Native textarea styling */
.native-textarea {
  flex: 1;
  border: none;
  background: transparent;
  font-size: max(1rem, 16px); /* Prevent iOS zoom */
  color: var(--color-text-primary, #1a1a1a);
  outline: none;
  width: 100%;
  padding: 0;
  margin-top: var(--spacing-xs, 4px); /* Offset for floating label */
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}

/* Placeholder styling (shown when not focused and no value) */
.native-input::placeholder,
.native-textarea::placeholder {
  color: var(--placeholder-color, var(--color-text-secondary, #6c757d));
  opacity: 0;
  transition: opacity var(--transition-base, 0.3s ease);
}

.input-container.is-focused .native-input::placeholder,
.input-container.is-focused .native-textarea::placeholder {
  opacity: 0.6;
}

/* Character counter */
.char-count {
  font-size: var(--font-size-xs, 0.75rem);
  color: var(--color-text-muted, #757575);
  text-align: right;
  margin-top: var(--spacing-xs, 4px);
  margin-right: var(--spacing-xs, 4px);
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
  .input-container {
    border-width: 3px;
  }

  .input-container.is-focused {
    border-width: 3px;
  }

  .input-label {
    font-weight: var(--font-weight-bold, 700);
  }

  .error-text {
    font-weight: var(--font-weight-bold, 700);
  }
}

/* Accessibility: Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .input-container,
  .input-label,
  .native-input::placeholder,
  .native-textarea::placeholder {
    transition: none;
  }

  .native-form-field {
    animation: none;
  }
}

/* Animation - entrance effect */
.native-form-field {
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

/* Hover support for desktop */
@media (hover: hover) {
  .input-container:hover:not(.is-focused) {
    border-color: var(--color-focus, var(--ion-color-primary));
  }

  .input-container.has-error:hover {
    border-color: var(--ion-color-danger);
  }
}

/* Textarea container adjustments */
.input-container:has(.native-textarea) {
  align-items: flex-start;
  min-height: 120px;
}
</style>
