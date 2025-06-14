// frontend/src/services/progressCalculation.ts
import type { RunResponse, TargetResponse } from '@/services/api'

/**
 * Calculate total distance for all runs in a specific month
 * @param runs Array of user's runs
 * @param period Month period in format "YYYY-MM" (e.g., "2025-06")
 * @returns Total distance in kilometers for that month
 */
export function calculateMonthlyTotal(runs: RunResponse[], period: string): number {
  if (!runs || runs.length === 0) {
    return 0
  }

  const total = runs
    .filter(run => {
      // Extract YYYY-MM from run date (YYYY-MM-DD format)
      const runMonth = run.date.substring(0, 7) // "2025-06-15" -> "2025-06"
      return runMonth === period
    })
    .reduce((sum, run) => sum + run.distance_km, 0)

  // Round to 1 decimal place to avoid floating point precision issues
  return Math.round(total * 10) / 10
}

/**
 * Calculate total distance for all runs in a specific year
 * @param runs Array of user's runs
 * @param period Year period in format "YYYY" (e.g., "2025")
 * @returns Total distance in kilometers for that year
 */
export function calculateYearlyTotal(runs: RunResponse[], period: string): number {
  if (!runs || runs.length === 0) {
    return 0
  }

  const total = runs
    .filter(run => {
      // Extract YYYY from run date (YYYY-MM-DD format)
      const runYear = run.date.substring(0, 4) // "2025-06-15" -> "2025"
      return runYear === period
    })
    .reduce((sum, run) => sum + run.distance_km, 0)

  // Round to 1 decimal place to avoid floating point precision issues
  return Math.round(total * 10) / 10
}

/**
 * Calculate progress information for a target
 * @param currentDistance Current aggregated distance achieved
 * @param target Target object with distance goal
 * @returns Progress object with current, target, percentage, and remaining
 */
export function calculateProgress(currentDistance: number, target: TargetResponse | undefined) {
  if (!target) {
    return null
  }

  const percentage = Math.round((currentDistance / target.distance_km) * 100)
  const remaining = Math.round((target.distance_km - currentDistance) * 10) / 10

  return {
    current: currentDistance,
    target: target.distance_km,
    percentage: Math.min(percentage, 100), // Cap at 100%
    remaining: Math.max(remaining, 0) // Don't show negative remaining
  }
}
