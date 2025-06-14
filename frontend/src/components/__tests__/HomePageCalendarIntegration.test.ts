// frontend/src/components/__tests__/HomePageCalendarIntegration.test.ts
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

describe('HomePage Calendar Integration', () => {
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

  it('should render calendar component', async () => {
    // ARRANGE - Simple mock data
    const mockRuns = [
      { run_id: '1', date: '2025-06-01', distance_km: 5.0, duration: '00:30:00', pace: '06:00', notes: 'run' }
    ]

    // Mock API to resolve quickly
    vi.mocked(api.runApi.getRuns).mockResolvedValue(mockRuns)
    vi.mocked(api.targetApi.getTargets).mockResolvedValue([])

    const wrapper = mount(HomePage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // Wait for component to mount and load data
    await wrapper.vm.$nextTick()

    // ASSERT - Find all h2 elements and check for Activity section
    const allH2Elements = wrapper.findAll('h2')
    const h2Texts = allH2Elements.map(h2 => h2.text())
    expect(h2Texts).toContain('Activity')

    // Calendar should exist (look for calendar container)
    const calendarContainer = wrapper.find('.calendar-container')
    expect(calendarContainer.exists()).toBe(true)
  }, 10000)

  it('should show both sections exist', () => {
    // ARRANGE - Mock API responses to resolve immediately
    vi.mocked(api.runApi.getRuns).mockResolvedValue([])
    vi.mocked(api.targetApi.getTargets).mockResolvedValue([])

    const wrapper = mount(HomePage, {
      global: {
        plugins: [mockRouter]
      }
    })

    // ASSERT - Both section titles should be present in the DOM
    const allH2Elements = wrapper.findAll('h2')
    const h2Texts = allH2Elements.map(h2 => h2.text())

    expect(h2Texts).toContain('Progress')
    expect(h2Texts).toContain('Activity')
  })
})
