<template>
  <div
    class="calendar-card"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    tabindex="0"
    role="button"
    :aria-label="`Open calendar ${calendar.title}. ${videoProgress}. Status: ${calendar.status}`"
  >
    <!-- Action Button - Top-right corner -->
    <!-- Draft (not shared): Three dots menu with Edit + Delete -->
    <!-- Active (shared): Only trash bin icon for delete -->
    <ion-button
      v-if="!isShared"
      @click.stop="openContextMenu"
      ref="contextMenuTrigger"
      class="context-menu-button"
      fill="clear"
      size="small"
      :aria-label="`Options for ${calendar.title}`"
    >
      <ion-icon slot="icon-only" :icon="ellipsisVertical"></ion-icon>
    </ion-button>

    <!-- Shared calendars: Direct delete button (no edit option) -->
    <ion-button
      v-else
      @click.stop="showDeleteConfirmation"
      class="context-menu-button delete-button"
      fill="clear"
      size="small"
      :aria-label="`Delete ${calendar.title}`"
    >
      <ion-icon slot="icon-only" :icon="trashOutline" color="danger"></ion-icon>
    </ion-button>
    
    <div class="calendar-header">
      <h3 class="calendar-title">{{ calendar.title }}</h3>
      <StatusChip 
        :status="calendar.status" 
        variant="minimal"
        class="calendar-status-chip"
      />
    </div>
    
    <p class="calendar-dates">{{ formattedDateRange }}</p>
    
    <div class="calendar-progress">
      <span class="progress-text">{{ videoProgress }}</span>
    </div>
  </div>

  <!-- Context Menu - Using reusable ContextMenu component -->
  <ContextMenu
    :is-open="isContextMenuOpen"
    :trigger-event="popoverEvent"
    :items="contextMenuItems"
    :header="`${calendar.title} Options`"
    @dismiss="closeContextMenu"
  />

  <!-- Delete Confirmation Dialog -->
  <ion-alert
    :is-open="isDeleteDialogOpen"
    :header="'⚠️ Delete Calendar'"
    :subHeader="calendar.title"
    :message="deleteConfirmationMessage"
    :buttons="[
      {
        text: 'Cancel',
        role: 'cancel',
        handler: () => {
          isDeleteDialogOpen = false;
        }
      },
      {
        text: 'Delete',
        role: 'destructive',
        cssClass: 'alert-button-danger',
        handler: () => {
          handleDelete();
        }
      }
    ]"
    @didDismiss="isDeleteDialogOpen = false"
  ></ion-alert>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { IonAlert, IonButton, IonIcon } from '@ionic/vue';
import { ellipsisVertical, pencilOutline, trashOutline } from 'ionicons/icons';
import StatusChip from '@/components/StatusChip.vue';
import ContextMenu, { type ContextMenuItem } from '@/components/ContextMenu.vue';
import { useCalendar } from '@/composables/useCalendar';
import { useAlert } from '@/composables/useAlert';
import type { CalendarCardProps } from '@/types/calendar';

// Props
const props = defineProps<CalendarCardProps>();

// Emits
const emit = defineEmits<{
  'click': [calendarId: string];
  'edit': [calendarId: string];
  'delete': [calendarId: string];
}>();

// Composables
const { deleteCalendar } = useCalendar();
const { showError } = useAlert();

// Reactive state for context menu and delete functionality
const isContextMenuOpen = ref(false);
const isDeleteDialogOpen = ref(false);
const isDeleting = ref(false);
const popoverEvent = ref<Event | undefined>(undefined);
const contextMenuTrigger = ref<HTMLElement | null>(null);

// Check if calendar is shared (has shareToken) - shared calendars cannot be edited
const isShared = computed(() => !!props.calendar.shareToken);

// Context menu items configuration (for ContextMenu component)
const contextMenuItems = computed<ContextMenuItem[]>(() => {
  const items: ContextMenuItem[] = [];

  // Only show Edit button if calendar is NOT shared
  if (!isShared.value) {
    items.push({
      text: 'Edit',
      icon: pencilOutline,
      handler: handleEdit
    });
  }

  // Always show Delete button
  items.push({
    text: 'Delete',
    icon: trashOutline,
    role: 'destructive',
    handler: showDeleteConfirmation
  });

  // Always show Cancel button
  items.push({
    text: 'Cancel',
    role: 'cancel',
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    handler: () => {} // No-op, ContextMenu will just dismiss
  });

  return items;
});

// Computed properties for professional data display
const videoProgress = computed(() => {
  // Calculate total days from duration (assuming Calendar interface has duration)
  // For now, we'll extract from dateRange or use videoCount as fallback
  const totalDays = calculateTotalDays();
  const uploadedVideos = props.calendar.videoCount || 0;

  return `${uploadedVideos}/${totalDays} videos`;
});

// Format date range in European style (DD.MM.YYYY – DD.MM.YYYY)
const formattedDateRange = computed(() => {
  return props.calendar.dateRange.replace(/(\d{4})-(\d{2})-(\d{2})/g, '$3.$2.$1').replace(' to ', ' – ');
});

// Concise delete confirmation message
const deleteConfirmationMessage = computed(() => {
  const uploadedVideos = props.calendar.videoCount || 0;

  return `This will permanently delete ${uploadedVideos} video${uploadedVideos !== 1 ? 's' : ''} and all calendar data. This cannot be undone.`;
});

