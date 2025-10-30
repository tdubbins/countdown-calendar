<template>
  <form 
    @submit.prevent="handleSubmit" 
    class="calendar-form"
    novalidate
    aria-label="Create new calendar form"
  >
    <!-- Form Title -->
    <div class="form-header">
      <h2 class="form-title">Create Your Calendar</h2>
      <p class="form-description">
        Set up your custom countdown calendar with video content for each day.
      </p>
    </div>

    <!-- Calendar Title Field -->
    <div class="field-help">
      📝 Give your calendar a memorable name (3-50 characters)
    </div>
    <FormField
      v-model="formData.title"
      label="Calendar Title"
      placeholder="e.g., Christmas Countdown 2025"
      :required="true"
      :error-message="errors.title"
      autocomplete="off"
      @blur="validateTitle"
      @update:model-value="clearTitleError"
    />

    <!-- Start Date Field -->
    <div class="field-help">
      📅 When should your calendar countdown begin?
    </div>
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
    <div class="field-help">
      🏁 When should your calendar countdown end?
    </div>
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
      <ion-item class="summary-item" lines="none">
        <ion-icon name="sparkles" slot="start" class="summary-icon"></ion-icon>
        <ion-label>
          <h3>Calendar Summary</h3>
          <p>{{ formattedSummary }}</p>
        </ion-label>
      </ion-item>
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
        <span v-else>📅 Create Calendar</span>
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
  IonItem,
  IonLabel,
  IonButton,
  IonIcon,
  IonSpinner
} from '@ionic/vue';
import FormField from '@/components/FormField.vue';
import type { CalendarCreateData } from '@/types/calendar';
import {
  calculateDaysBetween,
  formatCalendarSummary,
  validateDateRange,
  isDateInPast,
  CALENDAR_CONSTANTS
} from '@/utils/calendarUtils';

// Props
interface Props {
  initialData?: Partial<CalendarCreateData>;
  isSubmitting?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({}),
  isSubmitting: false
});

// Emits
const emit = defineEmits<{
  'submit': [data: CalendarCreateData];
  'cancel': [];
}>();

// Reactive form data (we'll calculate duration from dates)
const formData = ref({
  title: props.initialData.title || '',
  startDate: props.initialData.startDate || '',
  endDate: ''
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
  } else if (isDateInPast(startDate)) {
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
    emit('submit', submitData);
  } else {
    errorMessage.value = 'Please fix the errors above before creating your calendar.';
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
/* Use theme system consistently */
.calendar-form {
  max-width: 500px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

/* Form Header */
.form-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.form-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.form-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
  margin: 0;
}

/* Field Help Text (improved placement above fields) */
.field-help {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
  margin-top: var(--spacing-lg);
  line-height: var(--line-height-normal);
  font-weight: var(--font-weight-medium);
}

/* First field help has no top margin */
.field-help:first-of-type {
  margin-top: 0;
}

/* Calendar Summary Display */
.calendar-summary {
  margin: var(--spacing-lg) 0;
}

.summary-item {
  --background: rgba(var(--ion-color-success-rgb), 0.1);
  --border-radius: var(--radius-md);
  border: 2px solid rgba(var(--ion-color-success-rgb), 0.2);
  --padding-start: var(--spacing-md);
  --padding-end: var(--spacing-md);
  --padding-top: var(--spacing-md);
  --padding-bottom: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  animation: slideInRight var(--transition-base);
}

.summary-icon {
  color: var(--ion-color-success);
  font-size: var(--font-size-xl);
}

.summary-item h3 {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.summary-item p {
  font-size: var(--font-size-base);
  color: var(--ion-color-success);
  font-weight: var(--font-weight-medium);
  margin: 0;
}

/* Form Actions (following existing auth form patterns) */
.form-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
}

.form-actions ion-button {
  height: 48px; /* Touch-friendly button height */
  --border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
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

/* Mobile optimizations */
@media (max-width: 480px) {
  .calendar-form {
    padding: var(--spacing-sm);
  }
  
  .form-title {
    font-size: var(--font-size-xl);
  }
  
  .form-actions {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}

/* Tablet improvements */
@media (min-width: 768px) {
  .calendar-form {
    padding: var(--spacing-lg);
  }
  
  .form-actions {
    justify-content: flex-end;
  }
  
  .form-actions ion-button {
    flex: 0 0 auto;
    min-width: 120px;
  }
}

/* Desktop improvements */
@media (min-width: 1024px) {
  .calendar-form {
    max-width: 600px;
    padding: var(--spacing-xl);
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