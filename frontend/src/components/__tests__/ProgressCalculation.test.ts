// frontend/src/components/__tests__/progressCalculation.test.ts
import { describe, it, expect } from 'vitest'
import { calculateMonthlyTotal, calculateYearlyTotal, calculateProgress } from '../../services/progressCalculation'

describe('Progress Calculation Helpers', () => {
  // Mock run data for testing
  const mockRuns = [
    { run_id: '1', date: '2025-06-01', distance_km: 5.0, duration: '00:30:00', pace: '06:00', notes: '' },
    { run_id: '2', date: '2025-06-05', distance_km: 3.2, duration: '00:20:00', pace: '06:15', notes: '' },
    { run_id: '3', date: '2025-06-10', distance_km: 8.5, duration: '00:45:00', pace: '05:30', notes: '' },
    { run_id: '4', date: '2025-05-28', distance_km: 4.0, duration: '00:25:00', pace: '06:15', notes: '' }, // Previous month
    { run_id: '5', date: '2024-12-15', distance_km: 6.0, duration: '00:35:00', pace: '05:50', notes: '' }, // Previous year
  ]

  // Mock target data
  const mockTargets = [
    {
      target_id: 'target1',
      user_id: 'user123',
      target_type: 'monthly',
      period: '2025-06',
      period_display: 'June 2025',
      distance_km: 50.0,
      created_at: '2025-06-01T00:00:00Z'
    },
    {
      target_id: 'target2',
      user_id: 'user123',
      target_type: 'yearly',
      period: '2025',
      period_display: '2025',
      distance_km: 500.0,
      created_at: '2025-01-01T00:00:00Z'
    }
  ]

  it('should calculate monthly aggregated distance correctly', () => {
    // RED TEST - function doesn't exist yet

    // This function should aggregate runs for June 2025
    // Expected: 5.0 + 3.2 + 8.5 = 16.7km (runs from 2025-06-*)
    // Should exclude: 4.0km from May 2025, 6.0km from December 2024

    const monthlyTotal = calculateMonthlyTotal(mockRuns, '2025-06')

    expect(monthlyTotal).toBe(16.7)
  })

  it('should calculate yearly aggregated distance correctly', () => {
    // RED TEST - function doesn't exist yet

    // This function should aggregate runs for 2025
    // Expected: 5.0 + 3.2 + 8.5 + 4.0 = 20.7km (all 2025 runs)
    // Should exclude: 6.0km from December 2024

    const yearlyTotal = calculateYearlyTotal(mockRuns, '2025')

    expect(yearlyTotal).toBe(20.7)
  })

  it('should calculate progress percentage correctly', () => {
    // RED TEST - function doesn't exist yet

    // Test monthly progress: 16.7km of 50km target
    const monthlyProgress = calculateProgress(16.7, mockTargets[0])

    expect(monthlyProgress).toEqual({
      current: 16.7,
      target: 50.0,
      percentage: 33, // Math.round((16.7/50) * 100) = 33%
      remaining: 33.3 // 50.0 - 16.7 = 33.3
    })
  })

  it('should handle empty runs array', () => {
    // RED TEST - Edge case testing

    const monthlyTotal = calculateMonthlyTotal([], '2025-06')
    const yearlyTotal = calculateYearlyTotal([], '2025')

    expect(monthlyTotal).toBe(0)
    expect(yearlyTotal).toBe(0)
  })

  it('should handle no matching runs for period', () => {
    // RED TEST - Edge case testing

    // No runs in July 2025
    const monthlyTotal = calculateMonthlyTotal(mockRuns, '2025-07')
    // No runs in 2026
    const yearlyTotal = calculateYearlyTotal(mockRuns, '2026')

    expect(monthlyTotal).toBe(0)
    expect(yearlyTotal).toBe(0)
  })
})
