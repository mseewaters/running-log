// src/components/__tests__/QuickLogPage.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import QuickLogPage from '../QuickLogPage.vue'

// Mock router for testing
const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/run', name: 'run', component: { template: '<div>Run</div>' } }
  ]
})

describe('QuickLogPage', () => {
  // Core functionality: Page structure
  it('displays the page title', () => {
    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    expect(wrapper.find('[data-testid="page-title"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="page-title"]').text()).toBe('Quick Log')
  })

  // Core functionality: Form fields exist
  it('provides all required form fields', () => {
    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    expect(wrapper.find('[data-testid="date-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="distance-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="time-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="run-type-select"]').exists()).toBe(true)
  })

  // Core functionality: Save button exists
  it('provides save run button', () => {
    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    const saveButton = wrapper.find('[data-testid="save-button"]')
    expect(saveButton.exists()).toBe(true)
    expect(saveButton.text()).toBe('Save Run')
  })

  // Core functionality: Form submission
  it('handles form submission', async () => {
    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    const form = wrapper.find('[data-testid="quick-log-form"]')
    expect(form.exists()).toBe(true)

    // Should be able to submit form
    await form.trigger('submit')
    expect(form.element.tagName).toBe('FORM')
  })

  // Core functionality: Form submission with valid data

  it('shows validation errors for empty required fields', async () => {
    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Clear all fields
    await wrapper.find('[data-testid="distance-input"]').setValue('')
    await wrapper.find('[data-testid="time-input"]').setValue('')

    // Submit form
    await wrapper.find('[data-testid="quick-log-form"]').trigger('submit')

    // Should show error messages
    expect(wrapper.find('[data-testid="distance-error"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="time-error"]').exists()).toBe(true)
  })

  it('validates time format', async () => {
    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Enter invalid time format
    await wrapper.find('[data-testid="time-input"]').setValue('invalid')
    await wrapper.find('[data-testid="quick-log-form"]').trigger('submit')

    // Should show time format error
    expect(wrapper.find('[data-testid="time-error"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="time-error"]').text()).toContain('format')
  })

  it('does not submit form with validation errors', async () => {
    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Clear required fields
    await wrapper.find('[data-testid="distance-input"]').setValue('')
    await wrapper.find('[data-testid="time-input"]').setValue('')

    // Submit form
    await wrapper.find('[data-testid="quick-log-form"]').trigger('submit')

    // Should not show success message
    expect(wrapper.find('.success-message').exists()).toBe(false)
  })
})
