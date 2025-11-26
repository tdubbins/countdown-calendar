import { computed, ComputedRef } from 'vue';
import { SharedCalendarDay } from './useSharedCalendar';

/**
 * Door state types
 * - locked: Future day, not yet unlocked (grey, not clickable)
 * - unlocked: Day is unlocked but not yet opened (Christmas gradient, clickable)
 * - opened: Day has been opened/watched (dark green, still clickable for rewatch)
 */
export type DoorState = 'locked' | 'unlocked' | 'opened';

/**
 * Composable for calculating door states
 * Determines if a door should be locked, unlocked, or opened
 *
 * State priority logic:
 * 1. If backend says is_unlocked = false → 'locked'
 * 2. Else if day is in openedDays array → 'opened'
 * 3. Else → 'unlocked'
 */
export function useDoorState(
  day: SharedCalendarDay,
  isDayOpened: (dayNumber: number) => boolean
): ComputedRef<DoorState> {
  const doorState = computed<DoorState>(() => {
    // Priority 1: Check if unlocked (from backend)
    if (!day.isUnlocked) {
      return 'locked';
    }

    // Priority 2: Check if already opened (from LocalStorage)
    if (isDayOpened(day.dayNumber)) {
      return 'opened';
    }

    // Priority 3: Unlocked but not yet opened
    return 'unlocked';
  });

  return doorState;
}

/**
 * Get CSS class for door state
 * @param state - The door state
 * @returns CSS class name
 */
export function getDoorStateClass(state: DoorState): string {
  return `door-card--${state}`;
}

/**
 * Check if door is clickable
 * @param state - The door state
 * @returns true if door can be clicked
 */
export function isDoorClickable(state: DoorState): boolean {
  // Locked doors are not clickable
  // Unlocked and opened doors are both clickable
  return state !== 'locked';
}

/**
 * Get ARIA label for door state.
 *
 * @param dayNumber - The day number
 * @param state - The door state
 * @param startDate - The calendar start date (for locked day info)
 * @returns Descriptive ARIA label
 */
export function getDoorAriaLabel(
  dayNumber: number,
  state: DoorState,
  startDate?: string
): string {
  const baseLabel = `Day ${dayNumber}`;

  switch (state) {
    case 'locked': {
      if (startDate) {
        // Calculate unlock date for better UX
        const start = new Date(startDate);
        const unlockDate = new Date(start);
        unlockDate.setDate(start.getDate() + dayNumber - 1);
        const unlockDateString = unlockDate.toLocaleDateString('en-US', {
          month: 'long',
          day: 'numeric'
        });
        return `${baseLabel}, locked until ${unlockDateString}`;
      }
      return `${baseLabel}, locked, not yet available`;
    }
    case 'unlocked':
      return `${baseLabel}, unlocked, click to open and watch video`;
    case 'opened':
      return `${baseLabel}, already opened, click to watch video again`;
    default:
      return baseLabel;
  }
}

/**
 * Get icon name for door state
 * @param state - The door state
 * @returns Ionicon name for the state
 */
export function getDoorStateIcon(state: DoorState): string {
  switch (state) {
    case 'locked':
      return 'lock-closed-outline';
    case 'unlocked':
      return 'gift-outline';
    case 'opened':
      return 'checkmark-circle-outline';
    default:
      return 'gift-outline';
  }
}
