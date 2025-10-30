<template>
  <form
    @submit.prevent="handleSubmit"
    class="calendar-form"
    novalidate
    :aria-label="mode === 'edit' ? 'Edit calendar form' : 'Create new calendar form'"
  >
    <!-- Form Title -->
    <div class="form-header">
      <h2 class="form-title">{{ mode === 'edit' ? 'Edit Calendar' : 'Create Calendar' }}</h2>
    </div>

    <!-- Calendar Title Field -->
    <FormField
      v-model="formData.title"
      label="Calendar Title"
      placeholder="Christmas Countdown 2025"
      :required="true"
      :error-message="errors.title"
      autocomplete="off"
      @blur="validateTitle"
      @update:model-value="clearTitleError"
    />

    <!-- Start Date Field -->
    <FormField
      v-model="formData.startDate"
      label="Start Date"
      type="date"
      :required="true"
      :error-message="errors.startDate"
      @blur="validateStartDate"
      @update:model-value="clearStartDateError"
    />

    <!-- End Date Field -->
    <FormField
      v-model="formData.endDate"
      label="End Date"
      type="date"
      :required="true"
      :error-message="errors.endDate"
      @blur="validateEndDate"
      @update:model-value="clearEndDateError"
    />

    <!-- Calendar Summary Display -->
    <div v-if="calculatedDuration" class="calendar-summary">
      <p class="summary-text">{{ calculatedDuration }} days</p>
    </div>

    <!-- Form Actions -->
    <div class="form-actions">
      <ion-button
        type="button"
        fill="clear"
        color="medium"
        @click="handleCancel"
        size="large"
        aria-label="Cancel calendar creation"
      >
        Cancel
      </ion-button>
      
      <ion-button
        type="submit"
        :disabled="!isFormValid || isSubmitting"
        expand="block"
        size="large"
        color="primary"
        :aria-describedby="errorMessage ? 'form-error' : (successMessage ? 'form-success' : undefined)"
      >
        <ion-spinner v-if="isSubmitting" name="crescent" size="small"></ion-spinner>
        <span v-else>{{ mode === 'edit' ? 'Save Changes' : 'Create Calendar' }}</span>
      </ion-button>
    </div>

    <!-- Status Messages -->
    <div v-if="errorMessage" id="form-error" class="status-message error-message" role="alert">
      {{ errorMessage }}
    </div>
    <div v-if="successMessage" id="form-success" class="status-message success-message" role="status">
      {{ successMessage }}
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  IonButton,
  IonSpinner
} from '@ionic/vue';
import FormField from '@/components/FormField.vue';
import type { CalendarCreateData, Calendar } from '@/types/calendar';
import {
  calculateDaysBetween,
  formatCalendarSummary,
  validateDateRange,
  isDateInPast,
  CALENDAR_CONSTANTS
} from '@/utils/calendarUtils';

// Props
interface Props {
  calendar?: Calendar; // Optional calendar prop for edit mode
  initialData?: Partial<CalendarCreateData>;
  isSubmitting?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  calendar: undefined,
  initialData: () => ({}),
  isSubmitting: false
});

// Computed mode to determine if we're creating or editing
const mode = computed(() => props.calendar ? 'edit' : 'create');

// Emits
const emit = defineEmits<{
  'submit': [data: CalendarCreateData, calendarId?: string];
  'cancel': [];
}>();

// Expose reset function for parent components
const resetForm = () => {
  // Reset form data to initial empty state
  formData.value = {
    title: '',
    startDate: '',
    endDate: ''
  };
  
  // Clear all errors
  errors.value = {
    title: '',
    startDate: '',
    endDate: ''
  };
  
  // Clear status messages
  errorMessage.value = '';
  successMessage.value = '';
};

// Expose methods to parent component
defineExpose({
  resetForm
});

// Helper function to calculate end date from start date and duration
const calculateEndDate = (startDate: string, duration: number): string => {
  const start = new Date(startDate);
  const end = new Date(start);
  end.setDate(start.getDate() + duration - 1); // -1 because duration includes start day
  return end.toISOString().split('T')[0];
};

// Reactive form data (we'll calculate duration from dates)
const formData = ref({
  title: props.calendar?.title || props.initialData.title || '',
  startDate: props.calendar?.startDate || props.initialData.startDate || '',
  endDate: props.calendar ? calculateEndDate(props.calendar.startDate, props.calendar.duration) : ''
});

// Form validation errors
const errors = ref({
  title: '',
  startDate: '',
  endDate: ''
});

// Status messages (following existing auth pattern)
const errorMessage = ref('');
const successMessage = ref('');

// Computed properties using extracted utilities
const calculatedDuration = computed(() => {
  return calculateDaysBetween(formData.value.startDate, formData.value.endDate);
});

const formattedSummary = computed(() => {
  return formatCalendarSummary(formData.value.startDate, formData.value.endDate);
});

const isFormValid = computed(() => {
  return formData.value.title.trim().length >= 3 &&
         formData.value.startDate &&
         formData.value.endDate &&
         calculatedDuration.value &&
         calculatedDuration.value >= CALENDAR_CONSTANTS.MIN_DURATION_DAYS &&
         calculatedDuration.value <= CALENDAR_CONSTANTS.MAX_DURATION_DAYS &&
         !errors.value.title &&
         !errors.value.startDate &&
         !errors.value.endDate;
});

