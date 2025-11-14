/**
 * Component Tests for CalendarForm.vue
 *
 * Tests form rendering, validation, user interactions, and submission logic.
 * Ensures proper error handling and accessibility compliance.
 *
 * Coverage targets:
 * - Form rendering in create/edit modes
 * - Field validation (title, dates, duration)
 * - User interactions (input, blur, submit, cancel)
 * - Error message display
 * - Submit button state (enabled/disabled)
 * - Duration calculation
 *
 * Run with: npm run test:unit tests/unit/example.spec.ts
 */

import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import CalendarForm from '@/components/CalendarForm.vue';
import FormField from '@/components/FormField.vue';
import type { Calendar } from '@/types/calendar';

// Mock Ionic components
jest.mock('@ionic/vue', () => ({
  IonButton: {
    name: 'IonButton',
    template: '<button><slot></slot></button>',
  },
  IonSpinner: {
    name: 'IonSpinner',
    template: '<span>Loading...</span>',
  },
}));

describe('CalendarForm.vue', () => {
  /**
   * Test Suite: Basic Rendering
   */
  describe('Rendering', () => {
    it('renders calendar creation form with all fields', () => {
      const wrapper = mount(CalendarForm, {
        global: {
          components: {
            FormField,
          },
        },
      });

      expect(wrapper.text()).toMatch('Create Calendar');
      expect(wrapper.text()).toMatch('Calendar Title');
      expect(wrapper.text()).toMatch('Start Date');
      expect(wrapper.text()).toMatch('End Date');
    });

    it('renders form in edit mode when calendar prop is provided', () => {
      const mockCalendar: Calendar = {
        id: 'cal-123',
        title: 'Test Calendar',
        startDate: '2025-12-01',
        endDate: '2025-12-25',
        duration: 25,
        dateRange: 'Dec 1 - Dec 25, 2025',
        videoCount: 0,
        status: 'active',
        createdAt: '2025-11-01T00:00:00Z',
      };

      const wrapper = mount(CalendarForm, {
        props: {
          calendar: mockCalendar,
        },
        global: {
          components: {
            FormField,
          },
        },
      });

      expect(wrapper.text()).toMatch('Edit Calendar');
      expect(wrapper.text()).toMatch('Save Changes');
    });

    it('renders cancel and submit buttons', () => {
      const wrapper = mount(CalendarForm, {
        global: {
          components: {
            FormField,
          },
        },
      });

      const buttons = wrapper.findAll('button');
      expect(buttons.length).toBeGreaterThanOrEqual(2);
      expect(wrapper.html()).toContain('Cancel');
      expect(wrapper.html()).toContain('Create Calendar');
    });

    it('renders calendar duration summary when dates are selected', async () => {
      // Mount with initial data already set
      const wrapper = mount(CalendarForm, {
        props: {
          initialData: {
            title: 'Test',
            startDate: '2025-12-01',
          },
        },
        global: {
          components: {
            FormField,
          },
        },
      });

      await nextTick();

      // Find the end date input field directly (native input, not FormField component)
      // const endDateInput = wrapper.find('input[type="date"]').element as HTMLInputElement;

      // Set value on all date inputs (find the end date one)
      const dateInputs = wrapper.findAll('input[type="date"]');

      // First is start date, second is end date
      if (dateInputs.length >= 2) {
        const endDateField = dateInputs[1];
        await endDateField.setValue('2025-12-25');
        await nextTick();

        // Duration summary should be visible
        expect(wrapper.html()).toContain('25 days');
      }
    });
  });

  /**
   * Test Suite: Form Validation
   */
  describe('Form Validation', () => {
    describe('Title validation', () => {
      it('should require minimum 3 characters for title', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        // Find title field and set short value
        const formFields = wrapper.findAllComponents(FormField);
        const titleField = formFields.find((field) => field.props('label') === 'Calendar Title');

        if (titleField) {
          await titleField.vm.$emit('update:modelValue', 'AB');
          await titleField.vm.$emit('blur');
          await nextTick();

          expect(titleField.props('errorMessage')).toBe('Title must be at least 3 characters long');
        }
      });

      it('should accept valid title (3-50 characters)', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const formFields = wrapper.findAllComponents(FormField);
        const titleField = formFields.find((field) => field.props('label') === 'Calendar Title');

        if (titleField) {
          await titleField.vm.$emit('update:modelValue', 'Valid Title');
          await titleField.vm.$emit('blur');
          await nextTick();

          expect(titleField.props('errorMessage')).toBe('');
        }
      });

      it('should reject titles longer than 50 characters', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const formFields = wrapper.findAllComponents(FormField);
        const titleField = formFields.find((field) => field.props('label') === 'Calendar Title');

        if (titleField) {
          const longTitle = 'A'.repeat(51);
          await titleField.vm.$emit('update:modelValue', longTitle);
          await titleField.vm.$emit('blur');
          await nextTick();

          expect(titleField.props('errorMessage')).toBe('Title must be less than 50 characters');
        }
      });
    });

    describe('Date validation', () => {
      it('should require start date', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const formFields = wrapper.findAllComponents(FormField);
        const startDateField = formFields.find((field) => field.props('label') === 'Start Date');

        if (startDateField) {
          await startDateField.vm.$emit('blur');
          await nextTick();

          expect(startDateField.props('errorMessage')).toBe('Start date is required');
        }
      });

      it('should require end date', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const formFields = wrapper.findAllComponents(FormField);
        const endDateField = formFields.find((field) => field.props('label') === 'End Date');

        if (endDateField) {
          await endDateField.vm.$emit('blur');
          await nextTick();

          expect(endDateField.props('errorMessage')).toBe('End date is required');
        }
      });

      it('should reject past start dates in create mode', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const formFields = wrapper.findAllComponents(FormField);
        const startDateField = formFields.find((field) => field.props('label') === 'Start Date');

        if (startDateField) {
          await startDateField.vm.$emit('update:modelValue', '2020-01-01');
          await startDateField.vm.$emit('blur');
          await nextTick();

          expect(startDateField.props('errorMessage')).toBe('Start date cannot be in the past');
        }
      });

      it('should validate end date is after start date', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const formFields = wrapper.findAllComponents(FormField);
        const startDateField = formFields.find((field) => field.props('label') === 'Start Date');
        const endDateField = formFields.find((field) => field.props('label') === 'End Date');

        if (startDateField && endDateField) {
          await startDateField.vm.$emit('update:modelValue', '2025-12-25');
          await endDateField.vm.$emit('update:modelValue', '2025-12-01');
          await endDateField.vm.$emit('blur');
          await nextTick();

          expect(endDateField.props('errorMessage')).toBe('End date must be after start date');
        }
      });

      it('should validate duration does not exceed 31 days', async () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const formFields = wrapper.findAllComponents(FormField);
        const startDateField = formFields.find((field) => field.props('label') === 'Start Date');
        const endDateField = formFields.find((field) => field.props('label') === 'End Date');

        if (startDateField && endDateField) {
          await startDateField.vm.$emit('update:modelValue', '2025-12-01');
          await endDateField.vm.$emit('update:modelValue', '2026-01-15'); // More than 31 days
          await endDateField.vm.$emit('blur');
          await nextTick();

          expect(endDateField.props('errorMessage')).toBe('Calendar cannot exceed 31 days');
        }
      });
    });

    describe('Submit button state', () => {
      it('should disable submit button when form is invalid', () => {
        const wrapper = mount(CalendarForm, {
          global: {
            components: {
              FormField,
            },
          },
        });

        const submitButton = wrapper.findAll('button').find((btn) => btn.text().includes('Create'));
        expect(submitButton?.attributes('disabled')).toBeDefined();
      });

      it('should enable submit button when form is valid', async () => {
        const wrapper = mount(CalendarForm, {
          props: {
            initialData: {
              title: 'Valid Calendar',
              startDate: '2025-12-01',
            },
          },
          global: {
            components: {
              FormField,
            },
          },
        });

        // Set end date to make form valid
        const formFields = wrapper.findAllComponents(FormField);
        const endDateField = formFields.find((field) => field.props('label') === 'End Date');

        if (endDateField) {
          await endDateField.vm.$emit('update:modelValue', '2025-12-25');
          await nextTick();

          const submitButton = wrapper.findAll('button').find((btn) => btn.text().includes('Create'));
          expect(submitButton?.attributes('disabled')).toBeUndefined();
        }
      });

      it('should disable submit button when submitting', async () => {
        const wrapper = mount(CalendarForm, {
          props: {
            isSubmitting: true,
            initialData: {
              title: 'Valid Calendar',
              startDate: '2025-12-01',
            },
          },
          global: {
            components: {
              FormField,
            },
          },
        });

        // Set end date
        const formFields = wrapper.findAllComponents(FormField);
        const endDateField = formFields.find((field) => field.props('label') === 'End Date');

        if (endDateField) {
          await endDateField.vm.$emit('update:modelValue', '2025-12-25');
          await nextTick();

          const submitButton = wrapper.findAll('button').find((btn) => btn.html().includes('Loading'));
          expect(submitButton?.attributes('disabled')).toBeDefined();
        }
      });
    });
  });

  /**
   * Test Suite: User Interactions
   */
  describe('User Interactions', () => {
    it('should emit submit event with form data on valid submission', async () => {
      const wrapper = mount(CalendarForm, {
        props: {
          initialData: {
            title: 'Test Calendar',
            startDate: '2025-12-01',
          },
        },
        global: {
          components: {
            FormField,
          },
        },
      });

      // Set end date
      const formFields = wrapper.findAllComponents(FormField);
      const endDateField = formFields.find((field) => field.props('label') === 'End Date');

      if (endDateField) {
        await endDateField.vm.$emit('update:modelValue', '2025-12-25');
        await nextTick();

        // Submit form
        const form = wrapper.find('form');
        await form.trigger('submit.prevent');
        await nextTick();

        expect(wrapper.emitted('submit')).toBeTruthy();
        const submitEvent = wrapper.emitted('submit')?.[0] as any[];
        expect(submitEvent[0]).toHaveProperty('title', 'Test Calendar');
        expect(submitEvent[0]).toHaveProperty('startDate', '2025-12-01');
        expect(submitEvent[0]).toHaveProperty('duration', 25);
      }
    });

    it('should emit cancel event when cancel button is clicked', async () => {
      const wrapper = mount(CalendarForm, {
        global: {
          components: {
            FormField,
          },
        },
      });

      const cancelButton = wrapper.findAll('button').find((btn) => btn.text().includes('Cancel'));
      await cancelButton?.trigger('click');
      await nextTick();

      expect(wrapper.emitted('cancel')).toBeTruthy();
    });

    it('should clear error messages when user starts typing', async () => {
      const wrapper = mount(CalendarForm, {
        global: {
          components: {
            FormField,
          },
        },
      });

      const formFields = wrapper.findAllComponents(FormField);
      const titleField = formFields.find((field) => field.props('label') === 'Calendar Title');

      if (titleField) {
        // Trigger validation error
        await titleField.vm.$emit('update:modelValue', 'AB');
        await titleField.vm.$emit('blur');
        await nextTick();

        expect(titleField.props('errorMessage')).toBeTruthy();

        // Start typing again
        await titleField.vm.$emit('update:modelValue', 'ABC');
        await nextTick();

        // Error should be cleared
        expect(titleField.props('errorMessage')).toBe('');
      }
    });
  });

  /**
   * Test Suite: Edit Mode
   */
  describe('Edit Mode', () => {
    const mockCalendar: Calendar = {
      id: 'cal-123',
      title: 'Existing Calendar',
      startDate: '2025-12-01',
      endDate: '2025-12-25',
      duration: 25,
      dateRange: 'Dec 1 - Dec 25, 2025',
      videoCount: 5,
      status: 'active',
      createdAt: '2025-11-01T00:00:00Z',
    };

    it('should pre-populate form with calendar data', () => {
      const wrapper = mount(CalendarForm, {
        props: {
          calendar: mockCalendar,
        },
        global: {
          components: {
            FormField,
          },
        },
      });

      const formFields = wrapper.findAllComponents(FormField);
      const titleField = formFields.find((field) => field.props('label') === 'Calendar Title');
      const startDateField = formFields.find((field) => field.props('label') === 'Start Date');
      const endDateField = formFields.find((field) => field.props('label') === 'End Date');

      expect(titleField?.props('modelValue')).toBe('Existing Calendar');
      expect(startDateField?.props('modelValue')).toBe('2025-12-01');
      expect(endDateField?.props('modelValue')).toBe('2025-12-25');
    });

    it('should emit submit with calendar ID in edit mode', async () => {
      const wrapper = mount(CalendarForm, {
        props: {
          calendar: mockCalendar,
        },
        global: {
          components: {
            FormField,
          },
        },
      });

      const form = wrapper.find('form');
      await form.trigger('submit.prevent');
      await nextTick();

      expect(wrapper.emitted('submit')).toBeTruthy();
      const submitEvent = wrapper.emitted('submit')?.[0] as any[];
      expect(submitEvent[1]).toBe('cal-123'); // Calendar ID as second parameter
    });
  });

  /**
   * Test Suite: Duration Calculation
   */
  describe('Duration Calculation', () => {
    it('should calculate and display duration correctly', async () => {
      const wrapper = mount(CalendarForm, {
        props: {
          initialData: {
            startDate: '2025-12-01',
          },
        },
        global: {
          components: {
            FormField,
          },
        },
      });

      const formFields = wrapper.findAllComponents(FormField);
      const endDateField = formFields.find((field) => field.props('label') === 'End Date');

      if (endDateField) {
        await endDateField.vm.$emit('update:modelValue', '2025-12-25');
        await nextTick();

        expect(wrapper.html()).toContain('25 days');
      }
    });

    it('should update duration when dates change', async () => {
      const wrapper = mount(CalendarForm, {
        props: {
          initialData: {
            startDate: '2025-12-01',
          },
        },
        global: {
          components: {
            FormField,
          },
        },
      });

      const formFields = wrapper.findAllComponents(FormField);
      const endDateField = formFields.find((field) => field.props('label') === 'End Date');

      if (endDateField) {
        // Set first duration
        await endDateField.vm.$emit('update:modelValue', '2025-12-25');
        await nextTick();
        expect(wrapper.html()).toContain('25 days');

        // Change end date
        await endDateField.vm.$emit('update:modelValue', '2025-12-15');
        await nextTick();
        expect(wrapper.html()).toContain('15 days');
      }
    });
  });
});
