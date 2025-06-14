// frontend/src/components/__tests__/QuickLogPageProgress.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import QuickLogPage from '../QuickLogPage.vue'
import * as api from '@/services/api'

// Mock the API
vi.mock('@/services/api', () => ({
  runApi: {
    createRun: vi.fn(),
    getRuns: vi.fn()
  },
  targetApi: {
    getTargets: vi.fn()
  }
}))

describe('QuickLogPage Progress Calculation', () => {
  let mockRouter: any

  beforeEach(() => {
    vi.clearAllMocks()

    mockRouter = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/quick-log', component: QuickLogPage }
      ]
    })
  })

  it('should show aggregated monthly progress after saving a run', async () => {
    // ARRANGE - Mock existing runs and targets
    const mockExistingRuns = [
      { run_id: '1', date: '2025-06-01', distance_km: 5.0, duration: '00:30:00', pace: '06:00', notes: '' },
      { run_id: '2', date: '2025-06-05', distance_km: 3.2, duration: '00:20:00', pace: '06:15', notes: '' }
    ]

    const mockTargets = [
      {
        target_id: 'target1',
        user_id: 'user123',
        target_type: 'monthly' as const,
        period: '2025-06',
        period_display: 'June 2025',
        distance_km: 50.0,
        created_at: '2025-06-01T00:00:00Z'
      }
    ]

    const mockNewRun = {
      run_id: '3',
      date: '2025-06-14',
      distance_km: 8.5,
      duration: '00:45:00',
      pace: '05:30',
      notes: ''
    }

    // Mock API responses
    vi.mocked(api.targetApi.getTargets).mockResolvedValue(mockTargets)
    vi.mocked(api.runApi.createRun).mockResolvedValue(mockNewRun)
    vi.mocked(api.runApi.getRuns).mockResolvedValue([...mockExistingRuns, mockNewRun])

    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Wait for component to load targets
    await wrapper.vm.$nextTick()

    // ACT - Fill form and submit
    await wrapper.find('[data-testid="distance-input"]').setValue('8.5')
    await wrapper.find('[data-testid="time-input"]').setValue('45:00')
    await wrapper.find('[data-testid="run-type-select"]').setValue('easy')

    const form = wrapper.find('[data-testid="quick-log-form"]')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    // Wait for async operations
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // ASSERT - Progress should show aggregated total
    // Expected: 5.0 + 3.2 + 8.5 = 16.7km of 50km target = 33%
    const monthlyProgress = wrapper.find('[data-testid="monthly-progress"]')
    expect(monthlyProgress.exists()).toBe(true)

    // Check that it shows the aggregated total, not just the new run
    expect(monthlyProgress.text()).toContain('16.7km')
    expect(monthlyProgress.text()).toContain('50km')
    expect(monthlyProgress.text()).toContain('33%')
  })

  it('should show aggregated yearly progress after saving a run', async () => {
    // ARRANGE - Mock runs from different months in 2025
    const mockExistingRuns = [
      { run_id: '1', date: '2025-01-15', distance_km: 10.0, duration: '01:00:00', pace: '06:00', notes: '' },
      { run_id: '2', date: '2025-03-20', distance_km: 7.5, duration: '00:45:00', pace: '06:00', notes: '' },
      { run_id: '3', date: '2025-05-10', distance_km: 12.3, duration: '01:15:00', pace: '06:05', notes: '' }
    ]

    const mockTargets = [
      {
        target_id: 'target2',
        user_id: 'user123',
        target_type: 'yearly' as const,
        period: '2025',
        period_display: '2025',
        distance_km: 500.0,
        created_at: '2025-01-01T00:00:00Z'
      }
    ]

    const mockNewRun = {
      run_id: '4',
      date: '2025-06-14',
      distance_km: 15.2,
      duration: '01:30:00',
      pace: '05:55',
      notes: ''
    }

    // Mock API responses
    vi.mocked(api.targetApi.getTargets).mockResolvedValue(mockTargets)
    vi.mocked(api.runApi.createRun).mockResolvedValue(mockNewRun)
    vi.mocked(api.runApi.getRuns).mockResolvedValue([...mockExistingRuns, mockNewRun])

    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()

    // ACT - Submit new run
    await wrapper.find('[data-testid="distance-input"]').setValue('15.2')
    await wrapper.find('[data-testid="time-input"]').setValue('1:30:00')

    const form = wrapper.find('[data-testid="quick-log-form"]')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // ASSERT - Progress should show aggregated yearly total
    // Expected: 10.0 + 7.5 + 12.3 + 15.2 = 45.0km of 500km target = 9%
    const yearlyProgress = wrapper.find('[data-testid="yearly-progress"]')
    expect(yearlyProgress.exists()).toBe(true)

    expect(yearlyProgress.text()).toContain('45km')
    expect(yearlyProgress.text()).toContain('500km')
    expect(yearlyProgress.text()).toContain('9%')
  })

  it('should handle case when user has no existing runs', async () => {
    // ARRANGE - New user with no runs
    const mockTargets = [
      {
        target_id: 'target1',
        user_id: 'user123',
        target_type: 'monthly' as const,
        period: '2025-06',
        period_display: 'June 2025',
        distance_km: 50.0,
        created_at: '2025-06-01T00:00:00Z'
      }
    ]

    const mockNewRun = {
      run_id: '1',
      date: '2025-06-14',
      distance_km: 5.0,
      duration: '00:30:00',
      pace: '06:00',
      notes: ''
    }

    // Mock API responses - empty existing runs
    vi.mocked(api.targetApi.getTargets).mockResolvedValue(mockTargets)
    vi.mocked(api.runApi.createRun).mockResolvedValue(mockNewRun)
    vi.mocked(api.runApi.getRuns).mockResolvedValue([mockNewRun]) // Only the new run

    const wrapper = mount(QuickLogPage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()

    // ACT - Submit first run
    await wrapper.find('[data-testid="distance-input"]').setValue('5.0')
    await wrapper.find('[data-testid="time-input"]').setValue('30:00')

    const form = wrapper.find('[data-testid="quick-log-form"]')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // ASSERT - Should show just the first run's progress
    const monthlyProgress = wrapper.find('[data-testid="monthly-progress"]')
    expect(monthlyProgress.exists()).toBe(true)

    expect(monthlyProgress.text()).toContain('5km')
    expect(monthlyProgress.text()).toContain('50km')
    expect(monthlyProgress.text()).toContain('10%')
  })
})