// Validation functions
const validateTitle = () => {
  const title = formData.value.title.trim();
  
  if (!title) {
    errors.value.title = 'Calendar title is required';
  } else if (title.length < 3) {
    errors.value.title = 'Title must be at least 3 characters long';
  } else if (title.length > 50) {
    errors.value.title = 'Title must be less than 50 characters';
  } else {
    errors.value.title = '';
  }
};

const validateStartDate = () => {
  const startDate = formData.value.startDate;

  if (!startDate) {
    errors.value.startDate = 'Start date is required';
  } else if (mode.value === 'create' && isDateInPast(startDate)) {
    // Only check for past dates when creating a new calendar
    errors.value.startDate = 'Start date cannot be in the past';
  } else {
    errors.value.startDate = '';
  }
};

const validateEndDate = () => {
  const endDate = formData.value.endDate;
  const startDate = formData.value.startDate;
  
  if (!endDate) {
    errors.value.endDate = 'End date is required';
  } else if (!startDate) {
    errors.value.endDate = 'Please select a start date first';
  } else {
    // Use the extracted validation utility
    const validationError = validateDateRange(
      startDate, 
      endDate, 
      CALENDAR_CONSTANTS.MAX_DURATION_DAYS
    );
    
    errors.value.endDate = validationError || '';
  }
};

// Clear error functions (following existing auth pattern)
const clearTitleError = () => {
  errors.value.title = '';
  errorMessage.value = '';
};

const clearStartDateError = () => {
  errors.value.startDate = '';
  errorMessage.value = '';
};

const clearEndDateError = () => {
  errors.value.endDate = '';
  errorMessage.value = '';
};

// Event handlers
const handleSubmit = () => {
  // Clear previous status messages
  errorMessage.value = '';
  successMessage.value = '';

  // Validate all fields before submission
  validateTitle();
  validateStartDate();
  validateEndDate();

  if (isFormValid.value && calculatedDuration.value) {
    // Create the CalendarCreateData object with calculated duration
    const submitData: CalendarCreateData = {
      title: formData.value.title,
      startDate: formData.value.startDate,
      duration: calculatedDuration.value
    };

    // Emit with calendar ID if in edit mode
    if (mode.value === 'edit' && props.calendar?.id) {
      emit('submit', submitData, props.calendar.id);
    } else {
      emit('submit', submitData);
    }
  } else {
    const action = mode.value === 'edit' ? 'saving' : 'creating';
    errorMessage.value = `Please fix the errors above before ${action} your calendar.`;
  }
};

const handleCancel = () => {
  emit('cancel');
};

// Watch for changes to trigger validation
watch(() => formData.value.title, validateTitle);
watch(() => formData.value.startDate, () => {
  validateStartDate();
  // Re-validate end date when start date changes (affects duration calculation)
  if (formData.value.endDate) {
    validateEndDate();
  }
});
watch(() => formData.value.endDate, () => {
  validateEndDate();
  // Re-validate start date when end date changes
  if (formData.value.startDate) {
    validateStartDate();
  }
});
</script>

<style scoped>
/* Lightweight responsive calendar form */
.calendar-form {
  max-width: min(28rem, 90vw);
  margin: 0 auto;
  padding: clamp(1rem, 4vw, 2rem);
  container-type: inline-size;
}

/* Form Header - Intrinsically responsive */
.form-header {
  text-align: center;
  margin-bottom: clamp(1.5rem, 6vh, 3rem);
}

.form-title {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

/* Calendar Summary - Lightweight */
.calendar-summary {
  margin: clamp(1rem, 3vh, 2rem) 0;
  text-align: center;
}

.summary-text {
  font-size: clamp(0.8rem, 2vw, 0.9rem);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin: 0;
  padding: clamp(0.5rem, 1.5vw, 1rem) clamp(0.75rem, 2vw, 1.25rem);
  background: var(--color-background);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  display: inline-block;
}

/* Form Actions - Intrinsically responsive */
.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: clamp(0.75rem, 2vw, 1rem);
  margin-top: clamp(1.5rem, 5vh, 3rem);
  justify-content: center;
}

.form-actions ion-button {
  height: clamp(3rem, 8vh, 3.5rem);
  --border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
  min-width: clamp(7rem, 25vw, 9rem);
  flex: 0 1 auto;
}

/* Container queries for micro-layouts (if supported) */
@container (max-width: 20rem) {
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions ion-button {
    min-width: 100%;
  }
}

/* Status Messages (following existing auth patterns) */
.status-message {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-align: center;
  animation: fadeIn var(--transition-base);
}

.error-message {
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  color: var(--ion-color-danger);
  border: 1px solid rgba(var(--ion-color-danger-rgb), 0.3);
}

.success-message {
  background-color: rgba(var(--ion-color-success-rgb), 0.1);
  color: var(--ion-color-success);
  border: 1px solid rgba(var(--ion-color-success-rgb), 0.3);
}

/* Accessibility and user preference support only */
@media (prefers-reduced-motion: reduce) {
  .calendar-form {
    animation: none;
  }
}

/* Animation */
.calendar-form {
  animation: fadeInUp var(--transition-slow);
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

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>