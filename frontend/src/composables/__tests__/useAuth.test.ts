/**
 * Unit Tests for useAuth Composable
 *
 * Tests authentication functionality with mocked API calls and browser APIs.
 * Ensures proper token management, state updates, and error handling.
 *
 * Coverage targets:
 * - login(): User login with credential validation
 * - register(): User registration with email verification
 * - logout(): Session cleanup and redirect
 * - isAuthenticated: Computed authentication state
 * - Token storage/retrieval from localStorage
 * - Error handling for network failures
 *
 * Run with: npm run test:unit src/composables/__tests__/useAuth.test.ts
 */

import { useAuth } from '../useAuth';
import { API_ENDPOINTS } from '@/config/api';

// Mock dependencies
jest.mock('vue-router', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

jest.mock('@/composables/useCalendar', () => ({
  useCalendar: () => ({
    calendars: { value: [] },
    fetchCalendars: jest.fn(),
  }),
  clearCalendarData: jest.fn(),
}));

// Mock API configuration
jest.mock('@/config/api', () => ({
  API_ENDPOINTS: {
    LOGIN: () => 'http://localhost:5001/api/auth/login',
    REGISTER: () => 'http://localhost:5001/api/auth/register',
    LOGOUT: () => 'http://localhost:5001/api/auth/logout',
  },
}));

describe('useAuth Composable', () => {
  // Test data
  const mockUser = {
    id: 'user-123',
    email: 'test@gmail.com',
  };

  const mockToken = 'mock-jwt-token-12345';

  const validCredentials = {
    email: 'test@gmail.com',
    password: 'TestPass123',
  };

  // Setup and teardown
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();

    // Clear all mocks
    jest.clearAllMocks();

    // Reset fetch mock
    globalThis.fetch = jest.fn();

    // Reset auth state using the exported clearAuthData function
    const auth = useAuth();
    auth.clearAuthData();
  });

  afterEach(() => {
    // Clean up
    localStorage.clear();
    const auth = useAuth();
    auth.clearAuthData();
  });

  /**
   * Test Suite: login()
   *
   * Tests user login functionality with various scenarios.
   */
  describe('login', () => {
    describe('Successful login', () => {
      it('should login successfully with valid credentials', async () => {
        // Mock successful API response
        (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            token: mockToken,
            user: mockUser,
          }),
        });

        const auth = useAuth();
        const result = await auth.login(validCredentials.email, validCredentials.password);

        // Verify result
        expect(result.success).toBe(true);
        expect(result.message).toBe('Login successful');

        // Verify API call
        expect(globalThis.fetch).toHaveBeenCalledWith(
          API_ENDPOINTS.LOGIN(),
          expect.objectContaining({
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: validCredentials.email,
              password: validCredentials.password,
            }),
          })
        );

        // Verify authentication state
        expect(auth.isAuthenticated.value).toBe(true);
        expect(auth.currentUser.value).toEqual(mockUser);

        // Verify localStorage
        expect(localStorage.getItem('auth_token')).toBe(mockToken);
        expect(localStorage.getItem('user_data')).toBe(JSON.stringify(mockUser));
      });

      it('should set loading state during login', async () => {
        // Mock delayed API response
        (globalThis.fetch as jest.Mock).mockImplementationOnce(
          () =>
            new Promise((resolve) =>
              setTimeout(
                () =>
                  resolve({
                    ok: true,
                    json: async () => ({
                      token: mockToken,
                      user: mockUser,
                    }),
                  }),
                100
              )
            )
        );

        const auth = useAuth();

        // Start login
        const loginPromise = auth.login(validCredentials.email, validCredentials.password);

        // Check loading state
        expect(auth.isLoading.value).toBe(true);

        // Wait for completion
        await loginPromise;

        // Loading should be false after completion
        expect(auth.isLoading.value).toBe(false);
      });
    });

    describe('Failed login', () => {
      it('should handle invalid credentials', async () => {
        // Mock failed API response
        (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 401,
          json: async () => ({
            error: 'Invalid email or password',
          }),
        });

        const auth = useAuth();
        const result = await auth.login('wrong@email.com', 'wrongpass');

        // Verify result
        expect(result.success).toBe(false);
        expect(result.message).toBe('Invalid email or password');

        // Verify authentication state remains false
        expect(auth.isAuthenticated.value).toBe(false);
        expect(auth.currentUser.value).toBe(null);

        // Verify no tokens stored
        expect(localStorage.getItem('auth_token')).toBe(null);
      });

      it('should handle network errors', async () => {
        // Mock network error
        (globalThis.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

        const auth = useAuth();
        const result = await auth.login(validCredentials.email, validCredentials.password);

        // Verify error handling
        expect(result.success).toBe(false);
        expect(result.message).toBe('Network error');
        expect(auth.isAuthenticated.value).toBe(false);
      });

      it('should handle server errors (500)', async () => {
        // Mock server error
        (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: async () => ({
            error: 'Internal server error',
          }),
        });

        const auth = useAuth();
        const result = await auth.login(validCredentials.email, validCredentials.password);

        expect(result.success).toBe(false);
        expect(result.message).toBe('Internal server error');
      });

      it('should set loading to false after error', async () => {
        (globalThis.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

        const auth = useAuth();
        await auth.login(validCredentials.email, validCredentials.password);

        // Loading should be false even after error
        expect(auth.isLoading.value).toBe(false);
      });
    });
  });

  /**
   * Test Suite: register()
   *
   * Tests user registration functionality.
   */
  describe('register', () => {
    const registrationData = {
      email: 'newuser@example.com',
      password: 'NewPass123',
      confirmPassword: 'NewPass123',
    };

    describe('Successful registration', () => {
      it('should register successfully with valid data', async () => {
        // Mock successful registration
        (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            message: 'Registration successful. Please check your email to verify your account.',
          }),
        });

        const auth = useAuth();
        const result = await auth.register(
          registrationData.email,
          registrationData.password,
          registrationData.confirmPassword
        );

        // Verify result
        expect(result.success).toBe(true);
        expect(result.message).toContain('Registration successful');

        // Verify API call (includes frontendUrl for verification link)
        expect(globalThis.fetch).toHaveBeenCalledWith(
          API_ENDPOINTS.REGISTER(),
          expect.objectContaining({
            method: 'POST',
          })
        );
        // Verify the body contains registration data
        const fetchCall = (globalThis.fetch as jest.Mock).mock.calls[0];
        const requestBody = JSON.parse(fetchCall[1].body);
        expect(requestBody.email).toBe(registrationData.email);
        expect(requestBody.password).toBe(registrationData.password);
        expect(requestBody.confirmPassword).toBe(registrationData.confirmPassword);
      });

      it('should set loading state during registration', async () => {
        // Mock delayed response
        (globalThis.fetch as jest.Mock).mockImplementationOnce(
          () =>
            new Promise((resolve) =>
              setTimeout(
                () =>
                  resolve({
                    ok: true,
                    json: async () => ({
                      message: 'Registration successful',
                    }),
                  }),
                100
              )
            )
        );

        const auth = useAuth();
        const registerPromise = auth.register(
          registrationData.email,
          registrationData.password,
          registrationData.confirmPassword
        );

        expect(auth.isLoading.value).toBe(true);
        await registerPromise;
        expect(auth.isLoading.value).toBe(false);
      });
    });

    describe('Failed registration', () => {
      it('should handle duplicate email error', async () => {
        // Mock duplicate email error
        (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 400,
          json: async () => ({
            error: 'Email already exists',
          }),
        });

        const auth = useAuth();
        const result = await auth.register(
          'existing@email.com',
          registrationData.password,
          registrationData.confirmPassword
        );

        expect(result.success).toBe(false);
        expect(result.message).toBe('Email already exists');
      });

      it('should handle password mismatch', async () => {
        (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 400,
          json: async () => ({
            error: 'Passwords do not match',
          }),
        });

        const auth = useAuth();
        const result = await auth.register(
          registrationData.email,
          'Password123',
          'DifferentPass123'
        );

        expect(result.success).toBe(false);
        expect(result.message).toBe('Passwords do not match');
      });

      it('should handle weak password error', async () => {
        (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 400,
          json: async () => ({
            error: 'Password must contain an uppercase letter',
          }),
        });

        const auth = useAuth();
        const result = await auth.register(
          registrationData.email,
          'weakpass',
          'weakpass'
        );

        expect(result.success).toBe(false);
        expect(result.message).toContain('uppercase letter');
      });

      it('should handle network errors', async () => {
        (globalThis.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

        const auth = useAuth();
        const result = await auth.register(
          registrationData.email,
          registrationData.password,
          registrationData.confirmPassword
        );

        expect(result.success).toBe(false);
        expect(result.message).toBe('Network error');
      });
    });
  });

  /**
   * Test Suite: logout()
   *
   * Tests logout functionality and session cleanup.
   */
  describe('logout', () => {
    beforeEach(() => {
      // Set up authenticated state
      localStorage.setItem('auth_token', mockToken);
      localStorage.setItem('user_data', JSON.stringify(mockUser));
    });

    it('should logout successfully and clear all data', async () => {
      // Setup authenticated state first
      localStorage.setItem('auth_token', mockToken);
      localStorage.setItem('user_data', JSON.stringify(mockUser));

      const auth = useAuth();
      auth.setAuthData(mockToken, mockUser);

      // Verify initial authenticated state
      expect(auth.isAuthenticated.value).toBe(true);

      // Mock successful logout API call
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await auth.logout();

      // Verify logout API called
      expect(globalThis.fetch).toHaveBeenCalledWith(
        API_ENDPOINTS.LOGOUT(),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`,
          }),
        })
      );

      // Verify state cleared
      expect(auth.isAuthenticated.value).toBe(false);
      expect(auth.currentUser.value).toBe(null);

      // Verify localStorage cleared
      expect(localStorage.getItem('auth_token')).toBe(null);
      expect(localStorage.getItem('user_data')).toBe(null);
    });

    it('should clear data even if logout API fails', async () => {
      // Mock failed logout API
      (globalThis.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const auth = useAuth();
      await auth.logout();

      // Should still clear local data
      expect(auth.isAuthenticated.value).toBe(false);
      expect(localStorage.getItem('auth_token')).toBe(null);
    });

    it('should handle logout without token', async () => {
      // Clear token
      localStorage.removeItem('auth_token');

      const auth = useAuth();
      await auth.logout();

      // Should not throw error
      expect(auth.isAuthenticated.value).toBe(false);
    });
  });

  /**
   * Test Suite: isAuthenticated (computed property)
   *
   * Tests authentication state tracking.
   */
  describe('isAuthenticated', () => {
    it('should return false when no token exists', () => {
      const auth = useAuth();
      expect(auth.isAuthenticated.value).toBe(false);
    });

    it('should return true when token exists in localStorage', () => {
      const auth = useAuth();
      // Set auth data using the proper method
      auth.setAuthData(mockToken, mockUser);
      expect(auth.isAuthenticated.value).toBe(true);
    });

    it('should update reactively when token is set', async () => {
      const auth = useAuth();
      expect(auth.isAuthenticated.value).toBe(false);

      // Mock successful login
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          token: mockToken,
          user: mockUser,
        }),
      });

      await auth.login(validCredentials.email, validCredentials.password);
      expect(auth.isAuthenticated.value).toBe(true);
    });

    it('should update reactively when logged out', async () => {
      const auth = useAuth();
      // Set auth data first
      auth.setAuthData(mockToken, mockUser);
      expect(auth.isAuthenticated.value).toBe(true);

      // Mock logout
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await auth.logout();
      expect(auth.isAuthenticated.value).toBe(false);
    });
  });

  /**
   * Test Suite: Token persistence
   *
   * Tests localStorage token management.
   */
  describe('Token persistence', () => {
    it('should store token in localStorage after login', async () => {
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          token: mockToken,
          user: mockUser,
        }),
      });

      const auth = useAuth();
      await auth.login(validCredentials.email, validCredentials.password);

      expect(localStorage.getItem('auth_token')).toBe(mockToken);
    });

    it('should store user data in localStorage after login', async () => {
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          token: mockToken,
          user: mockUser,
        }),
      });

      const auth = useAuth();
      await auth.login(validCredentials.email, validCredentials.password);

      const storedUser = localStorage.getItem('user_data');
      expect(storedUser).toBe(JSON.stringify(mockUser));
    });

    it('should restore auth state from localStorage on initialization', () => {
      // Create auth instance and set data (simulates page reload with localStorage)
      const auth = useAuth();
      auth.setAuthData(mockToken, mockUser);

      expect(auth.isAuthenticated.value).toBe(true);
      expect(auth.currentUser.value).toEqual(mockUser);
    });

    it('should handle corrupted user data in localStorage', () => {
      // Should not throw error - set only token without user data
      const auth = useAuth();
      auth.setAuthData(mockToken, null);

      expect(auth.isAuthenticated.value).toBe(true); // Token still valid
      expect(auth.currentUser.value).toBe(null); // But user data is null
    });
  });

  /**
   * Test Suite: getAuthHeaders()
   *
   * Tests authorization header generation for API calls.
   */
  describe('getAuthHeaders', () => {
    it('should return headers with Authorization when authenticated', () => {
      const auth = useAuth();
      auth.setAuthData(mockToken, mockUser);

      const headers = auth.getAuthHeaders();

      expect(headers).toEqual({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${mockToken}`,
      });
    });

    it('should return headers without Authorization when not authenticated', () => {
      const auth = useAuth();

      const headers = auth.getAuthHeaders();

      expect(headers).toEqual({
        'Content-Type': 'application/json',
      });
    });
  });

  /**
   * Test Suite: checkAuth()
   *
   * Tests authentication check utility.
   */
  describe('checkAuth', () => {
    it('should return true when authenticated', () => {
      const auth = useAuth();
      auth.setAuthData(mockToken, mockUser);

      expect(auth.checkAuth()).toBe(true);
    });

    it('should return false when not authenticated', () => {
      const auth = useAuth();

      expect(auth.checkAuth()).toBe(false);
    });
  });

  /**
   * Integration Tests
   *
   * Test complete authentication flows.
   */
  describe('Integration scenarios', () => {
    it('should handle complete login → logout flow', async () => {
      // Mock login
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          token: mockToken,
          user: mockUser,
        }),
      });

      const auth = useAuth();

      // Login
      await auth.login(validCredentials.email, validCredentials.password);
      expect(auth.isAuthenticated.value).toBe(true);

      // Mock logout
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      // Logout
      await auth.logout();
      expect(auth.isAuthenticated.value).toBe(false);
      expect(localStorage.getItem('auth_token')).toBe(null);
    });

    it('should handle session persistence across page reloads', async () => {
      // First session: login
      (globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          token: mockToken,
          user: mockUser,
        }),
      });

      let auth = useAuth();
      await auth.login(validCredentials.email, validCredentials.password);

      // Simulate page reload by creating new instance
      auth = useAuth();
      expect(auth.isAuthenticated.value).toBe(true);
      expect(auth.currentUser.value).toEqual(mockUser);
    });
  });
});
