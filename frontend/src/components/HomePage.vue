<template>
  <div class="page-container">
    <!-- Header matching Figma -->
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">FINISH LINES</h1>
        <img
          src="@/assets/runner_noline.png"
          alt="Runner"
          class="runner-icon-small"
        />
      </div>
    </header>

    <!-- Navigation -->
    <BottomNavigation />

    <!-- Main content -->
    <main class="main-content">
      <!-- Progress Section -->
      <section class="progress-section">
        <h2 class="section-title">Progress</h2>

        <!-- Loading state -->
        <div v-if="isLoading" data-testid="progress-loading" class="loading-message">
          Loading your progress...
        </div>

        <!-- Progress content -->
        <div v-else class="progress-content">
          <!-- Monthly Progress -->
          <div v-if="currentMonthTarget" class="progress-item" data-testid="home-monthly-progress">
            <h4 class="progress-title">{{ currentMonthTarget.period_display }} Progress</h4>
            <div class="progress-details">
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
              <div class="progress-percentage">
                {{ monthlyProgress?.percentage || 0 }}% complete
              </div>
            </div>
          </div>

          <!-- Yearly Progress -->
          <div v-if="currentYearTarget" class="progress-item" data-testid="home-yearly-progress">
            <h4 class="progress-title">{{ currentYear }} Progress</h4>
            <div class="progress-details">
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
              <div class="progress-percentage">
                {{ yearlyProgress?.percentage || 0 }}% complete
              </div>
            </div>
          </div>

          <!-- No targets message -->
          <div v-if="!currentMonthTarget && !currentYearTarget && !isLoading" class="no-targets" data-testid="home-no-targets">
            <p class="no-targets-text">No targets set for this period.</p>
            <p class="no-targets-text">
              <router-link to="/plan" class="target-link">Set targets</router-link> to track your progress!
            </p>
          </div>
        </div>
      </section>

      <!-- Activity Section -->
      <section class="activity-section">
        <h2 class="section-title">Activity</h2>

        <!-- RunCalendar Component -->
        <RunCalendar :runs="allRuns" />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import RunCalendar from './RunCalendar.vue'
import { runApi, targetApi, type TargetResponse, type RunResponse } from '@/services/api'
import { calculateMonthlyTotal, calculateYearlyTotal, calculateProgress } from '@/services/progressCalculation'

// State
const isLoading = ref(true)
const targets = ref<TargetResponse[]>([])
const allRuns = ref<RunResponse[]>([])

// Get current year and month
const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1 // getMonth() returns 0-11
const currentMonthKey = `${currentYear}-${currentMonth.toString().padStart(2, '0')}`

// Computed: Current month and year targets
const currentMonthTarget = computed(() => {
  return targets.value.find(t => t.target_type === 'monthly' && t.period === currentMonthKey)
})

const currentYearTarget = computed(() => {
  return targets.value.find(t => t.target_type === 'yearly' && t.period === currentYear.toString())
})

// Computed: Aggregated progress calculations
const monthlyProgress = computed(() => {
  if (!currentMonthTarget.value) return null
  const monthlyTotal = calculateMonthlyTotal(allRuns.value, currentMonthKey)
  return calculateProgress(monthlyTotal, currentMonthTarget.value)
})

const yearlyProgress = computed(() => {
  if (!currentYearTarget.value) return null
  const yearlyTotal = calculateYearlyTotal(allRuns.value, currentYear.toString())
  return calculateProgress(yearlyTotal, currentYearTarget.value)
})

// Load data when component mounts
onMounted(async () => {
  await loadData()
})

// Load all necessary data
const loadData = async () => {
  isLoading.value = true
  try {
    // Load targets and runs in parallel
    const [targetsResult, runsResult] = await Promise.all([
      loadTargets(),
      loadAllRuns()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    isLoading.value = false
  }
}

// Load targets from API
const loadTargets = async () => {
  try {
    targets.value = await targetApi.getTargets()
  } catch (error) {
    console.error('Failed to load targets:', error)
  }
}

// Load all runs for progress calculation
const loadAllRuns = async () => {
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
  padding-bottom: 80px; /* Space for bottom navigation */
}

.app-header {
  background-color: var(--charcoal-dark);
  padding: 0rem 1rem;
  border-bottom: 6px solid var(--yellow-safety);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 3.5rem;
}

.app-title {
  color: var(--yellow-safety);
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-top: 0.5rem;
}

.runner-icon-small {
  height: 100%;
  width: auto;
  object-fit: contain;
}

.main-content {
  padding: 1.5rem;
}

.section-title {
  color: var(--white-off);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

/* Progress Section Styles */
.progress-section {
  margin-bottom: 2rem;
}

.loading-message {
  text-align: center;
  color: var(--gray-cool);
  padding: 2rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-cool);
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-item {
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid var(--gray-cool);
}

.progress-title {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-align: center;
}

.progress-details {
  text-align: center;
}

.progress-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.current-distance {
  color: var(--yellow-safety);
  font-weight: 600;
  font-size: 1.2rem;
}

.progress-separator {
  color: var(--gray-cool);
  font-size: 1rem;
}

.target-distance {
  color: var(--white-off);
  font-weight: 500;
  font-size: 1.2rem;
}

.progress-bar {
  background-color: var(--charcoal-dark);
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  background-color: var(--yellow-safety);
  height: 100%;
  border-radius: 5px;
  transition: width 0.3s ease;
}

.progress-percentage {
  color: var(--gray-cool);
  font-size: 0.9rem;
  font-weight: 500;
}

.no-targets {
  text-align: center;
  padding: 2rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-cool);
}

.no-targets-text {
  color: var(--gray-cool);
  margin-bottom: 0.5rem;
}

.target-link {
  color: var(--blue-cyan);
  text-decoration: none;
  font-weight: 500;
}

.target-link:hover {
  text-decoration: underline;
}

/* Activity Section Styles */
.activity-section {
  margin-bottom: 2rem;
}
</style>
