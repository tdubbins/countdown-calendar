<template>
  <button
    class="delete-button"
    :class="buttonClass"
    @click="handleClick"
    :aria-label="ariaLabel"
    :title="title"
    :disabled="isLoading"
    type="button"
  >
    <ion-icon 
      v-if="!isLoading"
      name="trash-outline" 
      aria-hidden="true"
    ></ion-icon>
    <ion-spinner 
      v-if="isLoading"
      name="crescent"
      class="delete-spinner"
    ></ion-spinner>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonIcon, IonSpinner } from '@ionic/vue';

// Props interface following existing patterns
interface Props {
  size?: 'small' | 'default' | 'large';
  variant?: 'default' | 'card' | 'minimal';
  ariaLabel?: string;
  title?: string;
  isLoading?: boolean;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'default',
  variant: 'default',
  ariaLabel: 'Delete item',
  title: 'Delete item',
  isLoading: false,
  disabled: false
});

// Emits
const emit = defineEmits<{
  'click': [];
}>();

// Computed properties following existing codebase patterns
const buttonClass = computed(() => {
  const sizeClass = `delete-button--${props.size}`;
  const variantClass = `delete-button--${props.variant}`;
  const stateClass = props.isLoading ? 'delete-button--loading' : '';
  return [sizeClass, variantClass, stateClass].filter(Boolean);
});

// Methods
const handleClick = () => {
  if (!props.disabled && !props.isLoading) {
    emit('click');
  }
};
</script>

<style scoped>
/* Base delete button styling following theme system */
.delete-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ion-color-medium);
  transition: all var(--transition-base);
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.delete-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Size variants following existing button patterns */
.delete-button--small {
  min-width: 32px;
  min-height: 32px;
  padding: var(--spacing-2xs);
}

.delete-button--default {
  min-width: 44px;  /* NFR [U2]: Accessible touch target */
  min-height: 44px; /* NFR [U2]: Accessible touch target */
}

.delete-button--large {
  min-width: 48px;
  min-height: 48px;
  padding: var(--spacing-sm);
}

/* Variant styles following StatusChip patterns */
.delete-button--default:hover {
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  color: var(--ion-color-danger);
  transform: scale(1.05);
}

.delete-button--card {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  z-index: 2;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  box-shadow: var(--shadow-sm);
}

.delete-button--card:hover {
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  color: var(--ion-color-danger);
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.delete-button--minimal {
  min-width: 28px;
  min-height: 28px;
  padding: var(--spacing-2xs);
}

.delete-button--minimal:hover {
  background-color: rgba(var(--ion-color-danger-rgb), 0.08);
  color: var(--ion-color-danger);
}

/* Focus states following ActionButton patterns */
.delete-button:focus {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  color: var(--ion-color-danger);
}

.delete-button:active {
  transform: scale(0.95);
}

/* Icon styling */
.delete-button ion-icon {
  font-size: 1.2rem;
  pointer-events: none;
}

.delete-button--small ion-icon {
  font-size: 1rem;
}

.delete-button--large ion-icon {
  font-size: 1.4rem;
}

/* Loading state */
.delete-button--loading {
  pointer-events: none;
}

.delete-spinner {
  width: 16px;
  height: 16px;
  --color: var(--ion-color-medium);
}

/* Dark theme support following existing patterns */
@media (prefers-color-scheme: dark) {
  .delete-button--card {
    background-color: rgba(0, 0, 0, 0.7);
    color: var(--ion-color-medium-tint);
  }
  
  .delete-button--card:hover {
    background-color: rgba(var(--ion-color-danger-rgb), 0.2);
    color: var(--ion-color-danger-tint);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .delete-button {
    border: 2px solid var(--color-text-primary);
  }
  
  .delete-button:hover,
  .delete-button:focus {
    background-color: var(--ion-color-danger);
    color: white;
    border-color: var(--ion-color-danger-shade);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .delete-button {
    transition: none;
  }
  
  .delete-button:hover,
  .delete-button:active {
    transform: none;
  }
}

/* Touch-friendly sizing for mobile */
@media (pointer: coarse) {
  .delete-button--default {
    min-width: 48px;
    min-height: 48px;
  }
  
  .delete-button--card {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>