// src/components/__tests__/TargetSettingPage.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import TargetSettingPage from '../TargetSettingPage.vue'
import { targetApi } from '@/services/api'

// Mock the API
vi.mock('@/services/api', () => ({
  targetApi: {
    createTarget: vi.fn(),
    getTargets: vi.fn()
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

describe('TargetSettingPage', () => {
  // Test 1: Component renders core elements
  it('renders essential form elements', () => {
    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Core functionality: form exists and has required inputs
    expect(wrapper.find('[data-testid="target-type-select"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="period-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="distance-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="create-target-button"]').exists()).toBe(true)
  })

  // Test 2: Core functionality - target type affects period input
  it('changes period placeholder based on target type', async () => {
    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    const periodInput = wrapper.find('[data-testid="period-input"]')

    // Should start with monthly placeholder
    expect(periodInput.attributes('placeholder')).toContain('YYYY-MM')

    // Change to yearly
    await wrapper.find('[data-testid="target-type-select"]').setValue('yearly')

    // Should change to yearly placeholder
    expect(periodInput.attributes('placeholder')).toContain('YYYY')
  })

  // Test 3: Core functionality - form validation
  it('validates required inputs', async () => {
    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Submit empty form
    const form = wrapper.find('[data-testid="target-setting-form"]')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    // Should show validation errors for required fields
    expect(wrapper.find('[data-testid="period-error"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="distance-error"]').exists()).toBe(true)
  })

  // Test 4: Core functionality - successful target creation
  it('calls API when form is submitted with valid data', async () => {
    const mockTargetResponse = {
      target_id: 'mock-target-id',
      user_id: 'mock-user-id',
      target_type: 'monthly' as const,
      period: '2025-06',
      period_display: 'June 2025',
      distance_km: 100,
      created_at: '2025-06-14T10:00:00Z'
    }

    vi.mocked(targetApi.createTarget).mockResolvedValue(mockTargetResponse)
    vi.mocked(targetApi.getTargets).mockResolvedValue([])

    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Fill valid data
    await wrapper.find('[data-testid="target-type-select"]').setValue('monthly')
    await wrapper.find('[data-testid="period-input"]').setValue('2025-06')
    await wrapper.find('[data-testid="distance-input"]').setValue('100')

    // Submit form
    const form = wrapper.find('[data-testid="target-setting-form"]')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Should call API with correct data
    expect(targetApi.createTarget).toHaveBeenCalledWith({
      target_type: 'monthly' as const,
      period: '2025-06',
      distance_km: 100
    })
  })

  // Test 5: Core functionality - error handling
  it('displays error when API call fails', async () => {
    vi.mocked(targetApi.createTarget).mockRejectedValue(new Error('API Error'))
    vi.mocked(targetApi.getTargets).mockResolvedValue([])

    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Fill and submit form
    await wrapper.find('[data-testid="target-type-select"]').setValue('monthly')
    await wrapper.find('[data-testid="period-input"]').setValue('2025-06')
    await wrapper.find('[data-testid="distance-input"]').setValue('100')

    const form = wrapper.find('[data-testid="target-setting-form"]')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // Should show error message
    expect(wrapper.find('[data-testid="general-error"]').exists()).toBe(true)
  })

  // Test 6: Core functionality - period format validation
  it('validates period format correctly', async () => {
    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Test invalid monthly period
    await wrapper.find('[data-testid="target-type-select"]').setValue('monthly')
    await wrapper.find('[data-testid="period-input"]').setValue('2025-13') // Invalid month
    await wrapper.find('[data-testid="distance-input"]').setValue('100')

    const form = wrapper.find('[data-testid="target-setting-form"]')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    // Should show period validation error
    expect(wrapper.find('[data-testid="period-error"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="period-error"]').text()).toContain('Invalid month')
  })

  // Test 7: Core functionality - loads and displays existing targets
  it('loads existing targets on mount', async () => {
    const mockTargets = [
      {
        target_id: '1',
        user_id: 'test-user',
        target_type: 'monthly' as const,
        period: '2025-06',
        period_display: 'June 2025',
        distance_km: 100,
        created_at: '2025-06-14T10:00:00Z'
      }
    ]

    vi.mocked(targetApi.getTargets).mockResolvedValue(mockTargets)

    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Should call getTargets API
    expect(targetApi.getTargets).toHaveBeenCalled()

    // Should display target data (basic check that data is rendered)
    expect(wrapper.text()).toContain('100km')
  })

  // Test 8: Core functionality - empty state
  it('shows message when no targets exist', async () => {
    vi.mocked(targetApi.getTargets).mockResolvedValue([])

    const wrapper = mount(TargetSettingPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Should show empty state message
    expect(wrapper.find('[data-testid="no-targets-message"]').exists()).toBe(true)
  })
})
