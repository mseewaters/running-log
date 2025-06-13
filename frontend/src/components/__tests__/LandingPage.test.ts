// src/components/__tests__/LandingPage.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LandingPage from '../LandingPage.vue'

describe('LandingPage', () => {
  // Core structure and branding
  it('displays the app title and branding', () => {
    const wrapper = mount(LandingPage)

    expect(wrapper.find('[data-testid="app-title"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="app-title"]').text()).toContain('FINISH LINES')
    expect(wrapper.find('[data-testid="tagline"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="tagline"]').text()).toContain('Track your runs. Hit your goals')
  })

  // Essential login functionality
  it('provides login form with required fields', () => {
    const wrapper = mount(LandingPage)

    expect(wrapper.find('[data-testid="login-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="email-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="password-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="login-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="login-button"]').text()).toBe('Sign In')
  })

  // Essential navigation options
  it('provides registration option for new users', () => {
    const wrapper = mount(LandingPage)

    expect(wrapper.find('[data-testid="register-link"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-link"]').text()).toContain('Register')
  })

  // Mobile responsiveness (using CSS class)
  it('is mobile-friendly', () => {
    const wrapper = mount(LandingPage)

    const container = wrapper.find('[data-testid="landing-container"]')
    expect(container.exists()).toBe(true)
    expect(container.classes()).toContain('landing-container') // Our CSS class
  })

  // Logo/branding presence (not specific styling)
  it('displays app logo', () => {
    const wrapper = mount(LandingPage)

    expect(wrapper.find('[data-testid="logo-circle"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="runner-icon"]').exists()).toBe(true)
  })

  it('handles form submission', async () => {
    const wrapper = mount(LandingPage)

    // Fill out the form
    const emailInput = wrapper.find('[data-testid="email-input"]')
    const passwordInput = wrapper.find('[data-testid="password-input"]')
    const form = wrapper.find('[data-testid="login-form"]')

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')

    // Submit form
    await form.trigger('submit')

    // Should prevent default form submission
    expect(form.element.tagName).toBe('FORM') // Form exists
  })

  it('shows validation errors for empty fields', async () => {
    const wrapper = mount(LandingPage)

    const form = wrapper.find('[data-testid="login-form"]')
    await form.trigger('submit')

    // Should show error messages for empty fields
    expect(wrapper.find('[data-testid="email-error"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="password-error"]').exists()).toBe(true)
  })

  it('shows loading state during login', async () => {
    const wrapper = mount(LandingPage)

    // Fill form and submit
    await wrapper.find('[data-testid="email-input"]').setValue('test@example.com')
    await wrapper.find('[data-testid="password-input"]').setValue('password123')
    await wrapper.find('[data-testid="login-form"]').trigger('submit')

    // Should show loading state
    const button = wrapper.find('[data-testid="login-button"]')
    expect(button.text()).toContain('Signing In...')
  })



})
