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
    <div class="calendar-header">
      <h3 class="calendar-title">{{ calendar.title }}</h3>
      <StatusChip 
        :status="calendar.status" 
        variant="minimal"
        class="calendar-status-chip"
      />
    </div>
    
    <p class="calendar-dates">{{ calendar.dateRange }}</p>
    
    <div class="calendar-progress">
      <span class="progress-text">{{ videoProgress }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import StatusChip from '@/components/StatusChip.vue';
import type { CalendarCardProps } from '@/types/calendar';

// Props
const props = defineProps<CalendarCardProps>();

// Emits
const emit = defineEmits<{
  'click': [calendarId: string];
}>();

// Computed properties for professional data display
const videoProgress = computed(() => {
  // Calculate total days from duration (assuming Calendar interface has duration)
  // For now, we'll extract from dateRange or use videoCount as fallback
  const totalDays = calculateTotalDays();
  const uploadedVideos = props.calendar.videoCount || 0;
  
  return `${uploadedVideos}/${totalDays} videos`;
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