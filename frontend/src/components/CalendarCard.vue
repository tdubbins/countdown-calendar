<template>
  <div
    class="calendar-card"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    tabindex="0"
    role="button"
    :aria-label="`Open calendar ${calendar.title}. ${videoProgress}. Status: ${calendarState}`"
  >
    <!-- Action Button - Top-right corner: Delete only -->
    <ion-button
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
      <ion-chip
        :color="publishedChipColor"
        outline
        class="published-status-chip"
        :aria-label="isCalendarPublished ? 'Calendar is published' : 'Calendar is unpublished'"
      >
        <ion-icon :icon="isCalendarPublished ? lockOpenOutline : lockClosedOutline" aria-hidden="true"></ion-icon>
        <ion-label>{{ isCalendarPublished ? 'Published' : 'Unpublished' }}</ion-label>
      </ion-chip>
    </div>
    
    <div class="calendar-info-row">
      <p class="calendar-dates">{{ formattedDateRange }}</p>
      <ion-chip
        :color="calendarStateChipColor"
        class="calendar-state-chip"
        :aria-label="`Calendar state: ${calendarState}`"
      >
        <ion-label>{{ calendarState }}</ion-label>
      </ion-chip>
    </div>

    <div class="calendar-progress">
      <span
        class="progress-text"
        :class="progressColorClass"
      >
        {{ videoProgress }}
      </span>
    </div>
  </div>

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
import { IonAlert, IonButton, IonIcon, IonChip, IonLabel } from '@ionic/vue';
import { trashOutline, lockOpenOutline, lockClosedOutline } from 'ionicons/icons';
import { useCalendar } from '@/composables/useCalendar';
import { useAlert } from '@/composables/useAlert';
import type { CalendarCardProps } from '@/types/calendar';

// Props
const props = defineProps<CalendarCardProps>();

// Emits
const emit = defineEmits<{
  'click': [calendarId: string];
  'delete': [calendarId: string];
}>();

// Composables
const { deleteCalendar } = useCalendar();
const { showError } = useAlert();

// Reactive state for delete functionality
const isDeleteDialogOpen = ref(false);

// Calendar published status
const isCalendarPublished = computed(() => props.calendar.published || false);

// Published chip color
const publishedChipColor = computed(() => {
  return isCalendarPublished.value ? 'success' : 'medium';
});

// Calculate calendar state (upcoming/ongoing/expired)
const calendarState = computed(() => {
  if (!props.calendar.startDate || !props.calendar.endDate) {
    return 'Unknown';
  }

  const now = new Date();
  now.setHours(0, 0, 0, 0); // Reset to start of day for date comparison

  const startDate = new Date(props.calendar.startDate);
  startDate.setHours(0, 0, 0, 0);

  const endDate = new Date(props.calendar.endDate);
  endDate.setHours(0, 0, 0, 0);

  if (now < startDate) {
    return 'Upcoming';
  } else if (now > endDate) {
    return 'Expired';
  } else {
    return 'Ongoing';
  }
});

// Calendar state chip color
const calendarStateChipColor = computed(() => {
  switch (calendarState.value) {
    case 'Upcoming':
      return 'primary';
    case 'Ongoing':
      return 'success';
    case 'Expired':
      return 'danger';
    default:
      return 'medium';
  }
});

// Constants for date calculations
const MS_PER_DAY = 1000 * 60 * 60 * 24;

// Calculate total days from date range (cached computed property for performance)
const totalDays = computed(() => {
  try {
    // Parse date range "YYYY-MM-DD to YYYY-MM-DD" format
    const dateRange = props.calendar.dateRange;

    // Null/undefined check to prevent crashes
    if (!dateRange) return 1;

    const dates = dateRange.split(' to ');
    if (dates.length !== 2) return 1;

    const startDate = new Date(dates[0]);
    const endDate = new Date(dates[1]);

    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return 1;

    // Calculate days difference (inclusive)
    const timeDiff = endDate.getTime() - startDate.getTime();
    const dayDiff = Math.ceil(timeDiff / MS_PER_DAY) + 1;

    return dayDiff > 0 ? dayDiff : 1;
  } catch {
    // Fallback: if we can't parse, assume single day
    return 1;
  }
});

// Video progress completion status
const progressPercentage = computed(() => {
  const videoCount = props.calendar.videoCount || 0;
  const duration = totalDays.value;

  if (duration === 0) {
    return 0;
  }
  return (videoCount / duration) * 100;
});

// Progress color class based on completion percentage
const progressColorClass = computed(() => {
  const videoCount = props.calendar.videoCount || 0;
  const percentage = progressPercentage.value;

  if (videoCount === 0 || percentage === 0) {
    return 'progress-text--empty';    // Gray - not started
  } else if (percentage >= 100) {
    return 'progress-text--complete'; // Green - complete
  } else {
    return 'progress-text--progress'; // Orange - in progress
  }
});

// Display video upload progress
const videoProgress = computed(() => {
  const uploadedVideos = props.calendar.videoCount || 0;
  return `${uploadedVideos}/${totalDays.value} videos`;
});

// Format date range in European style (DD.MM.YYYY – DD.MM.YYYY)
const formattedDateRange = computed(() => {
  if (!props.calendar.dateRange) {
    // Fallback: construct from startDate and endDate if dateRange is missing
    const start = props.calendar.startDate || '';
    const end = props.calendar.endDate || '';
    if (start && end) {
      const formatDate = (date: string) => {
        const [year, month, day] = date.split('-');
        return `${day}.${month}.${year}`;
      };
      return `${formatDate(start)} – ${formatDate(end)}`;
    }
    return 'Date range unavailable';
  }
  return props.calendar.dateRange.replace(/(\d{4})-(\d{2})-(\d{2})/g, '$3.$2.$1').replace(' to ', ' – ');
});