// Helper function to calculate total days from date range
const calculateTotalDays = (): number => {
  try {
    // Parse date range "YYYY-MM-DD to YYYY-MM-DD" format
    const dateRange = props.calendar.dateRange;
    const dates = dateRange.split(' to ');
    
    if (dates.length !== 2) return 1;
    
    const startDate = new Date(dates[0]);
    const endDate = new Date(dates[1]);
    
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return 1;
    
    // Calculate days difference (inclusive)
    const timeDiff = endDate.getTime() - startDate.getTime();
    const dayDiff = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1;
    
    return dayDiff > 0 ? dayDiff : 1;
  } catch {
    // Fallback: if we can't parse, assume single day
    return 1;
  }
};

// Handle click/keyboard interaction
const handleClick = () => {
  if (props.onClick) {
    props.onClick(props.calendar.id);
  }
  emit('click', props.calendar.id);
};

// Context menu functionality
const openContextMenu = (event: Event) => {
  event.stopPropagation(); // Prevent card click
  popoverEvent.value = event; // Store event for popover positioning
  isContextMenuOpen.value = true;
};

// Close context menu with proper cleanup
const closeContextMenu = () => {
  isContextMenuOpen.value = false;
  popoverEvent.value = undefined; // Clear event reference to prevent memory leaks
};

const handleEdit = () => {
  closeContextMenu(); // Use cleanup function
  emit('edit', props.calendar.id);
};

// Delete functionality
const showDeleteConfirmation = () => {
  closeContextMenu(); // Close menu before showing dialog
  isDeleteDialogOpen.value = true;
};

const handleDelete = async () => {
  try {
    isDeleteDialogOpen.value = false;
    isDeleting.value = true;

    const result = await deleteCalendar(props.calendar.id);

    if (result.success) {
      // Emit delete event so parent can handle any additional logic
      emit('delete', props.calendar.id);
    } else {
      // Show error using consistent useAlert composable
      await showError(result.error || 'Failed to delete calendar', {
        header: 'Delete Failed'
      });
    }
  } catch (error) {
    console.error('Delete error:', error);
    await showError('An unexpected error occurred while deleting the calendar', {
      header: 'Delete Failed'
    });
  } finally {
    isDeleting.value = false;
  }
};
</script>

<style scoped>
/* Lightweight responsive calendar card */
.calendar-card {
  background: var(--color-surface);
  padding: clamp(1rem, 3vw, 1.5rem);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: all var(--transition-base);
  border: 2px solid transparent;
  min-height: clamp(2.75rem, 8vh, 4rem); /* NFR [U2]: Touch-friendly targets */
  text-align: left;
  position: relative;
  container-type: inline-size;
}

/* Context Menu Button - positioned in top-right corner */
.context-menu-button {
  position: absolute;
  top: clamp(0.5rem, 2vw, 0.75rem);
  right: clamp(0.5rem, 2vw, 0.75rem);
  z-index: 10;
  --padding-start: 0.5rem;
  --padding-end: 0.5rem;
  min-width: 44px; /* NFR [U2]: Touch-friendly minimum */
  min-height: 44px; /* NFR [U2]: Touch-friendly minimum */
  color: var(--color-text-secondary);
  transition: color var(--transition-base);
}

.context-menu-button:hover {
  color: var(--color-text-primary);
}

.context-menu-button ion-icon {
  font-size: 1.5rem;
}

<<<<<<< HEAD
/* Delete button for shared/active calendars */
.context-menu-button.delete-button {
  color: var(--ion-color-danger);
}

.context-menu-button.delete-button:hover {
  color: var(--ion-color-danger);
  opacity: 0.8;
}

/* Popover Content Styling - Desktop only */
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
  --min-height: 44px; /* NFR [U2]: Touch-friendly */
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

=======
>>>>>>> 38f30de (Refactor: Extract ContextMenu component and improve code reusability)
/* Hover and focus states following theme patterns */
.calendar-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-focus);
}

.calendar-card:focus {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

/* Card header with title and status chip */
.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding-right: var(--spacing-xl); /* Space for delete button */
}

.calendar-title {
  font-size: clamp(1rem, 3vw, 1.25rem);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: var(--line-height-tight);
  flex: 1;
  /* Handle long titles gracefully */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.calendar-status-chip {
  flex-shrink: 0;
  align-self: flex-start;
}

/* Date range styling */
.calendar-dates {
  font-size: clamp(0.8rem, 2vw, 0.875rem);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  margin: 0 0 var(--spacing-sm) 0;
  line-height: var(--line-height-normal);
}

/* Video progress section */
.calendar-progress {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.progress-text {
  font-size: clamp(0.75rem, 1.8vw, 0.875rem);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  background-color: var(--color-background);
  padding: clamp(0.25rem, 1vw, 0.5rem) clamp(0.5rem, 1.5vw, 0.75rem);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

/* Container queries for micro-layouts */
@container (max-width: 15rem) {
  .calendar-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
    padding-right: var(--spacing-lg); /* Reduced padding for smaller cards */
  }
  
  .calendar-status-chip {
    align-self: flex-end;
  }
}

/* Accessibility and user preference support */
@media (prefers-contrast: high) {
  .calendar-card {
    border-width: 2px;
    border-color: var(--color-text-primary);
  }
  
  .progress-text {
    border-width: 2px;
    border-color: var(--color-text-primary);
  }
}

@media (prefers-reduced-motion: reduce) {
  .calendar-card {
    transition: none;
  }
  
  .calendar-card:hover {
    transform: none;
  }
}

@media (prefers-color-scheme: dark) {
  .progress-text {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
  }
}

/* Animation entrance effect */
.calendar-card {
  animation: cardEnter var(--transition-slow) ease-out;
}

@keyframes cardEnter {
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
