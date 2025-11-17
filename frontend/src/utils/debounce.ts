/**
 * Debounce Utility
 *
 * Creates a debounced function that delays invoking the provided function
 * until after `delay` milliseconds have elapsed since the last time it was invoked.
 *
 * Useful for:
 * - Form validation (validate only after user stops typing)
 * - Search queries (search only after user stops typing)
 * - Window resize handlers
 * - Scroll event handlers
 *
 * @example
 * const debouncedValidate = debounce((value: string) => {
 *   console.log('Validating:', value);
 * }, 300);
 *
 * // Only logs once after 300ms of no calls
 * debouncedValidate('a');
 * debouncedValidate('ab');
 * debouncedValidate('abc');
 * // -> Logs "Validating: abc" after 300ms
 */

/**
 * Creates a debounced function
 *
 * @param func - The function to debounce
 * @param delay - The delay in milliseconds (default: 300ms)
 * @returns A debounced version of the function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay = 300
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return function debounced(...args: Parameters<T>): void {
    // Clear the previous timeout
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }

    // Set a new timeout
    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, delay);
  };
}

/**
 * Creates a debounced function with a cancel method
 *
 * @param func - The function to debounce
 * @param delay - The delay in milliseconds (default: 300ms)
 * @returns A debounced function with a cancel method
 *
 * @example
 * const debouncedSave = debouncedWithCancel((data) => saveData(data), 500);
 * debouncedSave(formData);
 *
 * // Cancel pending save
 * debouncedSave.cancel();
 */
export function debouncedWithCancel<T extends (...args: any[]) => any>(
  func: T,
  delay = 300
): ((...args: Parameters<T>) => void) & { cancel: () => void } {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const debounced = function(...args: Parameters<T>): void {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, delay);
  };

  debounced.cancel = function(): void {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  return debounced;
}

/**
 * Common debounce delay constants
 */
export const DEBOUNCE_DELAYS = {
  /** Fast debounce for immediate feedback (100ms) */
  FAST: 100,
  /** Default debounce for form validation (300ms) */
  DEFAULT: 300,
  /** Medium debounce for search queries (500ms) */
  MEDIUM: 500,
  /** Slow debounce for expensive operations (1000ms) */
  SLOW: 1000,
} as const;
