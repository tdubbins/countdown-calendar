/**
 * useFormValidation Composable
 *
 * Provides reusable validation functions for form inputs across the application.
 * Centralizes validation logic to ensure consistent rules and error messages.
 *
 * Benefits:
 * - DRY principle: Single source of truth for validation rules
 * - Consistency: Same validation rules and error messages everywhere
 * - Maintainability: Update validation logic in one place
 * - Testability: Easy to unit test validation functions
 * - Type safety: TypeScript types for validation results
 *
 * Usage example:
 * ```typescript
 * const { validateEmail, validatePassword, validatePasswordMatch } = useFormValidation();
 *
 * // Validate email
 * const emailError = validateEmail(email.value);
 * if (emailError) {
 *   console.log('Email error:', emailError);
 * }
 *
 * // Validate password with complexity requirements
 * const passwordError = validatePassword(password.value, true);
 *
 * // Check if passwords match
 * const matchError = validatePasswordMatch(password.value, confirmPassword.value);
 * ```
 */

/**
 * Email validation regex
 * Matches basic email format: name@domain.ext
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Password complexity regex patterns
 */
const PASSWORD_REGEX = {
  uppercase: /[A-Z]/,
  lowercase: /[a-z]/,
  number: /\d/,
  minLength: 8
};

/**
 * useFormValidation Composable
 */
export function useFormValidation() {
  /**
   * Validate email address format
   *
   * Checks if email is provided and matches standard email format.
   *
   * @param email - Email address to validate
   * @returns Error message string, or empty string if valid
   *
   * @example
   * validateEmail('') // 'Email is required'
   * validateEmail('invalid') // 'Please enter a valid email address'
   * validateEmail('test@example.com') // ''
   */
  const validateEmail = (email: string): string => {
    if (!email) {
      return 'Email is required';
    }

    if (!EMAIL_REGEX.test(email)) {
      return 'Please enter a valid email address';
    }

    return '';
  };

  /**
   * Validate password
   *
   * Checks if password meets length and optionally complexity requirements.
   *
   * @param password - Password to validate
   * @param requireComplexity - Whether to enforce complexity rules (uppercase, lowercase, number)
   * @returns Error message string, or empty string if valid
   *
   * @example
   * validatePassword('') // 'Password is required'
   * validatePassword('short') // 'Password must be at least 8 characters'
   * validatePassword('password123', true) // 'Password must contain an uppercase letter'
   * validatePassword('Password123', true) // ''
   */
  const validatePassword = (password: string, requireComplexity: boolean = false): string => {
    if (!password) {
      return 'Password is required';
    }

    if (password.length < PASSWORD_REGEX.minLength) {
      return `Password must be at least ${PASSWORD_REGEX.minLength} characters`;
    }

    if (requireComplexity) {
      if (!PASSWORD_REGEX.uppercase.test(password)) {
        return 'Password must contain an uppercase letter';
      }

      if (!PASSWORD_REGEX.lowercase.test(password)) {
        return 'Password must contain a lowercase letter';
      }

      if (!PASSWORD_REGEX.number.test(password)) {
        return 'Password must contain a number';
      }
    }

    return '';
  };

  /**
   * Validate password confirmation match
   *
   * Checks if confirm password field matches the original password.
   *
   * @param password - Original password
   * @param confirmPassword - Confirmation password
   * @returns Error message string, or empty string if valid
   *
   * @example
   * validatePasswordMatch('pass', '') // 'Please confirm your password'
   * validatePasswordMatch('pass1', 'pass2') // 'Passwords do not match'
   * validatePasswordMatch('pass', 'pass') // ''
   */
  const validatePasswordMatch = (password: string, confirmPassword: string): string => {
    if (!confirmPassword) {
      return 'Please confirm your password';
    }

    if (password !== confirmPassword) {
      return 'Passwords do not match';
    }

    return '';
  };

  /**
   * Check if password meets complexity requirements
   *
   * Returns an object with boolean flags for each requirement.
   * Useful for showing real-time password strength indicators.
   *
   * @param password - Password to check
   * @returns Object with requirement flags
   *
   * @example
   * checkPasswordComplexity('pass') // { hasMinLength: false, hasUppercase: false, ... }
   * checkPasswordComplexity('Password123') // { hasMinLength: true, hasUppercase: true, ... }
   */
  const checkPasswordComplexity = (password: string) => {
    return {
      hasMinLength: password.length >= PASSWORD_REGEX.minLength,
      hasUppercase: PASSWORD_REGEX.uppercase.test(password),
      hasLowercase: PASSWORD_REGEX.lowercase.test(password),
      hasNumber: PASSWORD_REGEX.number.test(password),
      isValid: password.length >= PASSWORD_REGEX.minLength &&
               PASSWORD_REGEX.uppercase.test(password) &&
               PASSWORD_REGEX.lowercase.test(password) &&
               PASSWORD_REGEX.number.test(password)
    };
  };

  /**
   * Validate required field
   *
   * Generic validation for any required field.
   *
   * @param value - Value to validate
   * @param fieldName - Name of the field for error message
   * @returns Error message string, or empty string if valid
   *
   * @example
   * validateRequired('', 'Name') // 'Name is required'
   * validateRequired('John', 'Name') // ''
   */
  const validateRequired = (value: string, fieldName: string): string => {
    if (!value || value.trim() === '') {
      return `${fieldName} is required`;
    }
    return '';
  };

  return {
    validateEmail,
    validatePassword,
    validatePasswordMatch,
    checkPasswordComplexity,
    validateRequired
  };
}
