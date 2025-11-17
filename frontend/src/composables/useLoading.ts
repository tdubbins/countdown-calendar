/**
 * useLoading Composable
 *
 * Provides a reusable full-screen loading overlay for page-level operations.
 * Uses Ionic's loadingController for consistent UX across the application.
 *
 * Benefits:
 * - Prevents user interaction during critical operations
 * - Professional loading appearance
 * - Consistent with mobile app patterns
 * - Automatic dismissal on completion
 *
 * Usage example:
 * ```typescript
 * const { showLoading } = useLoading();
 *
 * // Show loading overlay
 * const loading = await showLoading('Deleting calendar...');
 * await deleteCalendar(id);
 * await loading.dismiss();
 *
 * // Or use with automatic dismissal
 * await withLoading('Saving changes...', async () => {
 *   await saveChanges();
 * });
 * ```
 */

import { loadingController } from '@ionic/vue';

/**
 * Loading spinner variants
 */
export type LoadingSpinner =
  | 'bubbles'
  | 'circles'
  | 'circular'
  | 'crescent'
  | 'dots'
  | 'lines'
  | 'lines-small';

/**
 * Loading configuration options
 */
export interface LoadingOptions {
  message?: string;
  spinner?: LoadingSpinner;
  duration?: number;
  backdropDismiss?: boolean;
  cssClass?: string;
}

/**
 * useLoading Composable
 */
export function useLoading() {
  /**
   * Show a full-screen loading overlay
   *
   * Returns the loading instance which must be manually dismissed.
   * Use this when you need fine-grained control over dismissal timing.
   *
   * @param message - Loading message to display
   * @param options - Optional customization options
   */
  const showLoading = async (
    message = 'Loading...',
    options: Omit<LoadingOptions, 'message'> = {}
  ) => {
    const {
      spinner = 'crescent',
      duration,
      backdropDismiss = false,
      cssClass,
    } = options;

    const loading = await loadingController.create({
      message,
      spinner,
      duration,
      backdropDismiss,
      cssClass,
    });

    await loading.present();
    return loading;
  };

  /**
   * Execute an async operation with automatic loading overlay
   *
   * Shows loading overlay during execution and automatically dismisses
   * when the operation completes (success or failure).
   *
   * @param message - Loading message to display
   * @param operation - Async function to execute
   * @param options - Optional customization options
   */
  const withLoading = async <T>(
    message: string,
    operation: () => Promise<T>,
    options: Omit<LoadingOptions, 'message'> = {}
  ): Promise<T> => {
    const loading = await showLoading(message, options);

    try {
      const result = await operation();
      return result;
    } finally {
      await loading.dismiss();
    }
  };

  /**
   * Dismiss all active loading overlays
   *
   * Useful for cleanup or error scenarios where you want to
   * ensure no loading overlays remain on screen.
   */
  const dismissAll = async () => {
    const topLoading = await loadingController.getTop();
    if (topLoading) {
      await loadingController.dismiss();
    }
  };

  return {
    showLoading,
    withLoading,
    dismissAll,
  };
}
