import { mount } from '@vue/test-utils'
import CalendarForm from '@/components/CalendarForm.vue'

describe('CalendarForm.vue', () => {
  it('renders calendar creation form', () => {
    const wrapper = mount(CalendarForm)
    expect(wrapper.text()).toMatch('Create Your Calendar')
    expect(wrapper.text()).toMatch('Calendar Title')
    expect(wrapper.text()).toMatch('Start Date')
    expect(wrapper.text()).toMatch('End Date')
  })
})