// Concise delete confirmation message
const deleteConfirmationMessage = computed(() => {
  const uploadedVideos = props.calendar.videoCount || 0;

  return `This will permanently delete ${uploadedVideos} video${uploadedVideos !== 1 ? 's' : ''} and all calendar data. This cannot be undone.`;
});

// Handle click/keyboard interaction
const handleClick = () => {
  if (props.onClick) {
    props.onClick(props.calendar.id);
  }
  emit('click', props.calendar.id);
};

// Delete functionality
const showDeleteConfirmation = () => {
  isDeleteDialogOpen.value = true;
};

const handleDelete = async () => {
  try {
    isDeleteDialogOpen.value = false;

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

/* Delete button styling */
.context-menu-button.delete-button {
  color: var(--ion-color-danger);
}

.context-menu-button.delete-button:hover {
  color: var(--ion-color-danger);
  opacity: 0.8;
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

/* Card header with title and status chip - Adaptive layout (NFR [U1]: Responsive design) */
.calendar-header {
  display: flex;
  flex-wrap: wrap; /* Allow wrapping when title is long */
  align-items: center;
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
  /* Allow title to take available space, chip wraps to next row when title is long */
  flex: 1 1 auto;
  min-width: 0; /* Prevent flex item overflow */
  /* Handle long titles gracefully with multi-line support */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* Show up to 2 lines */
  -webkit-box-orient: vertical;
  word-wrap: break-word;
}

/* Published status chip - Wraps to new row when title is long, aligns left on new row */
.published-status-chip {
  flex: 0 0 auto; /* Don't grow or shrink */
  font-size: 0.75rem;
  height: auto;
  min-height: unset;
  margin: 0; /* Remove default ion-chip margins */
}

.published-status-chip ion-label {
  font-size: 0.75rem;
  margin: 0;
}

/* Calendar info row - dates and state chip */
.calendar-info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  flex-wrap: wrap;
}

/* Date range styling */
.calendar-dates {
  font-size: clamp(0.8rem, 2vw, 0.875rem);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  margin: 0;
  line-height: var(--line-height-normal);
  flex: 1;
  min-width: 120px;
}

/* Calendar state chip */
.calendar-state-chip {
  flex-shrink: 0;
  font-size: 0.75rem;
  height: auto;
  min-height: unset;
  margin: 0; /* Remove default ion-chip margins */
}

.calendar-state-chip ion-label {
  font-size: 0.75rem;
  margin: 0;
  font-weight: var(--font-weight-semibold);
}

/* Video progress section */
.calendar-progress {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

/* Video progress chip-like styling */
.progress-text {
  display: inline-block;
  font-size: clamp(0.75rem, 1.8vw, 0.875rem);
  font-weight: var(--font-weight-semibold);
  padding: clamp(0.25rem, 1vw, 0.5rem) clamp(0.5rem, 1.5vw, 0.75rem);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

/* Empty state (0%) - Gray */
.progress-text--empty {
  color: #6c757d;
  background: rgba(108, 117, 125, 0.1);
  border: 1px solid rgba(108, 117, 125, 0.3);
}

/* In progress (1-99%) - Orange/Warning */
.progress-text--progress {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
}

/* Complete (100%) - Green/Success */
.progress-text--complete {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Container queries for micro-layouts (NFR [U1]: Mobile responsiveness) */
@container (max-width: 15rem) {
  .calendar-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
    padding-right: var(--spacing-lg); /* Reduced padding for smaller cards */
  }

  .calendar-title {
    width: 100%; /* Full width on very small cards */
  }

  .published-status-chip {
    align-self: flex-start; /* Left-aligned when stacked */
  }

  .calendar-info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }

  .calendar-state-chip {
    align-self: flex-start;
  }
}

/* Additional responsive support for mobile devices (NFR [U1]: 320px+ screens) */
@media (max-width: 480px) {
  .calendar-header {
    flex-wrap: wrap;
    gap: clamp(0.5rem, 2vw, 0.75rem);
  }

  .calendar-title {
    /* Title takes available space, chip wraps to new row if needed */
    flex: 1 1 auto;
    min-width: 0;
  }

  .published-status-chip {
    /* Chip wraps to new row on mobile, left-aligned */
    flex: 0 0 auto;
  }
}

/* Accessibility and user preference support */
@media (prefers-contrast: high) {
  .calendar-card {
    border-width: 2px;
    border-color: var(--color-text-primary);
  }

  .progress-text--empty,
  .progress-text--progress,
  .progress-text--complete {
    border-width: 2px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .calendar-card {
    transition: none;
  }

  .calendar-card:hover {
    transform: none;
  }

  .progress-text {
    transition: none;
  }
}

/* Dark mode support for better contrast */
@media (prefers-color-scheme: dark) {
  .progress-text--empty {
    color: #9ca3af;
    background: rgba(156, 163, 175, 0.15);
    border-color: rgba(156, 163, 175, 0.4);
  }

  .progress-text--progress {
    color: #fb923c;
    background: rgba(251, 146, 60, 0.15);
    border-color: rgba(251, 146, 60, 0.4);
  }

  .progress-text--complete {
    color: #34d399;
    background: rgba(52, 211, 153, 0.15);
    border-color: rgba(52, 211, 153, 0.4);
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
