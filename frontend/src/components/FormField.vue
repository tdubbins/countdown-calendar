<template>
  <div class="form-field">
    <div 
      class="input-container" 
      :class="{ 
        'has-error': hasError, 
        'is-focused': isFocused,
        'has-value': hasValue 
      }"
    >
      <input
        :id="fieldId"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        :placeholder="isFocused && type !== 'date' ? placeholder : ''"
        :required="required"
        :aria-invalid="hasError ? 'true' : 'false'"
        :aria-describedby="hasError ? errorId : undefined"
        :autocomplete="autocomplete"
        class="form-input"
      />
      <label 
        :for="fieldId" 
        class="form-label"
        :class="{ 'floating': isFocused || hasValue }"
      >
        {{ label }}{{ required ? ' *' : '' }}
      </label>
    </div>
    
    <div 
      v-if="hasError" 
      class="error-message"
      :id="errorId"
      role="alert"
      aria-live="polite"
    >
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue';

// Props
interface Props {
  modelValue: string;
  label: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  errorMessage?: string;
  autocomplete?: string;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  required: false,
  errorMessage: '',
  autocomplete: 'off'
});

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string];
  'blur': [];
  'focus': [];
}>();

// Reactive state
const isFocused = ref(false);
const inputRef = ref<HTMLInputElement>();

// Computed properties following design system patterns
const hasError = computed(() => !!props.errorMessage);
const hasValue = computed(() => {
  // For date inputs, check if there's actually a date value, not just whitespace
  if (props.type === 'date') {
    return !!props.modelValue && props.modelValue.trim() !== '';
  }
  return !!props.modelValue;
});
const fieldId = computed(() => `field-${props.label.toLowerCase().replace(/\s+/g, '-')}`);
const errorId = computed(() => `${fieldId.value}-error`);

// Methods for unified form behavior
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
};

const handleFocus = async () => {
  isFocused.value = true;
  emit('focus');
  
  // Ensure input is focused for accessibility
  await nextTick();
  inputRef.value?.focus();
};

const handleBlur = () => {
  isFocused.value = false;
  emit('blur');
};

// Expose focus method for parent components
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur()
});
</script>

<style scoped>
/* Unified minimalistic form field using theme system */
.form-field {
  margin-bottom: var(--spacing-lg);
  width: 100%;
}

/* Input container with modern floating label design */
.input-container {
  position: relative;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  min-height: 56px; /* NFR [U2]: Touch-friendly targets 44px+ */
  display: flex;
  align-items: center;
}

/* Focus state with professional highlight */
.input-container.is-focused {
  border-color: var(--color-focus);
  box-shadow: 0 0 0 3px rgba(var(--ion-color-primary-rgb), 0.1);
  background: var(--color-surface);
}

/* Error state styling */
.input-container.has-error {
  border-color: var(--ion-color-danger);
  background: rgba(var(--ion-color-danger-rgb), 0.02);
}

/* Input field styling */
.form-input {
  width: 100%;
  padding: var(--spacing-lg) var(--spacing-md);
  padding-top: calc(var(--spacing-lg) + var(--spacing-sm)); /* Space for floating label */
  border: none;
  background: transparent;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-primary);
  line-height: var(--line-height-normal);
  outline: none;
}

/* Hide date input placeholders for clean floating label appearance */
.form-input[type="date"]:not(:focus):not(.has-value) {
  color: transparent;
}

.form-input[type="date"]:focus {
  color: var(--color-text-primary);
}

/* Ensure date inputs show content when they have a value */
.input-container.has-value .form-input[type="date"] {
  color: var(--color-text-primary);
}

/* Modern floating label */
.form-label {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--transition-base);
  pointer-events: none;
  background: var(--color-surface);
  padding: 0 var(--spacing-xs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: calc(100% - var(--spacing-lg));
}

/* Floating label animation */
.form-label.floating {
  top: 0;
  transform: translateY(-50%);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-focus);
}

/* Error label color */
.input-container.has-error .form-label {
  color: var(--ion-color-danger);
}

/* Error message styling */
.error-message {
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--ion-color-danger);
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-xs);
  line-height: var(--line-height-normal);
}

.error-message::before {
  content: "●";
  color: var(--ion-color-danger);
  font-size: var(--font-size-xs);
  margin-top: 2px;
  flex-shrink: 0;
}

/* Intrinsic responsive design using CSS custom properties */
.input-container {
  --field-padding-x: clamp(0.75rem, 2vw, 1.5rem);
  --field-padding-y: clamp(0.75rem, 1.5vh, 1.25rem);
  --field-min-height: clamp(3.5rem, 8vh, 4rem);
  --label-offset: clamp(0.75rem, 2vw, 1.5rem);
  
  min-height: var(--field-min-height);
}

.form-input {
  padding: calc(var(--field-padding-y) + 0.5rem) var(--field-padding-x) var(--field-padding-y);
  font-size: clamp(1rem, 2.5vw, 1.125rem); /* Prevents iOS zoom naturally */
}

.form-label {
  left: var(--label-offset);
  font-size: clamp(0.875rem, 2vw, 1rem);
  padding: 0 clamp(0.25rem, 0.5vw, 0.5rem);
}

.form-label.floating {
  font-size: clamp(0.75rem, 1.5vw, 0.875rem);
}

.error-message {
  font-size: clamp(0.8rem, 1.8vw, 0.875rem);
}

/* Accessibility and preference-based adaptations */
@media (prefers-contrast: high) {
  .input-container {
    border-width: 3px;
    border-color: var(--color-text-primary);
  }
  
  .input-container.is-focused {
    border-color: var(--color-focus);
    box-shadow: 0 0 0 2px var(--color-focus);
  }
  
  .form-label,
  .error-message {
    font-weight: var(--font-weight-bold);
  }
}

@media (prefers-reduced-motion: reduce) {
  .input-container,
  .form-label {
    transition: none;
  }
}

@media (hover: hover) {
  .input-container:hover {
    border-color: var(--color-focus);
    background: var(--color-surface);
  }
  
  .input-container.has-error:hover {
    border-color: var(--ion-color-danger);
  }
}

/* Focus improvements for accessibility */
.form-input:focus {
  outline: none; /* Handled by container border */
}

.form-input:focus + .form-label {
  color: var(--color-focus);
}

/* Animation entrance effect */
.form-field {
  animation: formFieldEnter var(--transition-slow) ease-out;
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
</style>