/**
 * Unit Tests for useFormValidation Composable
 *
 * Tests all form validation functions with comprehensive edge cases.
 * Ensures consistent validation rules across registration, login, and other forms.
 *
 * Coverage targets:
 * - validateEmail(): Email format validation
 * - validatePassword(): Password strength validation (with/without complexity)
 * - validatePasswordMatch(): Password confirmation matching
 * - checkPasswordComplexity(): Returns complexity requirement flags
 * - validateRequired(): Generic required field validation
 *
 * Run with: npm run test:unit src/composables/__tests__/useFormValidation.test.ts
 */

import { useFormValidation } from '../useFormValidation';

describe('useFormValidation Composable', () => {
  // Create a fresh instance for each test to ensure isolation
  let validation: ReturnType<typeof useFormValidation>;

  beforeEach(() => {
    validation = useFormValidation();
  });

  /**
   * Test Suite: validateEmail()
   *
   * Email validation ensures proper email format and required field check.
   */
  describe('validateEmail', () => {
    describe('Valid emails', () => {
      it('should accept standard email format', () => {
        expect(validation.validateEmail('test@example.com')).toBe('');
        expect(validation.validateEmail('user@domain.org')).toBe('');
        expect(validation.validateEmail('name@company.co.uk')).toBe('');
      });

      it('should accept emails with numbers', () => {
        expect(validation.validateEmail('user123@example.com')).toBe('');
        expect(validation.validateEmail('test456@gmail.com')).toBe('');
      });

      it('should accept emails with dots and hyphens', () => {
        expect(validation.validateEmail('first.last@example.com')).toBe('');
        expect(validation.validateEmail('user-name@domain.com')).toBe('');
      });

      it('should accept emails with plus signs (Gmail alias)', () => {
        expect(validation.validateEmail('user+tag@gmail.com')).toBe('');
      });
    });

    describe('Invalid emails', () => {
      it('should reject empty email', () => {
        expect(validation.validateEmail('')).toBe('Email is required');
      });

      it('should reject email without @ symbol', () => {
        expect(validation.validateEmail('invalidemail.com')).toBe('Please enter a valid email address');
      });

      it('should reject email without domain', () => {
        expect(validation.validateEmail('user@')).toBe('Please enter a valid email address');
      });

      it('should reject email without username', () => {
        expect(validation.validateEmail('@example.com')).toBe('Please enter a valid email address');
      });

      it('should reject email without TLD', () => {
        expect(validation.validateEmail('user@domain')).toBe('Please enter a valid email address');
      });

      it('should reject email with spaces', () => {
        expect(validation.validateEmail('user name@example.com')).toBe('Please enter a valid email address');
        expect(validation.validateEmail('user@exam ple.com')).toBe('Please enter a valid email address');
      });

      it('should reject email with multiple @ symbols', () => {
        expect(validation.validateEmail('user@@example.com')).toBe('Please enter a valid email address');
      });
    });

    describe('Edge cases', () => {
      it('should reject whitespace-only input', () => {
        // Whitespace emails fail the regex check, not the empty check
        expect(validation.validateEmail('   ')).toBe('Please enter a valid email address');
      });

      it('should handle very long email addresses', () => {
        const longEmail = 'a'.repeat(50) + '@' + 'b'.repeat(50) + '.com';
        // Should accept if format is valid, regardless of length
        expect(validation.validateEmail(longEmail)).toBe('');
      });
    });
  });

  /**
   * Test Suite: validatePassword()
   *
   * Password validation with optional complexity requirements.
   */
  describe('validatePassword', () => {
    describe('Basic validation (no complexity)', () => {
      it('should accept passwords with 8+ characters', () => {
        expect(validation.validatePassword('password')).toBe('');
        expect(validation.validatePassword('12345678')).toBe('');
        expect(validation.validatePassword('abcdefgh')).toBe('');
      });

      it('should reject empty password', () => {
        expect(validation.validatePassword('')).toBe('Password is required');
      });

      it('should reject passwords shorter than 8 characters', () => {
        expect(validation.validatePassword('short')).toBe('Password must be at least 8 characters');
        expect(validation.validatePassword('1234567')).toBe('Password must be at least 8 characters');
      });
    });

    describe('Complexity validation (requireComplexity = true)', () => {
      it('should accept passwords meeting all requirements', () => {
        expect(validation.validatePassword('Password123', true)).toBe('');
        expect(validation.validatePassword('Test1234', true)).toBe('');
        expect(validation.validatePassword('MyPass99', true)).toBe('');
      });

      it('should reject password without uppercase letter', () => {
        expect(validation.validatePassword('password123', true)).toBe('Password must contain an uppercase letter');
      });

      it('should reject password without lowercase letter', () => {
        expect(validation.validatePassword('PASSWORD123', true)).toBe('Password must contain a lowercase letter');
      });

      it('should reject password without number', () => {
        expect(validation.validatePassword('Password', true)).toBe('Password must contain a number');
      });

      it('should reject password too short even if complex', () => {
        expect(validation.validatePassword('Pass1', true)).toBe('Password must be at least 8 characters');
      });
    });

    describe('Edge cases', () => {
      it('should handle special characters in passwords', () => {
        expect(validation.validatePassword('Pass@123', true)).toBe('');
        expect(validation.validatePassword('Test!#$%123', true)).toBe('');
      });

      it('should handle very long passwords', () => {
        const longPassword = 'Password123' + 'a'.repeat(100);
        expect(validation.validatePassword(longPassword, true)).toBe('');
      });

      it('should handle passwords with spaces', () => {
        expect(validation.validatePassword('Pass Word 123', true)).toBe('');
      });
    });

    describe('Real-world password examples', () => {
      it('should validate common password patterns', () => {
        // Test credential: TestPass123
        expect(validation.validatePassword('TestPass123', true)).toBe('');

        // Weak passwords that fail complexity
        expect(validation.validatePassword('password', true)).toBe('Password must contain an uppercase letter');
        expect(validation.validatePassword('PASSWORD', true)).toBe('Password must contain a lowercase letter');
        expect(validation.validatePassword('Password', true)).toBe('Password must contain a number');
      });
    });
  });

  /**
   * Test Suite: validatePasswordMatch()
   *
   * Ensures password and confirmation fields match.
   */
  describe('validatePasswordMatch', () => {
    describe('Matching passwords', () => {
      it('should accept matching passwords', () => {
        expect(validation.validatePasswordMatch('password', 'password')).toBe('');
        expect(validation.validatePasswordMatch('Test123', 'Test123')).toBe('');
        expect(validation.validatePasswordMatch('Complex@Pass1', 'Complex@Pass1')).toBe('');
      });
    });

    describe('Non-matching passwords', () => {
      it('should reject different passwords', () => {
        expect(validation.validatePasswordMatch('password1', 'password2')).toBe('Passwords do not match');
        expect(validation.validatePasswordMatch('Test123', 'test123')).toBe('Passwords do not match');
      });

      it('should reject empty confirmation password', () => {
        expect(validation.validatePasswordMatch('password', '')).toBe('Please confirm your password');
      });

      it('should be case-sensitive', () => {
        expect(validation.validatePasswordMatch('Password', 'password')).toBe('Passwords do not match');
      });
    });

    describe('Edge cases', () => {
      it('should handle passwords with special characters', () => {
        expect(validation.validatePasswordMatch('Pass@123', 'Pass@123')).toBe('');
        expect(validation.validatePasswordMatch('Pass@123', 'Pass#123')).toBe('Passwords do not match');
      });

      it('should handle passwords with spaces', () => {
        expect(validation.validatePasswordMatch('Pass 123', 'Pass 123')).toBe('');
        expect(validation.validatePasswordMatch('Pass 123', 'Pass  123')).toBe('Passwords do not match');
      });

      it('should handle very long passwords', () => {
        const longPass = 'Password123' + 'a'.repeat(100);
        expect(validation.validatePasswordMatch(longPass, longPass)).toBe('');
      });
    });
  });

  /**
   * Test Suite: checkPasswordComplexity()
   *
   * Returns object with boolean flags for each complexity requirement.
   */
  describe('checkPasswordComplexity', () => {
    describe('All requirements met', () => {
      it('should return all true flags for valid complex password', () => {
        const result = validation.checkPasswordComplexity('Password123');
        expect(result.hasMinLength).toBe(true);
        expect(result.hasUppercase).toBe(true);
        expect(result.hasLowercase).toBe(true);
        expect(result.hasNumber).toBe(true);
        expect(result.isValid).toBe(true);
      });
    });

    describe('Individual requirement failures', () => {
      it('should detect missing minimum length', () => {
        const result = validation.checkPasswordComplexity('Pass1');
        expect(result.hasMinLength).toBe(false);
        expect(result.hasUppercase).toBe(true);
        expect(result.hasLowercase).toBe(true);
        expect(result.hasNumber).toBe(true);
        expect(result.isValid).toBe(false);
      });

      it('should detect missing uppercase', () => {
        const result = validation.checkPasswordComplexity('password123');
        expect(result.hasMinLength).toBe(true);
        expect(result.hasUppercase).toBe(false);
        expect(result.hasLowercase).toBe(true);
        expect(result.hasNumber).toBe(true);
        expect(result.isValid).toBe(false);
      });

      it('should detect missing lowercase', () => {
        const result = validation.checkPasswordComplexity('PASSWORD123');
        expect(result.hasMinLength).toBe(true);
        expect(result.hasUppercase).toBe(true);
        expect(result.hasLowercase).toBe(false);
        expect(result.hasNumber).toBe(true);
        expect(result.isValid).toBe(false);
      });

      it('should detect missing number', () => {
        const result = validation.checkPasswordComplexity('Password');
        expect(result.hasMinLength).toBe(true);
        expect(result.hasUppercase).toBe(true);
        expect(result.hasLowercase).toBe(true);
        expect(result.hasNumber).toBe(false);
        expect(result.isValid).toBe(false);
      });
    });

    describe('Multiple requirement failures', () => {
      it('should detect multiple missing requirements', () => {
        const result = validation.checkPasswordComplexity('pass');
        expect(result.hasMinLength).toBe(false);
        expect(result.hasUppercase).toBe(false);
        expect(result.hasLowercase).toBe(true);
        expect(result.hasNumber).toBe(false);
        expect(result.isValid).toBe(false);
      });

      it('should handle empty password', () => {
        const result = validation.checkPasswordComplexity('');
        expect(result.hasMinLength).toBe(false);
        expect(result.hasUppercase).toBe(false);
        expect(result.hasLowercase).toBe(false);
        expect(result.hasNumber).toBe(false);
        expect(result.isValid).toBe(false);
      });
    });

    describe('Real-time validation use cases', () => {
      it('should provide feedback for progressive password entry', () => {
        // User types progressively
        let result = validation.checkPasswordComplexity('P');
        expect(result.isValid).toBe(false);

        result = validation.checkPasswordComplexity('Pass');
        expect(result.isValid).toBe(false);

        result = validation.checkPasswordComplexity('Passw');
        expect(result.isValid).toBe(false);

        result = validation.checkPasswordComplexity('Password');
        expect(result.isValid).toBe(false); // Still missing number

        result = validation.checkPasswordComplexity('Password1');
        expect(result.isValid).toBe(true); // All requirements met
      });
    });
  });

  /**
   * Test Suite: validateRequired()
   *
   * Generic required field validation with custom field names.
   */
  describe('validateRequired', () => {
    describe('Valid inputs', () => {
      it('should accept non-empty values', () => {
        expect(validation.validateRequired('value', 'Field')).toBe('');
        expect(validation.validateRequired('test', 'Name')).toBe('');
        expect(validation.validateRequired('123', 'Number')).toBe('');
      });

      it('should accept values with spaces when not empty', () => {
        expect(validation.validateRequired('Hello World', 'Message')).toBe('');
      });
    });

    describe('Invalid inputs', () => {
      it('should reject empty string', () => {
        expect(validation.validateRequired('', 'Name')).toBe('Name is required');
        expect(validation.validateRequired('', 'Email')).toBe('Email is required');
      });

      it('should reject whitespace-only values', () => {
        expect(validation.validateRequired('   ', 'Title')).toBe('Title is required');
        expect(validation.validateRequired('\t\n', 'Description')).toBe('Description is required');
      });
    });

    describe('Custom field names', () => {
      it('should use custom field name in error message', () => {
        expect(validation.validateRequired('', 'Calendar Title')).toBe('Calendar Title is required');
        expect(validation.validateRequired('', 'First Name')).toBe('First Name is required');
        expect(validation.validateRequired('', 'Phone Number')).toBe('Phone Number is required');
      });
    });

    describe('Edge cases', () => {
      it('should handle special characters in field names', () => {
        expect(validation.validateRequired('', 'Field Name (Optional)')).toBe('Field Name (Optional) is required');
      });

      it('should trim whitespace before validation', () => {
        expect(validation.validateRequired('  value  ', 'Field')).toBe('');
        expect(validation.validateRequired('     ', 'Field')).toBe('Field is required');
      });
    });
  });

  /**
   * Integration Tests
   *
   * Test multiple validation functions together as they would be used in forms.
   */
  describe('Integration scenarios', () => {
    describe('Registration form validation', () => {
      it('should validate complete registration form', () => {
        const email = 'test@gmail.com';
        const password = 'TestPass123';
        const confirmPassword = 'TestPass123';

        expect(validation.validateEmail(email)).toBe('');
        expect(validation.validatePassword(password, true)).toBe('');
        expect(validation.validatePasswordMatch(password, confirmPassword)).toBe('');
      });

      it('should catch all errors in invalid registration', () => {
        const email = 'invalid';
        const password = 'weak';
        const confirmPassword = 'different';

        expect(validation.validateEmail(email)).toBe('Please enter a valid email address');
        expect(validation.validatePassword(password, true)).toBe('Password must be at least 8 characters');
        expect(validation.validatePasswordMatch(password, confirmPassword)).toBe('Passwords do not match');
      });
    });

    describe('Login form validation', () => {
      it('should validate login credentials', () => {
        const email = 'test@gmail.com';
        const password = 'TestPass123';

        expect(validation.validateEmail(email)).toBe('');
        expect(validation.validatePassword(password, false)).toBe(''); // No complexity check for login
      });
    });

    describe('Password strength indicator', () => {
      it('should provide real-time complexity feedback', () => {
        const password = 'MyNewPass123';
        const complexity = validation.checkPasswordComplexity(password);
        const passwordError = validation.validatePassword(password, true);

        expect(complexity.isValid).toBe(true);
        expect(passwordError).toBe('');
      });
    });
  });
});
