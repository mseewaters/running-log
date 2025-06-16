// frontend/src/components/__tests__/HomePageProgress.test.ts - UPDATED
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../HomePage.vue'
import * as api from '@/services/api'

// Mock the API
vi.mock('@/services/api', () => ({
  runApi: {
    getRuns: vi.fn()
  },
  targetApi: {
    getTargets: vi.fn()
  }
}))

describe('HomePage Progress Display', () => {
  let mockRouter: any

  beforeEach(() => {
    vi.clearAllMocks()

    mockRouter = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Landing</div>' } },
        { path: '/home', component: HomePage }
      ]
    })
  })

  it('should display monthly progress when user has targets and runs', async () => {
    // ARRANGE - Mock runs and targets for June 2025
    const mockRuns = [
      { run_id: '1', date: '2025-06-01', distance_km: 8.0, duration: '00:45:00', pace: '05:37', notes: 'morning run' },
      { run_id: '2', date: '2025-06-05', distance_km: 5.2, duration: '00:32:00', pace: '06:09', notes: 'easy run' },
      { run_id: '3', date: '2025-06-10', distance_km: 12.5, duration: '01:15:00', pace: '06:00', notes: 'long run' },
      { run_id: '4', date: '2025-05-28', distance_km: 6.0, duration: '00:35:00', pace: '05:50', notes: 'May run' }, // Previous month
    ]

    const mockTargets = [
      {
        target_id: 'target1',
        user_id: 'user123',
        target_type: 'monthly' as const,
        period: '2025-06',
        period_display: 'June 2025',
        distance_km: 100.0,
        created_at: '2025-06-01T00:00:00Z'
      }
    ]

    // Mock API responses
    vi.mocked(api.runApi.getRuns).mockResolvedValue(mockRuns)
    vi.mocked(api.targetApi.getTargets).mockResolvedValue(mockTargets)

    const wrapper = mount(HomePage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // ASSERT - Should show monthly progress using new ProgressSection component
    // Expected: 8.0 + 5.2 + 12.5 = 25.7km of 100km = 26%
    const monthlyProgress = wrapper.find('[data-testid="monthly-progress"]')
    expect(monthlyProgress.exists()).toBe(true)
    expect(monthlyProgress.text()).toContain('25.7km')
    expect(monthlyProgress.text()).toContain('100km')
    expect(monthlyProgress.text()).toContain('26%')
  })

  it('should display yearly progress when user has yearly targets', async () => {
    // ARRANGE - Mock runs and yearly target
    const mockRuns = [
      { run_id: '1', date: '2025-01-15', distance_km: 20.0, duration: '02:00:00', pace: '06:00', notes: 'long run' },
      { run_id: '2', date: '2025-03-10', distance_km: 15.5, duration: '01:30:00', pace: '05:48', notes: 'tempo' },
      { run_id: '3', date: '2025-06-05', distance_km: 18.2, duration: '01:50:00', pace: '06:02', notes: 'easy' }
    ]

    const mockTargets = [
      {
        target_id: 'yearly',
        user_id: 'user123',
        target_type: 'yearly' as const,
        period: '2025',
        period_display: '2025',
        distance_km: 1000.0,
        created_at: '2025-01-01T00:00:00Z'
      }
    ]

    vi.mocked(api.runApi.getRuns).mockResolvedValue(mockRuns)
    vi.mocked(api.targetApi.getTargets).mockResolvedValue(mockTargets)

    const wrapper = mount(HomePage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // ASSERT - Should show yearly progress
    // Expected: 20.0 + 15.5 + 18.2 = 53.7km of 1000km = 5%
    const yearlyProgress = wrapper.find('[data-testid="yearly-progress"]')
    expect(yearlyProgress.exists()).toBe(true)
    expect(yearlyProgress.text()).toContain('53.7km')
    expect(yearlyProgress.text()).toContain('1000km')
    expect(yearlyProgress.text()).toContain('5%')
  })

  it('should show both monthly and yearly progress when both targets exist', async () => {
    // ARRANGE - Mock with both types of targets
    const mockRuns = [
      { run_id: '1', date: '2025-06-01', distance_km: 10.0, duration: '01:00:00', pace: '06:00', notes: 'run' },
      { run_id: '2', date: '2025-06-15', distance_km: 15.0, duration: '01:30:00', pace: '06:00', notes: 'run' }
    ]

    const mockTargets = [
      {
        target_id: 'monthly',
        user_id: 'user123',
        target_type: 'monthly' as const,
        period: '2025-06',
        period_display: 'June 2025',
        distance_km: 80.0,
        created_at: '2025-06-01T00:00:00Z'
      },
      {
        target_id: 'yearly',
        user_id: 'user123',
        target_type: 'yearly' as const,
        period: '2025',
        period_display: '2025',
        distance_km: 800.0,
        created_at: '2025-01-01T00:00:00Z'
      }
    ]

    vi.mocked(api.runApi.getRuns).mockResolvedValue(mockRuns)
    vi.mocked(api.targetApi.getTargets).mockResolvedValue(mockTargets)

    const wrapper = mount(HomePage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // ASSERT - Both progress sections should exist
    const monthlyProgress = wrapper.find('[data-testid="monthly-progress"]')
    const yearlyProgress = wrapper.find('[data-testid="yearly-progress"]')

    expect(monthlyProgress.exists()).toBe(true)
    expect(yearlyProgress.exists()).toBe(true)

    // Monthly: 25km of 80km = 31%
    expect(monthlyProgress.text()).toContain('25km')
    expect(monthlyProgress.text()).toContain('31%')

    // Yearly: 25km of 800km = 3%
    expect(yearlyProgress.text()).toContain('25km')
    expect(yearlyProgress.text()).toContain('3%')
  })

  it('should show no targets message when user has no targets', async () => {
    // ARRANGE - User with runs but no targets
    const mockRuns = [
      { run_id: '1', date: '2025-06-01', distance_km: 10.0, duration: '01:00:00', pace: '06:00', notes: 'run' }
    ]

    vi.mocked(api.runApi.getRuns).mockResolvedValue(mockRuns as any)
    vi.mocked(api.targetApi.getTargets).mockResolvedValue([] as api.TargetResponse[])

    const wrapper = mount(HomePage, {
      global: {
        plugins: [mockRouter]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // ASSERT - Should show no targets message
    const noTargetsMessage = wrapper.find('[data-testid="no-targets"]')
    expect(noTargetsMessage.exists()).toBe(true)
    expect(noTargetsMessage.text()).toContain('No targets set')
  })

  it('should handle loading states appropriately', async () => {
    // ARRANGE - Slow API responses
    const slowPromise = new Promise(resolve => setTimeout(() => resolve([]), 1000))
    vi.mocked(api.runApi.getRuns).mockReturnValue(slowPromise as Promise<api.RunResponse[]>)
    vi.mocked(api.targetApi.getTargets).mockReturnValue(slowPromise as Promise<api.TargetResponse[]>)

    const wrapper = mount(HomePage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // ASSERT - Should show loading state initially
    expect(wrapper.find('[data-testid="progress-loading"]').exists()).toBe(true)
  })
})
