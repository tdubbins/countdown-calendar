import { ref, watch } from 'vue';

/**
 * Composable for tracking which calendar doors have been opened.
 * Uses LocalStorage for persistence (per-browser, not synced across devices).
 */
export function useOpenedTracking(shareToken: string) {
  const openedDays = ref<number[]>([]);
  const storageKey = `calendar_${shareToken}_opened`;

  /**
   * Load opened days from LocalStorage on initialization
   */
  const loadOpenedDays = (): void => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Validate that it's an array of numbers
        if (Array.isArray(parsed) && parsed.every(item => typeof item === 'number')) {
          openedDays.value = parsed;
        } else {
          console.warn('Invalid opened days data in LocalStorage, resetting');
          openedDays.value = [];
          saveOpenedDays();
        }
      }
    } catch (error) {
      console.error('Error loading opened days from LocalStorage:', error);
      openedDays.value = [];
    }
  };

  /**
   * Save opened days to LocalStorage
   */
  const saveOpenedDays = (): void => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(openedDays.value));
    } catch (error) {
      console.error('Error saving opened days to LocalStorage:', error);
    }
  };

  /**
   * Check if a specific day has been opened
   * @param dayNumber - The day number to check
   * @returns true if the day has been opened
   */
  const isDayOpened = (dayNumber: number): boolean => {
    return openedDays.value.includes(dayNumber);
  };

  /**
   * Mark a day as opened
   * @param dayNumber - The day number to mark as opened
   */
  const markDayAsOpened = (dayNumber: number): void => {
    // Validate day number
    if (!Number.isInteger(dayNumber) || dayNumber < 1 || dayNumber > 31) {
      console.warn(`Invalid day number: ${dayNumber}`);
      return;
    }

    // Only add if not already in the list
    if (!isDayOpened(dayNumber)) {
      openedDays.value.push(dayNumber);
      // Sort for consistent ordering
      openedDays.value.sort((a, b) => a - b);
      saveOpenedDays();
    }
  };

  /**
   * Clear all opened days (for testing or reset)
   */
  const clearOpenedDays = (): void => {
    openedDays.value = [];
    saveOpenedDays();
  };

  /**
   * Get count of opened days
   */
  const getOpenedCount = (): number => {
    return openedDays.value.length;
  };

  // Watch for changes and auto-save
  watch(openedDays, saveOpenedDays, { deep: true });

  // Load on initialization
  loadOpenedDays();

  return {
    openedDays,
    isDayOpened,
    markDayAsOpened,
    clearOpenedDays,
    getOpenedCount
  };
}
