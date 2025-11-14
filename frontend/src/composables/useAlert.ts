/**
 * useAlert Composable
 *
 * Provides a reusable, consistent alert dialog system across the application.
 * Centralizes alert creation logic to ensure consistent UX and simplify maintenance.
 *
 * Benefits:
 * - DRY principle: Single source of truth for alert configuration
 * - Consistency: All alerts have same appearance and behavior
 * - Maintainability: Update alert behavior in one place
 * - Accessibility: Centralized ARIA and keyboard support
 * - Type safety: TypeScript types for alert variants
 *
 * Usage example:
 * ```typescript
 * const { showError, showConfirm } = useAlert();
 *
 * // Simple error alert
 * await showError('Failed to load data');
 *
 * // Error with custom header and button
 * await showError('Network error occurred', {
 *   header: 'Connection Failed',
 *   buttonText: 'Retry'
 * });
 *
 * // Confirmation dialog
 * await showConfirm(
 *   'Are you sure you want to delete this item?',
 *   () => console.log('Confirmed!')
 * );
 * ```
 */

import { alertController } from '@ionic/vue';

/**
 * Options for error alerts
 */
export interface ErrorAlertOptions {
  header?: string;
  buttonText?: string;
}

/**
 * Options for confirmation alerts
 */
export interface ConfirmAlertOptions {
  header?: string;
  confirmText?: string;
  cancelText?: string;
  confirmColor?: 'primary' | 'danger' | 'warning';
}

/**
 * useAlert Composable
 */
export function useAlert() {
  /**
   * Show a simple error alert dialog
   *
   * Displays an error message with a single dismiss button.
   * Default header is "Error", default button text is "OK".
   *
   * @param message - Error message to display
   * @param options - Optional customization options
   */
  const showError = async (
    message: string,
    options: ErrorAlertOptions = {}
  ): Promise<void> => {
    const {
      header = 'Error',
      buttonText = 'OK'
    } = options;

    const alert = await alertController.create({
      header,
      message,
      buttons: [buttonText]
    });

    await alert.present();
  };

  /**
   * Show a confirmation dialog with cancel/confirm options
   *
   * Displays a message with two buttons: Cancel and Confirm.
   * Only calls onConfirm callback if user clicks confirm button.
   *
   * @param message - Confirmation message to display
   * @param onConfirm - Callback function to execute when confirmed
   * @param options - Optional customization options
   */
  const showConfirm = async (
    message: string,
    onConfirm: () => void | Promise<void>,
    options: ConfirmAlertOptions = {}
  ): Promise<void> => {
    const {
      header = 'Confirm',
      confirmText = 'Confirm',
      cancelText = 'Cancel',
      confirmColor = 'primary'
    } = options;

    const alert = await alertController.create({
      header,
      message,
      buttons: [
        {
          text: cancelText,
          role: 'cancel'
        },
        {
          text: confirmText,
          handler: onConfirm,
          cssClass: `alert-button-${confirmColor}`
        }
      ]
    });

    await alert.present();
  };

  /**
   * Show an info alert dialog
   *
   * Similar to error alert but with "Info" as default header.
   * Useful for non-error informational messages.
   *
   * @param message - Information message to display
   * @param options - Optional customization options
   */
  const showInfo = async (
    message: string,
    options: ErrorAlertOptions = {}
  ): Promise<void> => {
    const {
      header = 'Info',
      buttonText = 'OK'
    } = options;

    const alert = await alertController.create({
      header,
      message,
      buttons: [buttonText]
    });

    await alert.present();
  };

  /**
   * Show a warning alert dialog
   *
   * Similar to error alert but with "Warning" as default header.
   * Useful for warning messages that require acknowledgment.
   *
   * @param message - Warning message to display
   * @param options - Optional customization options
   */
  const showWarning = async (
    message: string,
    options: ErrorAlertOptions = {}
  ): Promise<void> => {
    const {
      header = 'Warning',
      buttonText = 'OK'
    } = options;

    const alert = await alertController.create({
      header,
      message,
      buttons: [buttonText]
    });

    await alert.present();
  };

  return {
    showError,
    showConfirm,
    showInfo,
    showWarning
  };
}
