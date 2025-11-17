<template>
  <ion-button
    :expand="expand"
    :size="size"
    :color="color"
    :fill="fill"
    @click="handleClick"
    :class="buttonClass"
    :aria-label="ariaLabel"
    :disabled="disabled"
  >
    <ion-icon
      v-if="icon"
      :icon="icon"
      :slot="iconSlot"
      aria-hidden="true"
    ></ion-icon>
    <slot></slot>
  </ion-button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonButton, IonIcon } from '@ionic/vue';

/**
 * ActionButton Component
 *
 * Modern Ionic 7 button component with proper icon handling.
 * Icons must be imported from 'ionicons/icons' and passed as objects.
 *
 * @example
 * import { add } from 'ionicons/icons';
 * <ActionButton :icon="add" icon-slot="start">Add Calendar</ActionButton>
 */

// Props
interface Props {
  expand?: 'block' | 'full';
  size?: 'small' | 'default' | 'large';
  color?: string;
  fill?: 'clear' | 'outline' | 'solid';
  variant?: 'primary' | 'secondary';
  icon?: any; // Icon object from ionicons/icons (e.g., add, settings, helpCircle)
  iconSlot?: 'start' | 'end' | 'icon-only';
  ariaLabel?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  expand: 'block',
  size: 'large',
  color: 'primary',
  fill: 'solid',
  variant: 'primary',
  iconSlot: 'start',
  disabled: false
});

// Emits
const emit = defineEmits<{
  'click': [];
}>();

// Computed
const buttonClass = computed(() => `${props.variant}-button`);

// Methods
const handleClick = () => {
  if (!props.disabled) {
    emit('click');
  }
};
</script>

<style scoped>
.primary-button {
  height: 56px;
  font-weight: 700;
  font-size: 1.1rem;
  --border-radius: 12px;
  --box-shadow: 0 4px 15px rgba(var(--ion-color-primary-rgb), 0.4);
  text-transform: none;
  letter-spacing: 0.5px;
}

.primary-button:not(.button-disabled):hover {
  transform: translateY(-2px);
  --box-shadow: 0 6px 20px rgba(var(--ion-color-primary-rgb), 0.5);
}

.primary-button:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

.secondary-button {
  font-weight: 600;
  font-size: 1rem;
  text-decoration: underline;
}

.secondary-button:focus {
  outline: 2px solid var(--ion-color-medium);
  outline-offset: 2px;
}
</style>