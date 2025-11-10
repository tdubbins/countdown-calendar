/**
 * E2E Tests for Authentication Flow
 *
 * Tests complete user authentication workflows including:
 * - User login with valid credentials
 * - Login failure with invalid credentials
 * - Navigation to registration page
 * - Logout functionality
 * - Session persistence
 *
 * Prerequisites:
 * - Backend API running at http://localhost:5001
 * - Test user exists: test@gmail.com / TestPass123
 * - Frontend dev server running
 *
 * Run with: npm run test:e2e
 */

describe('Authentication Flow', () => {
  // Configuration
  const TEST_USER = {
    email: 'test@gmail.com',
    password: 'TestPass123',
  };

  const INVALID_USER = {
    email: 'wrong@email.com',
    password: 'WrongPass123',
  };

  // Helper function to clear all application storage
  const clearAppStorage = () => {
    cy.clearLocalStorage();
    cy.clearCookies();
  };

  beforeEach(() => {
    // Clear storage before each test
    clearAppStorage();
    // Visit the login page
    cy.visit('/login');
  });

  /**
   * Test Suite: Successful Login Flow
   */
  describe('Successful Login', () => {
    it('should login successfully with valid credentials', () => {
      // Step 1: Verify we're on the login page
      cy.url().should('include', '/login');
      cy.contains('Login').should('be.visible');

      // Step 2: Fill in login form
      cy.get('input[type="email"]')
        .should('be.visible')
        .type(TEST_USER.email)
        .should('have.value', TEST_USER.email);

      cy.get('input[type="password"]')
        .should('be.visible')
        .type(TEST_USER.password)
        .should('have.value', TEST_USER.password);

      // Step 3: Submit the form
      cy.contains('button', 'Login').click();

      // Step 4: Should redirect to dashboard
      cy.url().should('include', '/dashboard', { timeout: 10000 });

      // Step 5: Should see dashboard content
      cy.contains('Your Calendars', { timeout: 10000 }).should('be.visible');

      // Step 6: Should have auth token in localStorage
      cy.window().then((window) => {
        const token = window.localStorage.getItem('auth_token');
        expect(token).to.not.be.null;
        expect(token).to.be.a('string');
        expect(token.length).to.be.greaterThan(0);
      });

      // Step 7: Should have user data in localStorage
      cy.window().then((window) => {
        const userData = window.localStorage.getItem('user_data');
        expect(userData).to.not.be.null;

        const user = JSON.parse(userData);
        expect(user).to.have.property('email', TEST_USER.email);
      });
    });

    it('should persist session after page reload', () => {
      // Login first
      cy.get('input[type="email"]').type(TEST_USER.email);
      cy.get('input[type="password"]').type(TEST_USER.password);
      cy.contains('button', 'Login').click();

      // Wait for redirect
      cy.url().should('include', '/dashboard', { timeout: 10000 });

      // Reload the page
      cy.reload();

      // Should still be on dashboard (not redirected to login)
      cy.url().should('include', '/dashboard');
      cy.contains('Your Calendars').should('be.visible');
    });

    it('should show loading state during login', () => {
      cy.get('input[type="email"]').type(TEST_USER.email);
      cy.get('input[type="password"]').type(TEST_USER.password);

      // Click login button
      cy.contains('button', 'Login').click();

      // Should show loading spinner briefly
      cy.get('ion-spinner').should('exist');
    });
  });

  /**
   * Test Suite: Failed Login Attempts
   */
  describe('Failed Login', () => {
    it('should show error message with invalid credentials', () => {
      // Fill in invalid credentials
      cy.get('input[type="email"]').type(INVALID_USER.email);
      cy.get('input[type="password"]').type(INVALID_USER.password);

      // Submit form
      cy.contains('button', 'Login').click();

      // Should show error message
      cy.contains('Invalid email or password', { timeout: 5000 })
        .should('be.visible');

      // Should stay on login page
      cy.url().should('include', '/login');

      // Should not have auth token
      cy.window().then((window) => {
        const token = window.localStorage.getItem('auth_token');
        expect(token).to.be.null;
      });
    });

    it('should show validation error for empty email', () => {
      // Leave email empty, only fill password
      cy.get('input[type="password"]').type(TEST_USER.password);

      // Try to submit
      cy.contains('button', 'Login').click();

      // Should show validation error
      cy.contains('Email is required').should('be.visible');
    });

    it('should show validation error for empty password', () => {
      // Only fill email, leave password empty
      cy.get('input[type="email"]').type(TEST_USER.email);

      // Try to submit
      cy.contains('button', 'Login').click();

      // Should show validation error
      cy.contains('Password is required').should('be.visible');
    });

    it('should show validation error for invalid email format', () => {
      // Type invalid email
      cy.get('input[type="email"]').type('invalid-email');
      cy.get('input[type="password"]').type(TEST_USER.password);

      // Blur email field to trigger validation
      cy.get('input[type="email"]').blur();

      // Should show email format error
      cy.contains('Please enter a valid email address').should('be.visible');
    });

    it('should clear error message when user starts typing', () => {
      // Trigger an error first
      cy.get('input[type="email"]').type(INVALID_USER.email);
      cy.get('input[type="password"]').type(INVALID_USER.password);
      cy.contains('button', 'Login').click();

      // Wait for error
      cy.contains('Invalid email or password', { timeout: 5000 })
        .should('be.visible');

      // Start typing in email field
      cy.get('input[type="email"]').clear().type('new@email.com');

      // Error should disappear
      cy.contains('Invalid email or password').should('not.exist');
    });
  });

  /**
   * Test Suite: Navigation
   */
  describe('Navigation', () => {
    it('should navigate to registration page', () => {
      // Look for "Don't have an account?" link
      cy.contains("Don't have an account?").should('be.visible');
      cy.contains('Register').click();

      // Should navigate to register page
      cy.url().should('include', '/register');
      cy.contains('Create Account').should('be.visible');
    });

    it('should navigate back to login from register page', () => {
      // Go to register page
      cy.contains('Register').click();
      cy.url().should('include', '/register');

      // Navigate back to login
      cy.contains('Already have an account?').should('be.visible');
      cy.contains('Login').click();

      // Should be back on login page
      cy.url().should('include', '/login');
    });

    it('should redirect to login when accessing protected route without auth', () => {
      // Try to access dashboard directly
      cy.visit('/dashboard');

      // Should redirect to login
      cy.url().should('include', '/login');
      cy.contains('Login').should('be.visible');
    });
  });

  /**
   * Test Suite: Logout Flow
   */
  describe('Logout', () => {
    beforeEach(() => {
      // Login before each logout test
      cy.visit('/login');
      cy.get('input[type="email"]').type(TEST_USER.email);
      cy.get('input[type="password"]').type(TEST_USER.password);
      cy.contains('button', 'Login').click();
      cy.url().should('include', '/dashboard', { timeout: 10000 });
    });

    it('should logout successfully and clear session', () => {
      // Verify we're logged in first
      cy.window().then((window) => {
        expect(window.localStorage.getItem('auth_token')).to.not.be.null;
      });

      // Find and click logout button (could be in menu or visible)
      cy.contains('Logout').click();

      // Should redirect to login page
      cy.url().should('include', '/login', { timeout: 5000 });

      // Should clear localStorage
      cy.window().then((window) => {
        expect(window.localStorage.getItem('auth_token')).to.be.null;
        expect(window.localStorage.getItem('user_data')).to.be.null;
      });
    });

    it('should not be able to access dashboard after logout', () => {
      // Logout
      cy.contains('Logout').click();
      cy.url().should('include', '/login', { timeout: 5000 });

      // Try to access dashboard
      cy.visit('/dashboard');

      // Should redirect back to login
      cy.url().should('include', '/login');
    });
  });

  /**
   * Test Suite: Accessibility
   */
  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      // Email field should have label
      cy.get('label').contains('Email').should('be.visible');

      // Password field should have label
      cy.get('label').contains('Password').should('be.visible');
    });

    it('should support keyboard navigation', () => {
      // Focus email field
      cy.get('input[type="email"]').focus().type(TEST_USER.email);

      // Tab to password field
      cy.get('input[type="email"]').tab();
      cy.focused().should('have.attr', 'type', 'password');
      cy.focused().type(TEST_USER.password);

      // Tab to login button
      cy.focused().tab();
      cy.focused().should('contain', 'Login');

      // Press Enter to submit
      cy.focused().type('{enter}');

      // Should redirect to dashboard
      cy.url().should('include', '/dashboard', { timeout: 10000 });
    });

    it('should have proper ARIA attributes for errors', () => {
      // Trigger validation error
      cy.get('input[type="email"]').type('invalid-email').blur();

      // Error message should have proper ARIA
      cy.get('[role="alert"]').should('be.visible');
    });
  });

  /**
   * Test Suite: Responsive Design
   */
  describe('Responsive Design', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 },
    ];

    viewports.forEach((viewport) => {
      it(`should display correctly on ${viewport.name}`, () => {
        cy.viewport(viewport.width, viewport.height);

        // All form elements should be visible
        cy.get('input[type="email"]').should('be.visible');
        cy.get('input[type="password"]').should('be.visible');
        cy.contains('button', 'Login').should('be.visible');

        // Should be able to interact with form
        cy.get('input[type="email"]').type(TEST_USER.email);
        cy.get('input[type="password"]').type(TEST_USER.password);
        cy.contains('button', 'Login').should('be.enabled');
      });
    });
  });
});
