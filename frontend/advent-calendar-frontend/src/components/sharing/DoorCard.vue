<template>
  <button
    class="door-card"
    :class="[doorStateClass, { 'door-card--clickable': isClickable }]"
    :aria-label="ariaLabel"
    :aria-disabled="!isClickable"
    :disabled="!isClickable"
    :tabindex="isClickable ? 0 : -1"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
    role="button"
  >
    <!-- Day Number Badge -->
    <div class="door-number" aria-hidden="true">
      {{ day.dayNumber }}
    </div>

    <!-- Door Content -->
    <div class="door-content">
      <!-- State Icon -->
      <ion-icon
        :icon="stateIcon"
        class="door-icon"
        :class="`door-icon--${state}`"
        aria-hidden="true"
      ></ion-icon>

      <!-- Opened State: Show Checkmark -->
      <ion-icon
        v-if="state === 'opened'"
        :icon="checkmarkCircle"
        class="door-checkmark"
        aria-hidden="true"
      ></ion-icon>

      <!-- Locked State: Show Lock Icon -->
      <ion-icon
        v-if="state === 'locked'"
        :icon="lockClosedOutline"
        class="door-lock"
        aria-hidden="true"
      ></ion-icon>
    </div>

    <!-- Thumbnail for opened doors (future: Issue #85) -->
    <div v-if="state === 'opened' && day.thumbnail_path" class="door-thumbnail">
      <img
        :src="day.thumbnail_path"
        :alt="`Thumbnail for day ${day.day_number}`"
        loading="lazy"
      />
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonIcon } from '@ionic/vue';
import {
  lockClosedOutline,
  giftOutline,
  checkmarkCircle
} from 'ionicons/icons';
import { SharedCalendarDay } from '@/composables/useSharedCalendar';
import {
  useDoorState,
  getDoorStateClass,
  isDoorClickable,
  getDoorAriaLabel,
  getDoorStateIcon
} from '@/composables/useDoorState';

// Props
interface Props {
  day: SharedCalendarDay;
  startDate?: string; // Optional to handle loading state
  isDayOpened: (dayNumber: number) => boolean;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
  doorClick: [dayNumber: number];
}>();

// Composables
const state = useDoorState(props.day, props.isDayOpened);

// Computed Properties
const doorStateClass = computed(() => getDoorStateClass(state.value));
const isClickable = computed(() => isDoorClickable(state.value));
const ariaLabel = computed(() =>
  getDoorAriaLabel(props.day.day_number, state.value, props.startDate)
);

// State icon based on door state
const stateIcon = computed(() => {
  const iconName = getDoorStateIcon(state.value);
  switch (iconName) {
    case 'lock-closed-outline':
      return lockClosedOutline;
    case 'checkmark-circle-outline':
      return checkmarkCircle;
    case 'gift-outline':
    default:
      return giftOutline;
  }
});

// Handlers
const handleClick = () => {
  if (isClickable.value) {
    emit('doorClick', props.day.day_number);
  }
};
</script>

<style scoped>
/* Base Door Card Styles */
.door-card {
  position: relative;
  aspect-ratio: 1;
  min-height: 9rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
  transition: all var(--transition-base);
  border: none;
  cursor: default;

  /* NFR [U2]: Touch-friendly minimum size (44px+) */
  min-width: 44px;
  min-height: 140px;

  /* Remove button defaults */
  font-family: inherit;
  width: 100%;
}

/* NFR [U5]: Focus indicator for keyboard navigation */
.door-card:focus-visible {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* State 1: Locked Door 🔒 */
.door-card--locked {
  background: linear-gradient(135deg, #4a5568, #2d3748);
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.door-card--locked .door-icon {
  color: #9ca3af;
  font-size: clamp(2rem, 6vw, 3rem);
}

.door-card--locked .door-lock {
  position: absolute;
  font-size: clamp(1.5rem, 4vw, 2rem);
  color: #6b7280;
  margin-top: 0.5rem;
}

/* State 2: Unlocked Door (Ready to Open) */
.door-card--unlocked {
  background: linear-gradient(135deg, #c41e3a 0%, #165b33 100%);
  border: 2px solid #ffd700;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.door-card--unlocked:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

.door-card--unlocked:active {
  transform: scale(0.98);
}

.door-card--unlocked .door-icon {
  color: #ffd700;
  font-size: clamp(2.5rem, 7vw, 3.5rem);
}

/* State 3: Opened Door (Already Watched) ✅ */
.door-card--opened {
  background: #2c5f2d;
  opacity: 0.85;
  border: 2px solid #165b33;
  cursor: pointer;
}

.door-card--opened:hover {
  opacity: 1;
  transform: scale(1.02);
}

.door-card--opened .door-icon {
  color: #a3e635;
  font-size: clamp(2rem, 6vw, 2.5rem);
}

.door-card--opened .door-checkmark {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  color: #4ade80;
  z-index: 2;
}

/* Day Number Badge */
.door-number {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.95);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  z-index: 2;
  /* NFR [U5]: Color contrast 4.5:1 */
  text-shadow: none;
}

@media (prefers-color-scheme: dark) {
  .door-number {
    background: rgba(0, 0, 0, 0.8);
    color: #ffffff;
  }
}

/* Door Content Container */
.door-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
  height: 100%;
  position: relative;
}

/* Door Icon */
.door-icon {
  transition: all var(--transition-base);
}

/* Thumbnail for Opened Doors */
.door-thumbnail {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  opacity: 0.3;
  z-index: 0;
}

.door-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* NFR [U5]: Accessibility - Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .door-card {
    transition: none;
  }

  .door-card--unlocked:hover,
  .door-card--opened:hover {
    transform: none;
  }
}

/* NFR [U5]: High contrast mode */
@media (prefers-contrast: high) {
  .door-card--locked {
    border: 3px solid #6b7280;
  }

  .door-card--unlocked {
    border-width: 3px;
  }

  .door-card--opened {
    border-width: 3px;
  }

  .door-number {
    font-weight: var(--font-weight-black);
    border: 1px solid currentColor;
  }
}

/* Responsive adjustments for very small screens */
@media (max-width: 640px) {
  .door-card {
    min-height: 140px;
    padding: var(--spacing-sm);
  }

  .door-number {
    font-size: 0.8rem;
    padding: 0.2rem 0.4rem;
  }
}

/* Container queries for extra small screens */
@container (max-width: 20rem) {
  .door-number {
    font-size: 0.75rem;
    padding: 0.15rem 0.35rem;
  }

  .door-icon {
    font-size: 1.5rem !important;
  }
}
</style>
