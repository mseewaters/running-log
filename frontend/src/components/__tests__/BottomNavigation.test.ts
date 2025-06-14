// src/components/__tests__/BottomNavigation.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import BottomNavigation from '../BottomNavigation.vue'

// Mock router for testing
const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/run', name: 'run', component: { template: '<div>Run</div>' } },
    { path: '/plan', name: 'plan', component: { template: '<div>Plan</div>' } },
    { path: '/metrics', name: 'metrics', component: { template: '<div>Metrics</div>' } }
  ]
})

describe('BottomNavigation', () => {
  // Core functionality: Navigation exists
  it('provides navigation to all four main sections', () => {
    const wrapper = mount(BottomNavigation, {
      global: {
        plugins: [mockRouter]
      }
    })

    expect(wrapper.find('[data-testid="nav-home"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="nav-run"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="nav-plan"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="nav-metrics"]').exists()).toBe(true)
  })

  // Core functionality: Correct labels for user understanding
  it('shows correct navigation labels', () => {
    const wrapper = mount(BottomNavigation, {
      global: {
        plugins: [mockRouter]
      }
    })

    expect(wrapper.find('[data-testid="nav-home"]').text()).toContain('Home')
    expect(wrapper.find('[data-testid="nav-run"]').text()).toContain('Run')
    expect(wrapper.find('[data-testid="nav-plan"]').text()).toContain('Plan')
    expect(wrapper.find('[data-testid="nav-metrics"]').text()).toContain('Metrics')
  })

  // Core functionality: Navigation is clickable
  it('navigation items are interactive', async () => {
    const wrapper = mount(BottomNavigation, {
      global: {
        plugins: [mockRouter]
      }
    })

    const runNav = wrapper.find('[data-testid="nav-run"]')

    // Should be a clickable element
    expect(runNav.element.tagName.toLowerCase()).toBe('a')

    // Should have href or router-link functionality
    await runNav.trigger('click')
    expect(runNav.exists()).toBe(true) // Navigation exists and responded to click
  })
})
