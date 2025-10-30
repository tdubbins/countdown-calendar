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
    <!-- Three Dots Menu Button - positioned in top-right corner -->
    <ion-button
      @click.stop="openContextMenu"
      ref="contextMenuTrigger"
      class="context-menu-button"
      fill="clear"
      size="small"
      :aria-label="`Options for ${calendar.title}`"
    >
      <ion-icon slot="icon-only" :icon="ellipsisVertical"></ion-icon>
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

  <!-- Context Menu - Mobile: Action Sheet, Desktop: Popover -->
  <!-- Mobile Action Sheet (< 768px) -->
  <ion-action-sheet
    v-if="isMobileView"
    :is-open="isContextMenuOpen"
    :header="`${calendar.title} Options`"
    :buttons="contextMenuButtons"
    @didDismiss="closeContextMenu"
  ></ion-action-sheet>

  <!-- Desktop Popover (>= 768px) -->
  <ion-popover
    v-else
    :is-open="isContextMenuOpen"
    :event="popoverEvent"
    :dismiss-on-select="true"
    @didDismiss="closeContextMenu"
  >
    <ion-content class="popover-content">
      <ion-list lines="none">
        <ion-item button @click="handleEdit" detail="false">
          <ion-icon :icon="pencilOutline" slot="start" color="primary"></ion-icon>
          <ion-label>Edit</ion-label>
        </ion-item>
        <ion-item button @click="showDeleteConfirmation" detail="false" class="delete-item">
          <ion-icon :icon="trashOutline" slot="start" color="danger"></ion-icon>
          <ion-label color="danger">Delete</ion-label>
        </ion-item>
      </ion-list>
    </ion-content>
  </ion-popover>

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
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { IonAlert, IonActionSheet, IonPopover, IonButton, IonIcon, IonContent, IonList, IonItem, IonLabel } from '@ionic/vue';
import { ellipsisVertical, pencilOutline, trashOutline } from 'ionicons/icons';
import StatusChip from '@/components/StatusChip.vue';
import { useCalendar } from '@/composables/useCalendar';
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

// Reactive state for context menu and delete functionality
const isContextMenuOpen = ref(false);
const isDeleteDialogOpen = ref(false);
const isDeleting = ref(false);
const popoverEvent = ref<Event | undefined>(undefined);
const contextMenuTrigger = ref<HTMLElement | null>(null);

// Responsive detection for mobile vs desktop
const isMobileView = ref(window.innerWidth < 768);

// Update mobile view on window resize
const updateMobileView = () => {
  isMobileView.value = window.innerWidth < 768;
};

onMounted(() => {
  window.addEventListener('resize', updateMobileView);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateMobileView);
});

// Context menu buttons configuration
const contextMenuButtons = computed(() => [
  {
    text: 'Edit',
    icon: pencilOutline,
    handler: () => {
      handleEdit();
    }
  },
  {
    text: 'Delete',
    icon: trashOutline,
    role: 'destructive',
    handler: () => {
      showDeleteConfirmation();
    }
  },
  {
    text: 'Cancel',
    role: 'cancel'
  }
]);

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

  // For desktop popover, we need the event to position it
  if (!isMobileView.value) {
    popoverEvent.value = event;
  }
  isContextMenuOpen.value = true;
};

// Close context menu with proper cleanup
const closeContextMenu = () => {
  isContextMenuOpen.value = false;

  // Clear event reference to prevent memory leaks and popover errors
  if (!isMobileView.value) {
    popoverEvent.value = undefined;
  }
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
      // Show error message - could be improved with a toast notification
      console.error('Delete failed:', result.error);
      alert(`Failed to delete calendar: ${result.error}`);
    }
  } catch (error) {
    console.error('Delete error:', error);
    alert('An unexpected error occurred while deleting the calendar');
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

<style>
/* Mobile Action Sheet Improvements - Global styles (not scoped) */
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
