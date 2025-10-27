<template>
  <div 
    class="calendar-card"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    tabindex="0"
    role="button"
    :aria-label="`Open calendar ${calendar.title}`"
  >
    <div class="calendar-icon">📅</div>
    <h3>{{ calendar.title }}</h3>
    <p class="calendar-dates">{{ calendar.dateRange }}</p>
    <p class="calendar-info">{{ calendar.videoCount }} videos</p>
    <p class="calendar-status">{{ calendar.status }}</p>
  </div>
</template>

<script setup lang="ts">
import type { CalendarCardProps } from '@/types/calendar';

// Props
const props = defineProps<CalendarCardProps>();

// Emits
const emit = defineEmits<{
  'click': [calendarId: string];
}>();

// Handle click/keyboard interaction
const handleClick = () => {
  if (props.onClick) {
    props.onClick(props.calendar.id);
  }
  emit('click', props.calendar.id);
};
</script>

<style scoped>
.calendar-card {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  min-height: 44px; /* Touch-friendly */
  text-align: center;
}

.calendar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  border-color: var(--ion-color-primary);
}

.calendar-card:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

.calendar-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

.calendar-card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.calendar-dates {
  font-size: 0.95rem;
  color: var(--ion-color-primary);
  font-weight: 500;
  margin-bottom: 6px;
}

.calendar-info {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 4px;
}

.calendar-status {
  font-size: 0.85rem;
  color: #888;
  margin: 0;
}

/* Mobile adjustments */
@media (max-width: 480px) {
  .calendar-card {
    padding: 16px;
  }
}

/* Tablet improvements */
@media (min-width: 768px) {
  .calendar-card {
    padding: 24px;
  }
}

/* High contrast support */
@media (prefers-contrast: high) {
  .calendar-card {
    border-width: 2px;
    border-color: #333;
  }
}

/* Touch-friendly targets */
@media (pointer: coarse) {
  .calendar-card {
    min-height: 48px;
    padding: 20px;
  }
}
</style>