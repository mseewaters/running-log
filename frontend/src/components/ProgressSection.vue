<!-- frontend/src/components/ProgressSection.vue -->
<template>
  <section class="progress-section">
    <h2 class="section-title">Progress</h2>

    <!-- Loading state -->
    <div v-if="isLoading" data-testid="progress-loading" class="loading-message">
      Loading your progress...
    </div>

    <!-- Progress content -->
    <div v-else class="progress-content">
      <!-- Monthly Progress -->
      <div v-if="currentMonthTarget" class="progress-item" data-testid="monthly-progress">
        <div class="progress-header">
          <h4 class="progress-title">{{ currentMonthTarget.period_display }}</h4>
          <div class="time-progress">{{ monthTimeProgress }}% through month</div>
        </div>
        <div class="progress-stats">
          <span class="current-distance">{{ monthlyProgress?.current || 0 }}km</span>
          <span class="progress-separator">of</span>
          <span class="target-distance">{{ currentMonthTarget.distance_km }}km</span>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${monthlyProgress?.percentage || 0}%` }"
          ></div>
        </div>
        <div class="progress-footer">
          <span class="progress-percentage">{{ monthlyProgress?.percentage || 0 }}% complete</span>
          <span class="pace-indicator" :class="paceClass(monthlyProgress?.percentage || 0, monthTimeProgress)">
            {{ getPaceIndicator(monthlyProgress?.percentage || 0, monthTimeProgress) }}
          </span>
        </div>
      </div>

      <!-- Yearly Progress -->
      <div v-if="currentYearTarget" class="progress-item" data-testid="yearly-progress">
        <div class="progress-header">
          <h4 class="progress-title">{{ currentYear }}</h4>
          <div class="time-progress">{{ yearTimeProgress }}% through year</div>
        </div>
        <div class="progress-stats">
          <span class="current-distance">{{ yearlyProgress?.current || 0 }}km</span>
          <span class="progress-separator">of</span>
          <span class="target-distance">{{ currentYearTarget.distance_km }}km</span>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${yearlyProgress?.percentage || 0}%` }"
          ></div>
        </div>
        <div class="progress-footer">
          <span class="progress-percentage">{{ yearlyProgress?.percentage || 0 }}% complete</span>
          <span class="pace-indicator" :class="paceClass(yearlyProgress?.percentage || 0, yearTimeProgress)">
            {{ getPaceIndicator(yearlyProgress?.percentage || 0, yearTimeProgress) }}
          </span>
        </div>
      </div>

      <!-- No targets message -->
      <div v-if="!currentMonthTarget && !currentYearTarget && !isLoading" class="no-targets" data-testid="no-targets">
        <p class="no-targets-text">No targets set for this period.</p>
        <p class="no-targets-text">
          <router-link to="/plan" class="target-link">Set targets</router-link> to track your progress!
        </p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TargetResponse, RunResponse } from '@/services/api'
import { calculateMonthlyTotal, calculateYearlyTotal, calculateProgress } from '@/services/progressCalculation'

// Props
interface Props {
  isLoading: boolean
  targets: TargetResponse[]
  allRuns: RunResponse[]
}

const props = defineProps<Props>()

// Constants
const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1
const currentMonthKey = `${currentYear}-${currentMonth.toString().padStart(2, '0')}`

// Composable for time-based progress calculations
const useTimeProgress = () => {
  const monthTimeProgress = computed(() => {
    const now = new Date()
    const currentDay = now.getDate()
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate()
    return Math.round((currentDay / daysInMonth) * 100)
  })

  const yearTimeProgress = computed(() => {
    const now = new Date()
    const startOfYear = new Date(currentYear, 0, 1)
    const endOfYear = new Date(currentYear + 1, 0, 1)
    const totalYearMs = endOfYear.getTime() - startOfYear.getTime()
    const elapsedMs = now.getTime() - startOfYear.getTime()
    return Math.round((elapsedMs / totalYearMs) * 100)
  })

  return {
    monthTimeProgress,
    yearTimeProgress
  }
}

