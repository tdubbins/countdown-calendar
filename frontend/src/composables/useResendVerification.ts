/**
 * Resend Verification Email Composable
 *
 * Centralized logic for resending email verification links.
 * Eliminates code duplication between LoginPage and EmailVerificationPage.
 *
 * NFR Compliance:
 * - [SC3] Modular architecture - DRY principle
 * - [S4] Input validation
 */

import { ref } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from '@/utils/constants';

/**
 * Composable for resending verification emails
 *
 * @returns Object with state and resend function
 *
 * @example
 * const { isResending, message, messageType, resend } = useResendVerification();
 *
 * // Simple resend
 * await resend('user@example.com');
 *
 * // With success callback
 * await resend('user@example.com', () => {
 *   console.log('Email sent successfully!');
 * });
 */
export const useResendVerification = () => {
  // State
  const isResending = ref(false);
  const message = ref('');
  const messageType = ref<'success' | 'error'>('success');

  // Auth composable for API call
  const { resendVerificationEmail } = useAuth();

  /**
   * Resend verification email
   *
   * @param email - Email address to send verification to
   * @param onSuccess - Optional callback to run on successful send
   * @returns Promise with success status and message
   */
  const resend = async (
    email: string,
    onSuccess?: () => void
  ): Promise<{ success: boolean; message: string }> => {
    // Clear previous messages
    message.value = '';
    isResending.value = true;

    try {
      // Call API to resend verification email
      const result = await resendVerificationEmail(email);

      // Set message based on result
      if (result.success) {
        message.value = result.message || SUCCESS_MESSAGES.VERIFICATION_EMAIL_SENT;
        messageType.value = 'success';

        // Run success callback if provided
        if (onSuccess) {
          onSuccess();
        }
      } else {
        // Handle specific error messages
        if (result.message.toLowerCase().includes('too many')) {
          message.value = ERROR_MESSAGES.RESEND_RATE_LIMIT;
        } else {
          message.value = result.message || ERROR_MESSAGES.RESEND_VERIFICATION_FAILED;
        }
        messageType.value = 'error';
      }

      return result;
    } catch (error: any) {
      // Handle network or unexpected errors
      message.value = ERROR_MESSAGES.RESEND_VERIFICATION_FAILED;
      messageType.value = 'error';

      return {
        success: false,
        message: message.value
      };
    } finally {
      isResending.value = false;
    }
  };

  /**
   * Clear message state
   */
  const clearMessage = () => {
    message.value = '';
  };

  return {
    // State
    isResending,
    message,
    messageType,

    // Actions
    resend,
    clearMessage
  };
};
