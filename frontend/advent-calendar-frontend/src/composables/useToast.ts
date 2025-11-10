/**
 * useToast Composable
 *
 * Provides a reusable, consistent toast notification system across the application.
 * Centralizes toast creation logic to ensure consistent UX and simplify maintenance.
 *
 * Benefits:
 * - DRY principle: Single source of truth for toast configuration
 * - Consistency: All toasts have same appearance and behavior
 * - Maintainability: Update toast behavior in one place
 * - Accessibility: Centralized ARIA announcements
 * - Type safety: TypeScript types for toast variants
 */

import { toastController } from '@ionic/vue';

/**
 * Toast variants with predefined configurations
 */
export type ToastType = 'success' | 'error' | 'info' | 'warning';

/**
 * Toast configuration options
 */
export interface ToastOptions {
  message: string;
  type?: ToastType;
  duration?: number;
  position?: 'top' | 'bottom' | 'middle';
}

/**
 * Default durations for different toast types (in milliseconds)
 */
const DEFAULT_DURATIONS: Record<ToastType, number> = {
  success: 2000,  // Quick confirmation
  error: 3000,    // More time to read error
  info: 2500,     // Medium duration
  warning: 3000,  // More time for warnings
};

/**
 * Color mapping for toast types
 */
const TOAST_COLORS: Record<ToastType, string> = {
  success: 'success',
  error: 'danger',
  info: 'primary',
  warning: 'warning',
};

/**
 * useToast Composable
 *
 * Usage example:
 * ```typescript
 * const { showSuccess, showError } = useToast();
 *
 * // Show success toast
 * await showSuccess('Calendar created successfully!');
 *
 * // Show error toast
 * await showError('Failed to upload video');
 *
 * // Show custom toast
 * await showToast({
 *   message: 'Processing...',
 *   type: 'info',
 *   duration: 5000
 * });
 * ```
 */
export function useToast() {
  /**
   * Show a toast notification with custom configuration
   */
  const showToast = async (options: ToastOptions): Promise<void> => {
    const {
      message,
      type = 'info',
      duration = DEFAULT_DURATIONS[type],
      position = 'top',
    } = options;

    const toast = await toastController.create({
      message,
      duration,
      color: TOAST_COLORS[type],
      position,
    });

    await toast.present();
  };

  /**
   * Show a success toast (green, 2 seconds)
   */
  const showSuccess = async (message: string, duration?: number): Promise<void> => {
    await showToast({
      message,
      type: 'success',
      duration,
    });
  };

  /**
   * Show an error toast (red, 3 seconds)
   */
  const showError = async (message: string, duration?: number): Promise<void> => {
    await showToast({
      message,
      type: 'error',
      duration,
    });
  };

  /**
   * Show an info toast (blue, 2.5 seconds)
   */
  const showInfo = async (message: string, duration?: number): Promise<void> => {
    await showToast({
      message,
      type: 'info',
      duration,
    });
  };

  /**
   * Show a warning toast (yellow, 3 seconds)
   */
  const showWarning = async (message: string, duration?: number): Promise<void> => {
    await showToast({
      message,
      type: 'warning',
      duration,
    });
  };

  return {
    showToast,
    showSuccess,
    showError,
    showInfo,
    showWarning,
  };
}
