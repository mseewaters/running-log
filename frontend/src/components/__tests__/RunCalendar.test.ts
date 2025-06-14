// frontend/src/components/__tests__/RunCalendar.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import RunCalendar from '../RunCalendar.vue'

describe('RunCalendar Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render current month and year in header', () => {
    // ARRANGE - Mock current date to June 2025
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-06-15'))

    const wrapper = mount(RunCalendar, {
      props: {
        runs: []
      }
    })

    // ASSERT - Should show current month/year
    const header = wrapper.find('[data-testid="calendar-header"]')
    expect(header.exists()).toBe(true)
    expect(header.text()).toContain('June 2025')

    vi.useRealTimers()
  })

  it('should render all days of the current month', () => {
    // ARRANGE - Mock current date to June 2025 (30 days)
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-06-15'))

    const wrapper = mount(RunCalendar, {
      props: {
        runs: []
      }
    })

    // ASSERT - Should show 30 days for June
    const dayElements = wrapper.findAll('[data-testid^="calendar-day-"]')
    expect(dayElements.length).toBe(30)

    // Check specific days exist
    expect(wrapper.find('[data-testid="calendar-day-1"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="calendar-day-15"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="calendar-day-30"]').exists()).toBe(true)

    vi.useRealTimers()
  })

  it('should show yellow indicator on days with runs', () => {
    // ARRANGE - Mock runs for specific dates in June 2025
    const mockRuns = [
      { run_id: '1', date: '2025-06-01', distance_km: 5.0, duration: '00:30:00', pace: '06:00', notes: '' },
      { run_id: '2', date: '2025-06-05', distance_km: 3.2, duration: '00:20:00', pace: '06:15', notes: '' },
      { run_id: '3', date: '2025-06-15', distance_km: 8.5, duration: '00:45:00', pace: '05:30', notes: '' },
      { run_id: '4', date: '2025-05-28', distance_km: 4.0, duration: '00:25:00', pace: '06:15', notes: '' }, // Previous month - should not show
    ]

    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-06-15'))

    const wrapper = mount(RunCalendar, {
      props: {
        runs: mockRuns
      }
    })

    // ASSERT - Days with runs should have yellow indicators
    const day1 = wrapper.find('[data-testid="calendar-day-1"]')
    const day5 = wrapper.find('[data-testid="calendar-day-5"]')
    const day15 = wrapper.find('[data-testid="calendar-day-15"]')
    const day10 = wrapper.find('[data-testid="calendar-day-10"]') // No run on this day

    expect(day1.find('[data-testid="run-indicator"]').exists()).toBe(true)
    expect(day5.find('[data-testid="run-indicator"]').exists()).toBe(true)
    expect(day15.find('[data-testid="run-indicator"]').exists()).toBe(true)
    expect(day10.find('[data-testid="run-indicator"]').exists()).toBe(false)

    vi.useRealTimers()
  })

  it('should highlight today with different styling', () => {
    // ARRANGE - Mock current date to June 15, 2025
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-06-15T12:00:00Z'))

    const wrapper = mount(RunCalendar, {
      props: {
        runs: []
      }
    })

    // ASSERT - Today (15th) should have special styling
    const today = wrapper.find('[data-testid="calendar-day-15"]')
    console.log('Day 15 classes:', today.classes())
    expect(today.classes()).toContain('today')

    // Other days should not have today class
    const otherDay = wrapper.find('[data-testid="calendar-day-10"]')
    expect(otherDay.classes()).not.toContain('today')

    vi.useRealTimers()
  })

  it('should handle multiple runs on the same day', () => {
    // ARRANGE - Multiple runs on the same date
    const mockRuns = [
      { run_id: '1', date: '2025-06-01', distance_km: 5.0, duration: '00:30:00', pace: '06:00', notes: 'morning run' },
      { run_id: '2', date: '2025-06-01', distance_km: 3.0, duration: '00:20:00', pace: '06:40', notes: 'evening run' },
    ]

    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-06-15'))

    const wrapper = mount(RunCalendar, {
      props: {
        runs: mockRuns
      }
    })

    // ASSERT - Should still show only one indicator for multiple runs on same day
    const day1 = wrapper.find('[data-testid="calendar-day-1"]')
    const indicators = day1.findAll('[data-testid="run-indicator"]')
    expect(indicators.length).toBe(1)

    vi.useRealTimers()
  })

  it('should display day numbers correctly', () => {
    // ARRANGE
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-06-15'))

    const wrapper = mount(RunCalendar, {
      props: {
        runs: []
      }
    })

    // ASSERT - Check that day numbers are displayed correctly
    expect(wrapper.find('[data-testid="calendar-day-1"]').text()).toContain('1')
    expect(wrapper.find('[data-testid="calendar-day-15"]').text()).toContain('15')
    expect(wrapper.find('[data-testid="calendar-day-30"]').text()).toContain('30')

    vi.useRealTimers()
  })

  it('should handle empty runs array gracefully', () => {
    // ARRANGE
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-06-15'))

    const wrapper = mount(RunCalendar, {
      props: {
        runs: []
      }
    })

    // ASSERT - Should render without run indicators
    const dayElements = wrapper.findAll('[data-testid^="calendar-day-"]')
    expect(dayElements.length).toBe(30)

    // No run indicators should be present
    const indicators = wrapper.findAll('[data-testid="run-indicator"]')
    expect(indicators.length).toBe(0)

    vi.useRealTimers()
  })
})
