/**
 * Input Validation Utilities
 *
 * Centralized validation functions for consistency across the app.
 */

/**
 * Email validation regex
 * Basic email format: user@domain.tld
 */
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  error: string;
}

/**
 * Validate email address format
 *
 * @param email - Email address to validate
 * @returns ValidationResult with isValid boolean and error message
 *
 * @example
 * const result = validateEmail('user@example.com');
 * if (!result.isValid) {
 *   console.error(result.error);
 * }
 */
export const validateEmail = (email: string): ValidationResult => {
  // Check if email is empty
  if (!email || email.trim() === '') {
    return {
      isValid: false,
      error: 'Email is required'
    };
  }

  // Check email format against regex
  if (!EMAIL_REGEX.test(email.trim())) {
    return {
      isValid: false,
      error: 'Please enter a valid email address'
    };
  }

  // Email is valid
  return {
    isValid: true,
    error: ''
  };
};

/**
 * Validate password strength
 * Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 number
 *
 * @param password - Password to validate
 * @returns ValidationResult with isValid boolean and error message
 */
export const validatePassword = (password: string): ValidationResult => {
  if (!password) {
    return {
      isValid: false,
      error: 'Password is required'
    };
  }

  if (password.length < 8) {
    return {
      isValid: false,
      error: 'Password must be at least 8 characters long'
    };
  }

  if (!/[A-Z]/.test(password)) {
    return {
      isValid: false,
      error: 'Password must contain at least one uppercase letter'
    };
  }

  if (!/[a-z]/.test(password)) {
    return {
      isValid: false,
      error: 'Password must contain at least one lowercase letter'
    };
  }

  if (!/\d/.test(password)) {
    return {
      isValid: false,
      error: 'Password must contain at least one number'
    };
  }

  return {
    isValid: true,
    error: ''
  };
};

/**
 * Check if password meets all requirements (for real-time validation)
 *
 * @param password - Password to check
 * @returns Object with individual requirement checks
 */
export const checkPasswordRequirements = (password: string) => {
  return {
    hasMinLength: password.length >= 8,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumber: /\d/.test(password),
    isValid: password.length >= 8 &&
             /[A-Z]/.test(password) &&
             /[a-z]/.test(password) &&
             /\d/.test(password)
  };
};

/**
 * Validate passwords match
 *
 * @param password - Original password
 * @param confirmPassword - Confirmation password
 * @returns ValidationResult with isValid boolean and error message
 */
export const validatePasswordsMatch = (
  password: string,
  confirmPassword: string
): ValidationResult => {
  if (!confirmPassword) {
    return {
      isValid: false,
      error: 'Please confirm your password'
    };
  }

  if (password !== confirmPassword) {
    return {
      isValid: false,
      error: 'Passwords do not match'
    };
  }

  return {
    isValid: true,
    error: ''
  };
};
