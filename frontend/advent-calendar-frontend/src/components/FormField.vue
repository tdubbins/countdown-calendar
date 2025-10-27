<template>
  <div class="form-group">
    <ion-item 
      :class="{'ion-invalid': hasError, 'form-item': true}" 
      lines="none"
    >
      <ion-label position="stacked" class="form-label">
        {{ label }}
        <span v-if="required" aria-hidden="true">*</span>
      </ion-label>
      <ion-input
        :type="type"
        :value="modelValue"
        @ion-input="handleInput"
        @ion-blur="handleBlur"
        :placeholder="placeholder"
        :required="required"
        class="form-input"
        :aria-invalid="hasError ? 'true' : 'false'"
        :aria-describedby="hasError ? errorId : undefined"
        :autocomplete="autocomplete"
      ></ion-input>
    </ion-item>
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
import { computed } from 'vue';
import { IonItem, IonLabel, IonInput } from '@ionic/vue';

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
}>();

// Computed
const hasError = computed(() => !!props.errorMessage);
const errorId = computed(() => `${props.label.toLowerCase().replace(/\s+/g, '-')}-error`);

// Methods
const handleInput = (event: any) => {
  emit('update:modelValue', event.target.value);
};

const handleBlur = () => {
  emit('blur');
};
</script>

<style scoped>
.form-group {
  margin-bottom: 24px;
}

.form-item {
  --background: #f8f9fa;
  --border-radius: 12px;
  --padding-start: 16px;
  --padding-end: 16px;
  --padding-top: 16px;
  --padding-bottom: 16px;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.form-item:focus-within {
  --background: white;
  border-color: var(--ion-color-primary);
  box-shadow: 0 0 0 3px rgba(var(--ion-color-primary-rgb), 0.2);
  outline: 2px solid transparent;
}

.form-item.ion-invalid {
  border-color: var(--ion-color-danger);
  --background: #fff5f5;
}

.form-label {
  --color: #495057;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.form-input {
  --color: #212529;
  font-size: 1rem;
}

.form-input:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

.error-text {
  color: var(--ion-color-danger);
  font-size: 0.875rem;
  margin-top: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.error-text::before {
  content: "⚠️";
  font-size: 0.8rem;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .form-item {
    border-width: 3px;
  }
  
  .form-item:focus-within {
    border-width: 4px;
  }
  
  .error-text {
    font-weight: 700;
  }
}

/* Animation */
.form-item {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>