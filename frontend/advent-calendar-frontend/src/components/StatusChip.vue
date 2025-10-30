<template>
  <span 
    class="status-chip" 
    :class="chipClass"
    :aria-label="`Status: ${status}`"
    role="status"
  >
    {{ displayText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

// Props
interface Props {
  status: 'draft' | 'active' | 'completed';
  variant?: 'default' | 'minimal';
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default'
});

// Computed properties following existing codebase patterns
const chipClass = computed(() => {
  const baseClass = `status-chip--${props.status}`;
  const variantClass = `status-chip--${props.variant}`;
  return [baseClass, variantClass];
});

const displayText = computed(() => {
  switch (props.status) {
    case 'draft': return 'Draft';
    case 'active': return 'Active';
    case 'completed': return 'Complete';
    default: return props.status;
  }
});
</script>

<style scoped>
/* Base status chip styling using theme system */
.status-chip {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-tight);
  transition: all var(--transition-fast);
  text-transform: capitalize;
  white-space: nowrap;
  letter-spacing: 0.025em;
}

/* Status-specific colors following professional design patterns */
.status-chip--draft {
  background-color: rgba(var(--ion-color-medium-rgb), 0.1);
  color: var(--ion-color-medium-shade);
  border: 1px solid rgba(var(--ion-color-medium-rgb), 0.2);
}

.status-chip--active {
  background-color: rgba(var(--ion-color-primary-rgb), 0.1);
  color: var(--ion-color-primary-shade);
  border: 1px solid rgba(var(--ion-color-primary-rgb), 0.2);
}

.status-chip--completed {
  background-color: rgba(var(--ion-color-success-rgb), 0.1);
  color: var(--ion-color-success-shade);
  border: 1px solid rgba(var(--ion-color-success-rgb), 0.2);
}

/* Minimal variant for smaller contexts */
.status-chip--minimal {
  padding: 2px var(--spacing-xs);
  font-size: 0.6875rem; /* 11px */
  font-weight: var(--font-weight-semibold);
}

/* Hover effects for interactive contexts */
.status-chip:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .status-chip--draft {
    background-color: rgba(var(--ion-color-medium-rgb), 0.2);
    color: var(--ion-color-medium-tint);
  }
  
  .status-chip--active {
    background-color: rgba(var(--ion-color-primary-rgb), 0.2);
    color: var(--ion-color-primary-tint);
  }
  
  .status-chip--completed {
    background-color: rgba(var(--ion-color-success-rgb), 0.2);
    color: var(--ion-color-success-tint);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .status-chip {
    border-width: 2px;
    font-weight: var(--font-weight-bold);
  }
  
  .status-chip--draft {
    background-color: var(--ion-color-medium);
    color: white;
    border-color: var(--ion-color-medium-shade);
  }
  
  .status-chip--active {
    background-color: var(--ion-color-primary);
    color: white;
    border-color: var(--ion-color-primary-shade);
  }
  
  .status-chip--completed {
    background-color: var(--ion-color-success);
    color: white;
    border-color: var(--ion-color-success-shade);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .status-chip {
    transition: none;
  }
  
  .status-chip:hover {
    transform: none;
  }
}

/* Touch-friendly sizing for mobile */
@media (pointer: coarse) {
  .status-chip {
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: var(--font-size-sm);
    min-height: 24px; /* Ensure adequate touch target */
  }
}
</style>