/**
 * Jest Setup Configuration
 *
 * This file runs before all tests to configure the test environment.
 * It sets up global mocks for browser APIs.
 */

// Initialize global fetch mock
(global as any).fetch = jest.fn();

// Export to make this a module
export {};
