<template>
  <!-- Mobile Action Sheet (< 768px) -->
  <ion-action-sheet
    v-if="isMobileView"
    :is-open="isOpen"
    :header="header"
    :buttons="formattedButtons"
    @didDismiss="handleDismiss"
  ></ion-action-sheet>

  <!-- Desktop Popover (>= 768px) -->
  <ion-popover
    v-else
    :is-open="isOpen"
    :event="triggerEvent"
    :dismiss-on-select="true"
    @didDismiss="handleDismiss"
  >
    <ion-content class="popover-content">
      <ion-list lines="none">
        <ion-item
          v-for="(item, index) in menuItems"
          :key="index"
          button
          @click="handleItemClick(item)"
          detail="false"
          :class="{ 'delete-item': item.role === 'destructive' }"
        >
          <ion-icon
            :icon="item.icon"
            slot="start"
            :color="item.color || (item.role === 'destructive' ? 'danger' : 'primary')"
          ></ion-icon>
          <ion-label :color="item.role === 'destructive' ? 'danger' : undefined">
            {{ item.text }}
          </ion-label>
        </ion-item>
      </ion-list>
    </ion-content>
  </ion-popover>
</template>

<script setup lang="ts">
/**
 * ContextMenu Component
 *
 * A reusable context menu component that adapts to mobile and desktop environments.
 * - Mobile (<768px): Displays as an Action Sheet (bottom drawer)
 * - Desktop (>=768px): Displays as a Popover (positioned near trigger)
 *
 * Features:
 * - Automatic responsive behavior
 * - Touch-friendly mobile interface
 * - Keyboard-accessible desktop interface
 * - Destructive action styling
 * - Icon support
 * - Customizable colors
 *
 * Usage:
 * ```vue
 * <ContextMenu
 *   :is-open="isMenuOpen"
 *   :trigger-event="menuEvent"
 *   :items="[
 *     { text: 'Edit', icon: pencilOutline, handler: handleEdit },
 *     { text: 'Delete', icon: trashOutline, handler: handleDelete, role: 'destructive' }
 *   ]"
 *   header="Calendar Options"
 *   @dismiss="isMenuOpen = false"
 * />
 * ```
 */

import { computed } from 'vue';
import { IonActionSheet, IonPopover, IonContent, IonList, IonItem, IonIcon, IonLabel } from '@ionic/vue';
import { useResponsive } from '@/composables/useResponsive';

/**
 * Menu item interface
 */
export interface ContextMenuItem {
  /** Display text for the menu item */
  text: string;
  /** Ionicon to display */
  icon: string;
  /** Handler function to execute when clicked */
  handler: () => void;
  /** Optional role ('destructive' for delete actions, 'cancel' for cancel button) */
  role?: 'destructive' | 'cancel';
  /** Optional custom color override */
  color?: string;
}

/**
 * Component props
 */
interface Props {
  /** Whether the menu is currently open */
  isOpen: boolean;
  /** Menu items to display */
  items: ContextMenuItem[];
  /** Optional header text (primarily for mobile action sheet) */
  header?: string;
  /** Trigger event for desktop popover positioning (required for desktop) */
  triggerEvent?: Event;
}

const props = defineProps<Props>();

/**
 * Component emits
 */
const emit = defineEmits<{
  /** Emitted when the menu is dismissed */
  dismiss: [];
}>();

// Use responsive composable to determine mobile vs desktop
const { isMobile } = useResponsive();
const isMobileView = computed(() => isMobile());

/**
 * Menu items for display (excludes cancel role items on desktop)
 */
const menuItems = computed(() => {
  // On desktop, we don't show cancel buttons (user can click outside)
  return props.items.filter(item => item.role !== 'cancel');
});

/**
 * Format menu items for ion-action-sheet buttons
 * Action sheet expects a different format than our menu items
 */
const formattedButtons = computed(() => {
  return props.items.map(item => ({
    text: item.text,
    icon: item.icon,
    role: item.role,
    handler: item.handler
  }));
});

/**
 * Handle menu item click (desktop popover only)
 */
const handleItemClick = (item: ContextMenuItem) => {
  item.handler();
  emit('dismiss');
};

/**
 * Handle menu dismissal
 */
const handleDismiss = () => {
  emit('dismiss');
};
</script>

<style scoped>
/* Desktop Popover Styling */
.popover-content {
  --padding-top: 0;
  --padding-bottom: 0;
  --padding-start: 0;
  --padding-end: 0;
}

.popover-content ion-list {
  padding: 0.5rem 0;
  background: transparent;
}

.popover-content ion-item {
  --padding-start: 1rem;
  --padding-end: 1rem;
  --min-height: 44px; /* NFR [U2]: Touch-friendly minimum */
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color var(--transition-base);
}

.popover-content ion-item:hover {
  --background: rgba(var(--ion-color-primary-rgb), 0.1);
}

.popover-content ion-item.delete-item:hover {
  --background: rgba(var(--ion-color-danger-rgb), 0.1);
}

.popover-content ion-icon {
  font-size: 1.25rem;
  margin-right: 0.5rem;
}

.popover-content ion-label {
  font-weight: var(--font-weight-medium);
}
</style>

<style>
/* Mobile Action Sheet Global Styles (not scoped) */
/* Better spacing and visual hierarchy for touch-friendly interaction */
ion-action-sheet.action-sheet-destructive {
  --button-background-selected: rgba(var(--ion-color-danger-rgb), 0.1);
}

/* Increase spacing between action buttons for better touch targets */
ion-action-sheet button[role="destructive"] {
  margin-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding-top: 16px !important;
  padding-bottom: 16px !important;
}

/* Dark mode support for action sheet divider */
@media (prefers-color-scheme: dark) {
  ion-action-sheet button[role="destructive"] {
    border-top-color: rgba(255, 255, 255, 0.1);
  }
}
</style>
