/**
 * E2E Tests for Calendar Management Flow
 *
 * Tests complete calendar CRUD workflows including:
 * - Creating a new calendar
 * - Viewing calendar list
 * - Editing calendar details
 * - Deleting calendars
 * - Form validation
 * - Navigation between views
 *
 * Prerequisites:
 * - Backend API running at http://localhost:5001
 * - Test user logged in: test@gmail.com / TestPass123
 * - Frontend dev server running
 *
 * Run with: npm run test:e2e
 */

describe('Calendar Management Flow', () => {
  // Configuration
  const TEST_USER = {
    email: 'test@gmail.com',
    password: 'TestPass123',
  };

  const VALID_CALENDAR = {
    title: `E2E Test Calendar ${Date.now()}`, // Unique name for each test run
    startDate: '2025-12-01',
    endDate: '2025-12-25',
    expectedDuration: 25,
  };

  const INVALID_CALENDAR = {
    shortTitle: 'AB', // Too short (min 3 chars)
    longTitle: 'A'.repeat(51), // Too long (max 50 chars)
    pastStartDate: '2020-01-01',
    endBeforeStart: '2025-11-01', // Before start date
    tooLongDuration: '2026-02-01', // More than 31 days
  };

  // Helper function to login before tests
  const loginAsTestUser = () => {
    cy.clearLocalStorage();
    cy.clearCookies();
    cy.visit('/login');
    cy.get('input[type="email"]').type(TEST_USER.email);
    cy.get('input[type="password"]').type(TEST_USER.password);
    cy.contains('button', 'Login').click();
    cy.url().should('include', '/dashboard', { timeout: 10000 });
    cy.contains('Your Calendars', { timeout: 10000 }).should('be.visible');
  };

  beforeEach(() => {
    loginAsTestUser();
  });

  /**
   * Test Suite: Calendar Creation
   */
  describe('Creating a New Calendar', () => {
    it('should create a calendar with valid data', () => {
      // Step 1: Click "Create Calendar" button
      cy.contains('button', 'Create Calendar').should('be.visible').click();

      // Step 2: Should navigate to calendar form (or show modal)
      cy.contains('Calendar Title').should('be.visible');

      // Step 3: Fill in calendar form
      cy.get('input[placeholder*="Christmas"]').or('label:contains("Calendar Title")').parent().find('input')
        .type(VALID_CALENDAR.title)
        .should('have.value', VALID_CALENDAR.title);

      // Fill start date
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.startDate)
        .should('have.value', VALID_CALENDAR.startDate);

      // Fill end date
      cy.get('label:contains("End Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.endDate)
        .should('have.value', VALID_CALENDAR.endDate);

      // Step 4: Should display duration summary
      cy.contains(`${VALID_CALENDAR.expectedDuration} days`).should('be.visible');

      // Step 5: Submit button should be enabled
      cy.contains('button', 'Create Calendar').should('not.be.disabled');

      // Step 6: Submit the form
      cy.contains('button', 'Create Calendar').click();

      // Step 7: Should show success message or redirect
      cy.url().should('match', /\/(dashboard|calendar\/)/, { timeout: 10000 });

      // Step 8: Success toast/message should appear
      cy.contains(/successfully|created/i, { timeout: 5000 }).should('be.visible');

      // Step 9: Calendar should appear in the list
      cy.visit('/dashboard');
      cy.contains(VALID_CALENDAR.title, { timeout: 5000 }).should('be.visible');
    });

    it('should show loading state while creating calendar', () => {
      cy.contains('button', 'Create Calendar').click();

      // Fill form
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type(VALID_CALENDAR.title);
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.startDate);
      cy.get('label:contains("End Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.endDate);

      // Submit
      cy.contains('button', 'Create Calendar').click();

      // Should show loading spinner
      cy.get('ion-spinner').should('exist');
    });

    it('should display calendar in dashboard list after creation', () => {
      const uniqueTitle = `Test Calendar ${Date.now()}`;

      cy.contains('button', 'Create Calendar').click();

      // Create calendar
      cy.get('label:contains("Calendar Title")').parent().find('input').type(uniqueTitle);
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]').type('2025-12-01');
      cy.get('label:contains("End Date")').parent().find('input[type="date"]').type('2025-12-15');
      cy.contains('button', 'Create Calendar').click();

      // Wait for creation
      cy.url().should('match', /\/(dashboard|calendar\/)/, { timeout: 10000 });

      // Go to dashboard
      cy.visit('/dashboard');

      // New calendar should be visible
      cy.contains(uniqueTitle, { timeout: 5000 }).should('be.visible');

      // Should show calendar details
      cy.contains('Dec 1 - Dec 15').should('be.visible');
    });
  });

  /**
   * Test Suite: Form Validation
   */
  describe('Calendar Form Validation', () => {
    beforeEach(() => {
      cy.contains('button', 'Create Calendar').click();
      cy.contains('Calendar Title').should('be.visible');
    });

    it('should validate title minimum length (3 characters)', () => {
      // Type short title
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type(INVALID_CALENDAR.shortTitle)
        .blur();

      // Should show error
      cy.contains('at least 3 characters').should('be.visible');

      // Submit button should be disabled
      cy.contains('button', 'Create Calendar').should('be.disabled');
    });

    it('should validate title maximum length (50 characters)', () => {
      // Type long title
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type(INVALID_CALENDAR.longTitle)
        .blur();

      // Should show error
      cy.contains('less than 50 characters').should('be.visible');

      // Submit button should be disabled
      cy.contains('button', 'Create Calendar').should('be.disabled');
    });

    it('should validate start date is not in the past', () => {
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type(VALID_CALENDAR.title);

      // Select past date
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]')
        .type(INVALID_CALENDAR.pastStartDate)
        .blur();

      // Should show error
      cy.contains('cannot be in the past').should('be.visible');
    });

    it('should validate end date is after start date', () => {
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type(VALID_CALENDAR.title);

      // Set start date
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.startDate);

      // Set end date before start
      cy.get('label:contains("End Date")').parent().find('input[type="date"]')
        .type(INVALID_CALENDAR.endBeforeStart)
        .blur();

      // Should show error
      cy.contains('after start date').should('be.visible');
    });

    it('should validate duration does not exceed 31 days', () => {
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type(VALID_CALENDAR.title);

      cy.get('label:contains("Start Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.startDate);

      // Set end date more than 31 days later
      cy.get('label:contains("End Date")').parent().find('input[type="date"]')
        .type(INVALID_CALENDAR.tooLongDuration)
        .blur();

      // Should show error
      cy.contains('cannot exceed 31 days').should('be.visible');
    });

    it('should require all fields to be filled', () => {
      // Submit without filling anything
      cy.contains('button', 'Create Calendar').should('be.disabled');

      // Fill only title
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type(VALID_CALENDAR.title);
      cy.contains('button', 'Create Calendar').should('be.disabled');

      // Fill start date
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.startDate);
      cy.contains('button', 'Create Calendar').should('be.disabled');

      // Fill end date - now button should be enabled
      cy.get('label:contains("End Date")').parent().find('input[type="date"]')
        .type(VALID_CALENDAR.endDate);
      cy.contains('button', 'Create Calendar').should('not.be.disabled');
    });

    it('should clear errors when user corrects input', () => {
      // Trigger error
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .type('AB')
        .blur();
      cy.contains('at least 3 characters').should('be.visible');

      // Correct the input
      cy.get('label:contains("Calendar Title")').parent().find('input')
        .clear()
        .type('Valid Title');

      // Error should disappear
      cy.contains('at least 3 characters').should('not.exist');
    });
  });

  /**
   * Test Suite: Calendar List View
   */
  describe('Calendar List Display', () => {
    it('should display list of calendars on dashboard', () => {
      // Should show calendar grid/list
      cy.contains('Your Calendars').should('be.visible');

      // Should show calendar cards (if any exist)
      cy.get('[class*="calendar-card"]').should('exist');
    });

    it('should show empty state when no calendars exist', () => {
      // This test requires fresh user or calendar cleanup
      // Verify empty state message
      cy.visit('/dashboard');

      // May show empty state or existing calendars
      cy.get('body').then(($body) => {
        if ($body.text().includes('No calendars yet')) {
          cy.contains('Create your first calendar').should('be.visible');
        }
      });
    });

    it('should display calendar details correctly', () => {
      // Create a calendar first
      const testTitle = `Display Test ${Date.now()}`;

      cy.contains('button', 'Create Calendar').click();
      cy.get('label:contains("Calendar Title")').parent().find('input').type(testTitle);
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]').type('2025-12-01');
      cy.get('label:contains("End Date")').parent().find('input[type="date"]').type('2025-12-10');
      cy.contains('button', 'Create Calendar').click();
      cy.url().should('match', /\/(dashboard|calendar\/)/, { timeout: 10000 });

      // Go to dashboard
      cy.visit('/dashboard');

      // Find the calendar card
      cy.contains(testTitle).parents('[class*="calendar-card"]').within(() => {
        // Should show title
        cy.contains(testTitle).should('be.visible');

        // Should show date range
        cy.contains(/Dec/i).should('be.visible');

        // Should show day count or status
        cy.contains(/10|days|active/i).should('be.visible');
      });
    });
  });

  /**
   * Test Suite: Calendar Navigation
   */
  describe('Navigation', () => {
    it('should navigate to calendar detail page when clicked', () => {
      // Wait for calendars to load
      cy.contains('Your Calendars', { timeout: 10000 }).should('be.visible');

      // Click on a calendar (if any exist)
      cy.get('[class*="calendar-card"]').first().click();

      // Should navigate to calendar detail page
      cy.url().should('include', '/calendar/');

      // Should show calendar details
      cy.contains(/Calendar|Day/i).should('be.visible');
    });

    it('should return to dashboard when clicking back/cancel', () => {
      cy.contains('button', 'Create Calendar').click();

      // Click cancel button
      cy.contains('button', 'Cancel').click();

      // Should return to dashboard
      cy.url().should('include', '/dashboard');
    });

    it('should navigate to calendar form from empty state', () => {
      cy.visit('/dashboard');

      // If empty state exists, should have CTA button
      cy.get('body').then(($body) => {
        if ($body.text().includes('Create your first calendar')) {
          cy.contains('Create').click();
          cy.contains('Calendar Title').should('be.visible');
        }
      });
    });
  });

  /**
   * Test Suite: Calendar Deletion
   */
  describe('Deleting Calendars', () => {
    it('should delete calendar successfully', () => {
      // Create a calendar to delete
      const deleteTitle = `Delete Test ${Date.now()}`;

      cy.contains('button', 'Create Calendar').click();
      cy.get('label:contains("Calendar Title")').parent().find('input').type(deleteTitle);
      cy.get('label:contains("Start Date")').parent().find('input[type="date"]').type('2025-12-01');
      cy.get('label:contains("End Date")').parent().find('input[type="date"]').type('2025-12-05');
      cy.contains('button', 'Create Calendar').click();
      cy.url().should('match', /\/(dashboard|calendar\/)/, { timeout: 10000 });

      // Go to dashboard
      cy.visit('/dashboard');
      cy.contains(deleteTitle, { timeout: 5000 }).should('be.visible');

      // Find and click delete button
      cy.contains(deleteTitle).parents('[class*="calendar-card"]').within(() => {
        cy.contains('Delete').or(cy.get('[class*="delete"]')).click();
      });

      // Confirm deletion if confirmation dialog appears
      cy.get('body').then(($body) => {
        if ($body.text().includes('Are you sure')) {
          cy.contains('button', 'Delete').or(cy.contains('button', 'Confirm')).click();
        }
      });

      // Calendar should be removed from list
      cy.contains(deleteTitle).should('not.exist');
    });
  });

  /**
   * Test Suite: Responsive Design
   */
  describe('Responsive Calendar Management', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
    ];

    viewports.forEach((viewport) => {
      it(`should work correctly on ${viewport.name}`, () => {
        cy.viewport(viewport.width, viewport.height);

        // Dashboard should be accessible
        cy.contains('Your Calendars').should('be.visible');

        // Create button should be accessible
        cy.contains('button', 'Create Calendar').should('be.visible');

        // Calendar cards should be visible
        cy.get('[class*="calendar-card"]').should('exist');
      });
    });
  });

  /**
   * Test Suite: Accessibility
   */
  describe('Accessibility', () => {
    it('should have proper ARIA labels for calendar form', () => {
      cy.contains('button', 'Create Calendar').click();

      // Form should have aria-label
      cy.get('form[aria-label]').should('exist');

      // Required fields should be marked
      cy.get('input[required]').should('have.length.at.least', 3);
    });

    it('should support keyboard navigation in calendar list', () => {
      // Calendar cards should be focusable
      cy.get('[class*="calendar-card"]').first().focus().should('have.focus');

      // Should be able to tab through cards
      cy.get('[class*="calendar-card"]').first().tab();
    });
  });
});
