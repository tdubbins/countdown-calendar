/**
 * Unit Tests for Validators Utility
 *
 * Run with: npm run test:unit
 */

// Jest provides describe, it, expect as globals
import {
  validateEmail,
  validatePassword,
  validatePasswordsMatch,
  checkPasswordRequirements,
  EMAIL_REGEX
} from '../validators';

describe('validateEmail', () => {
  it('should validate correct email addresses', () => {
    const validEmails = [
      'user@example.com',
      'test.user@example.co.uk',
      'user+tag@example.com',
      'user_name@example.com',
      '123@example.com'
    ];

    validEmails.forEach(email => {
      const result = validateEmail(email);
      expect(result.isValid).toBe(true);
      expect(result.error).toBe('');
    });
  });

  it('should reject empty email', () => {
    const result = validateEmail('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Email is required');
  });

  it('should reject whitespace-only email', () => {
    const result = validateEmail('   ');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Email is required');
  });

  it('should reject invalid email formats', () => {
    const invalidEmails = [
      'notanemail',
      '@example.com',
      'user@',
      'user @example.com',
      'user@example'
    ];

    invalidEmails.forEach(email => {
      const result = validateEmail(email);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('valid email');
    });
  });

  it('should accept emails with consecutive dots in local part', () => {
    // The regex allows this - it's technically valid per RFC 5321
    const result = validateEmail('user..name@example.com');
    expect(result.isValid).toBe(true);
  });

  it('should trim whitespace from email', () => {
    const result = validateEmail('  user@example.com  ');
    expect(result.isValid).toBe(true);
  });
});

describe('validatePassword', () => {
  it('should validate strong password', () => {
    const result = validatePassword('StrongPass123');
    expect(result.isValid).toBe(true);
    expect(result.error).toBe('');
  });

  it('should reject empty password', () => {
    const result = validatePassword('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Password is required');
  });

  it('should reject password shorter than 8 characters', () => {
    const result = validatePassword('Pass1');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('8 characters');
  });

  it('should reject password without uppercase', () => {
    const result = validatePassword('password123');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('uppercase');
  });

  it('should reject password without lowercase', () => {
    const result = validatePassword('PASSWORD123');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('lowercase');
  });

  it('should reject password without number', () => {
    const result = validatePassword('PasswordOnly');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('number');
  });
});

describe('validatePasswordsMatch', () => {
  it('should validate matching passwords', () => {
    const result = validatePasswordsMatch('Password123', 'Password123');
    expect(result.isValid).toBe(true);
    expect(result.error).toBe('');
  });

  it('should reject empty confirm password', () => {
    const result = validatePasswordsMatch('Password123', '');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('confirm');
  });

  it('should reject non-matching passwords', () => {
    const result = validatePasswordsMatch('Password123', 'Password456');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('do not match');
  });

  it('should be case-sensitive', () => {
    const result = validatePasswordsMatch('Password123', 'password123');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('do not match');
  });
});

describe('checkPasswordRequirements', () => {
  it('should return all requirements met for strong password', () => {
    const result = checkPasswordRequirements('StrongPass123');
    expect(result.hasMinLength).toBe(true);
    expect(result.hasUppercase).toBe(true);
    expect(result.hasLowercase).toBe(true);
    expect(result.hasNumber).toBe(true);
    expect(result.isValid).toBe(true);
  });

  it('should identify missing minimum length', () => {
    const result = checkPasswordRequirements('Pass1');
    expect(result.hasMinLength).toBe(false);
    expect(result.isValid).toBe(false);
  });

  it('should identify missing uppercase', () => {
    const result = checkPasswordRequirements('password123');
    expect(result.hasUppercase).toBe(false);
    expect(result.isValid).toBe(false);
  });

  it('should identify missing lowercase', () => {
    const result = checkPasswordRequirements('PASSWORD123');
    expect(result.hasLowercase).toBe(false);
    expect(result.isValid).toBe(false);
  });

  it('should identify missing number', () => {
    const result = checkPasswordRequirements('PasswordOnly');
    expect(result.hasNumber).toBe(false);
    expect(result.isValid).toBe(false);
  });

  it('should work with empty password', () => {
    const result = checkPasswordRequirements('');
    expect(result.hasMinLength).toBe(false);
    expect(result.hasUppercase).toBe(false);
    expect(result.hasLowercase).toBe(false);
    expect(result.hasNumber).toBe(false);
    expect(result.isValid).toBe(false);
  });
});

describe('EMAIL_REGEX', () => {
  it('should be exported and work correctly', () => {
    expect(EMAIL_REGEX.test('user@example.com')).toBe(true);
    expect(EMAIL_REGEX.test('invalid')).toBe(false);
  });
});
