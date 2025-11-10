/**
 * Jest Global Type Declarations
 *
 * Extends the global namespace with Jest-specific types for testing environment
 */

declare global {
  // eslint-disable-next-line no-var
  var fetch: jest.Mock;
}

export {};