// Composable for target calculations
const useTargetProgress = () => {
  const currentMonthTarget = computed(() => {
    return props.targets.find(t => t.target_type === 'monthly' && t.period === currentMonthKey)
  })

  const currentYearTarget = computed(() => {
    return props.targets.find(t => t.target_type === 'yearly' && t.period === currentYear.toString())
  })

  const monthlyProgress = computed(() => {
    if (!currentMonthTarget.value) return null
    const monthlyTotal = calculateMonthlyTotal(props.allRuns, currentMonthKey)
    return calculateProgress(monthlyTotal, currentMonthTarget.value)
  })

  const yearlyProgress = computed(() => {
    if (!currentYearTarget.value) return null
    const yearlyTotal = calculateYearlyTotal(props.allRuns, currentYear.toString())
    return calculateProgress(yearlyTotal, currentYearTarget.value)
  })

  return {
    currentMonthTarget,
    currentYearTarget,
    monthlyProgress,
    yearlyProgress
  }
}

// Composable for pace indicators
const usePaceIndicators = () => {
  const getPaceIndicator = (distanceProgress: number, timeProgress: number): string => {
    const diff = distanceProgress - timeProgress
    if (diff >= 10) return 'Ahead of pace'
    if (diff >= 0) return 'On pace'
    if (diff >= -10) return 'Slightly behind'
    return 'Behind pace'
  }

  const paceClass = (distanceProgress: number, timeProgress: number): string => {
    const diff = distanceProgress - timeProgress
    if (diff >= 10) return 'pace-ahead'
    if (diff >= 0) return 'pace-on-track'
    if (diff >= -10) return 'pace-behind'
    return 'pace-way-behind'
  }

  return {
    getPaceIndicator,
    paceClass
  }
}

// Use composables
const { monthTimeProgress, yearTimeProgress } = useTimeProgress()
const {
  currentMonthTarget,
  currentYearTarget,
  monthlyProgress,
  yearlyProgress
} = useTargetProgress()
const { getPaceIndicator, paceClass } = usePaceIndicators()
</script>

<style scoped>
/* Progress Section Styles - Compact for mobile */
.progress-section {
  margin-bottom: 1.5rem;
}

.section-title {
  color: var(--white-off);
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.loading-message {
  text-align: center;
  color: var(--gray-cool);
  padding: 1rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.5rem;
  border: 1px solid var(--gray-cool);
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-item {
  background-color: var(--charcoal-medium);
  border-radius: 0.5rem;
  padding: 0.1rem;
  border: 1px solid var(--gray-cool);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-title {
  color: var(--white-off);
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
}

.time-progress {
  color: var(--gray-cool);
  font-size: 0.8rem;
  font-weight: 500;
}

.progress-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.current-distance {
  color: var(--yellow-safety);
  font-weight: 600;
  font-size: 1rem;
}

.progress-separator {
  color: var(--gray-cool);
  font-size: 0.85rem;
}

.target-distance {
  color: var(--white-off);
  font-weight: 500;
  font-size: 1rem;
}

.progress-bar {
  background-color: var(--charcoal-dark);
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  background-color: var(--yellow-safety);
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-percentage {
  color: var(--gray-cool);
  font-size: 0.8rem;
  font-weight: 500;
}

.pace-indicator {
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.pace-ahead {
  color: var(--green-success);
  background-color: var(--charcoal-dark);
}

.pace-on-track {
  color: var(--white-off);
  background-color: var(--charcoal-dark);
}

.pace-behind {
  color: #ffa726;
  background-color: var(--charcoal-dark);
}

.pace-way-behind {
  color: var(--red-alert);
  background-color: var(--charcoal-dark);
}

.no-targets {
  text-align: center;
  padding: 1.5rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.5rem;
  border: 1px solid var(--gray-cool);
}

.no-targets-text {
  color: var(--gray-cool);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.target-link {
  color: var(--blue-cyan);
  text-decoration: none;
  font-weight: 500;
}

.target-link:hover {
  text-decoration: underline;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .progress-item {
    padding: 0.875rem;
  }

  .progress-header {
    margin-bottom: 0.5rem;
  }

  .progress-title {
    font-size: 0.9rem;
  }

  .time-progress {
    font-size: 0.75rem;
  }

  .current-distance,
  .target-distance {
    font-size: 0.95rem;
  }

  .progress-separator {
    font-size: 0.8rem;
  }

  .progress-bar {
    height: 5px;
  }

  .progress-percentage,
  .pace-indicator {
    font-size: 0.75rem;
  }

  .pace-indicator {
    padding: 0.2rem 0.4rem;
  }
}
</style>
