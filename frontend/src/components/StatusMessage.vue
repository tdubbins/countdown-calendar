<template>
  <div
    v-if="message"
    :class="['status-message', `status-message--${type}`]"
    :role="type === 'error' ? 'alert' : 'status'"
    :aria-live="type === 'error' ? 'assertive' : 'polite'"
    :aria-atomic="true"
  >
    <ion-icon :name="iconName" class="message-icon" aria-hidden="true"></ion-icon>
    <p>{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonIcon } from '@ionic/vue';

/**
 * StatusMessage Component
 *
 * Reusable component for displaying success, error, info, and warning messages.
 * Provides consistent styling and accessibility features across the application.
 *
 * Features:
 * - Automatic icon selection based on message type
 * - Proper ARIA attributes for screen readers
 * - Consistent styling with theme system
 * - Type-safe props with TypeScript
 *
 * Usage:
 * <StatusMessage
 *   type="success"
 *   message="Account created successfully!"
 * />
 */

export interface Props {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

const props = defineProps<Props>();

/**
 * Icon mapping for message types
 */
const iconName = computed(() => {
  const icons = {
    success: 'checkmark-circle',
    error: 'alert-circle',
    info: 'information-circle',
    warning: 'warning'
  };
  return icons[props.type];
});
</script>

<style scoped>
/* Base message styling */
.status-message {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid;
  margin: var(--spacing-md) 0;
  animation: slideIn 0.3s ease-out;
}

.status-message p {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: 1.5;
  flex: 1;
}

.message-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px; /* Align with text baseline */
}

/* Success variant (green) */
.status-message--success {
  background-color: rgba(var(--ion-color-success-rgb), 0.1);
  border-color: rgba(var(--ion-color-success-rgb), 0.3);
  color: var(--ion-color-success-shade);
}

.status-message--success .message-icon {
  color: var(--ion-color-success);
}

/* Error variant (red) */
.status-message--error {
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  border-color: rgba(var(--ion-color-danger-rgb), 0.3);
  color: var(--ion-color-danger-shade);
}

.status-message--error .message-icon {
  color: var(--ion-color-danger);
}

/* Info variant (blue) */
.status-message--info {
  background-color: rgba(var(--ion-color-primary-rgb), 0.1);
  border-color: rgba(var(--ion-color-primary-rgb), 0.3);
  color: var(--ion-color-primary-shade);
}

.status-message--info .message-icon {
  color: var(--ion-color-primary);
}

/* Warning variant (yellow) */
.status-message--warning {
  background-color: rgba(var(--ion-color-warning-rgb), 0.1);
  border-color: rgba(var(--ion-color-warning-rgb), 0.3);
  color: var(--ion-color-warning-shade);
}

.status-message--warning .message-icon {
  color: var(--ion-color-warning);
}

/* Slide in animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .status-message--success {
    background-color: rgba(var(--ion-color-success-rgb), 0.15);
  }

  .status-message--error {
    background-color: rgba(var(--ion-color-danger-rgb), 0.15);
  }

  .status-message--info {
    background-color: rgba(var(--ion-color-primary-rgb), 0.15);
  }

  .status-message--warning {
    background-color: rgba(var(--ion-color-warning-rgb), 0.15);
  }
}

/* Responsive design */
@media (max-width: 480px) {
  .status-message {
    padding: var(--spacing-sm);
    font-size: var(--font-size-xs);
  }

  .message-icon {
    font-size: 18px;
  }
}
</style>
