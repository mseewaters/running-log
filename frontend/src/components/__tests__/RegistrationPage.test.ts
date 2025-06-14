// src/components/__tests__/RegistrationPage.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import RegistrationPage from '../RegistrationPage.vue'
import { authApi } from '@/services/api'

// Mock the API
vi.mock('@/services/api', () => ({
  authApi: {
    register: vi.fn()
  }
}))

// Mock router
const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: { template: '<div>Landing</div>' } },
    { path: '/home', name: 'home', component: { template: '<div>Home</div>' } }
  ]
})

describe('RegistrationPage', () => {
  // Test 1: Component renders properly
  it('renders registration form elements', () => {
    const wrapper = mount(RegistrationPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    expect(wrapper.find('[data-testid="registration-container"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="first-name-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="last-name-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="email-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="password-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="confirm-password-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-button"]').exists()).toBe(true)
  })

  // Test 2: Form validation works
  it('validates required fields', async () => {
    const wrapper = mount(RegistrationPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Trigger form submission (this should call handleRegistration)
    const form = wrapper.find('[data-testid="registration-form"]')
    await form.trigger('submit')

    // Wait for Vue to update the DOM
    await wrapper.vm.$nextTick()

    // Should show validation errors
    expect(wrapper.find('[data-testid="first-name-error"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="email-error"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="password-error"]').exists()).toBe(true)
  })

  // Test 3: Password confirmation validation
  it('validates password confirmation matches', async () => {
    const wrapper = mount(RegistrationPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Fill in form with mismatched passwords
    await wrapper.find('[data-testid="first-name-input"]').setValue('John')
    await wrapper.find('[data-testid="last-name-input"]').setValue('Doe')
    await wrapper.find('[data-testid="email-input"]').setValue('john@example.com')
    await wrapper.find('[data-testid="password-input"]').setValue('Password123!')
    await wrapper.find('[data-testid="confirm-password-input"]').setValue('DifferentPassword123!')

    // Trigger form submission
    const form = wrapper.find('[data-testid="registration-form"]')
    await form.trigger('submit')

    // Wait for Vue to update the DOM
    await wrapper.vm.$nextTick()

    // Check that the error element exists and has correct text
    const errorElement = wrapper.find('[data-testid="confirm-password-error"]')
    expect(errorElement.exists()).toBe(true)
    expect(errorElement.text()).toContain('Passwords do not match')
  })

  // Test 4: Successful registration
  it('handles successful registration', async () => {
    const mockRegisterResponse = {
      access_token: 'mock-token',
      token_type: 'Bearer',
      user_id: 'mock-user-id',
      email: 'john@example.com'
    }

    // Mock successful registration
    vi.mocked(authApi.register).mockResolvedValue(mockRegisterResponse)

    const wrapper = mount(RegistrationPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Fill in valid form data
    await wrapper.find('[data-testid="first-name-input"]').setValue('John')
    await wrapper.find('[data-testid="last-name-input"]').setValue('Doe')
    await wrapper.find('[data-testid="email-input"]').setValue('john@example.com')
    await wrapper.find('[data-testid="password-input"]').setValue('Password123!')
    await wrapper.find('[data-testid="confirm-password-input"]').setValue('Password123!')

    // Trigger form submission
    const form = wrapper.find('[data-testid="registration-form"]')
    await form.trigger('submit')

    // Wait for async operations to complete
    await wrapper.vm.$nextTick()

    // Give more time for the async call to complete
    await new Promise(resolve => setTimeout(resolve, 100))

    // Should call the API with correct data
    expect(authApi.register).toHaveBeenCalledWith({
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      password: 'Password123!'
    })
  })

  // Test 5: Error handling
  it('handles registration errors', async () => {
    // Mock registration failure
    vi.mocked(authApi.register).mockRejectedValue(new Error('Email already exists'))

    const wrapper = mount(RegistrationPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Fill in form
    await wrapper.find('[data-testid="first-name-input"]').setValue('John')
    await wrapper.find('[data-testid="last-name-input"]').setValue('Doe')
    await wrapper.find('[data-testid="email-input"]').setValue('john@example.com')
    await wrapper.find('[data-testid="password-input"]').setValue('Password123!')
    await wrapper.find('[data-testid="confirm-password-input"]').setValue('Password123!')

    // Trigger form submission
    const form = wrapper.find('[data-testid="registration-form"]')
    await form.trigger('submit')

    // Wait for async operations to complete
    await wrapper.vm.$nextTick()

    // Give more time for the async error handling
    await new Promise(resolve => setTimeout(resolve, 100))

    // Wait for DOM update after error
    await wrapper.vm.$nextTick()

    // Should show error message
    expect(wrapper.find('[data-testid="general-error"]').exists()).toBe(true)
  })

  // Test 6: Navigation to login
  it('provides link to login page', () => {
    const wrapper = mount(RegistrationPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    expect(wrapper.find('[data-testid="login-link"]').exists()).toBe(true)
  })
})
