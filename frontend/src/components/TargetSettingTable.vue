<!-- frontend/src/components/TargetSettingPage.vue - COMPLETE PAGE -->
<template>
  <div class="page-container">
    <!-- Header matching HomePage -->
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
      <div class="target-table-container">
        <h2 class="section-title">Set Your Running Targets</h2>
      </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-message">
      Loading your targets and progress...
    </div>

    <!-- Target table -->
    <div v-else class="target-table">
      <!-- Yearly Target Row -->
      <div class="target-row yearly-row">
        <div class="period-label">
          <strong>{{ currentYear }} Target</strong>
        </div>
        <div class="target-cell" @click="editYearlyTarget">
          <span v-if="!editingYearly" class="target-value yearly-target">
            {{ yearlyTarget ? `${yearlyTarget.distance_km.toFixed(1)} km` : 'Click to set' }}
          </span>
          <input
            v-else
            ref="yearlyInput"
            v-model="editYearlyValue"
            @blur="saveYearlyTarget"
            @keyup.enter="saveYearlyTarget"
            @keyup.escape="cancelYearlyEdit"
            class="target-input"
            type="number"
            min="0"
            max="10000"
            step="1"
          />
        </div>
        <div class="actual-cell">
          <span class="actual-value">{{ yearlyActual.toFixed(1) }} km</span>
        </div>
      </div>

      <!-- Separator -->
      <div class="table-separator"></div>



      <!-- Monthly Target Rows -->
      <div
        v-for="month in monthsData"
        :key="month.key"
        class="target-row monthly-row"
        :class="{ 'past-month': month.isPast, 'current-month': month.isCurrent }"
      >
        <div class="period-label">
          {{ month.label }}
        </div>
        <div class="target-cell" @click="editMonthlyTarget(month)">
          <span
            v-if="!month.isEditing"
            class="target-value"
            :class="{
              'past-target': month.isPast,
              'auto-target': month.isAutoCalculated,
              'user-target': month.hasUserTarget
            }"
          >
            {{ getMonthlyTargetDisplay(month) }}
          </span>
          <input
            v-else
            :ref="`monthlyInput-${month.key}`"
            v-model="month.editValue"
            @blur="saveMonthlyTarget(month)"
            @keyup.enter="saveMonthlyTarget(month)"
            @keyup.escape="cancelMonthlyEdit(month)"
            class="target-input"
            type="number"
            min="0"
            max="500"
            step="0.1"
          />
        </div>
        <div class="actual-cell">
          <span class="actual-value">{{ month.actual.toFixed(1) }} km</span>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="legend">
      <div class="legend-item">
        <span class="legend-color your-targets"></span>
        <span>Your Targets</span>
      </div>
      <div class="legend-item">
        <span class="legend-color actual-value"></span>
        <span>Actual Distance</span>
      </div>
    </div>

    <!-- Save Status -->
    <div v-if="saveStatus" class="save-status" :class="saveStatus.type">
      {{ saveStatus.message }}
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import { targetApi, runApi, type TargetResponse, type RunResponse } from '@/services/api'
import { calculateMonthlyTotal, calculateYearlyTotal } from '@/services/progressCalculation'

// State management
const isLoading = ref(true)
const targets = ref<TargetResponse[]>([])
const allRuns = ref<RunResponse[]>([])
const saveStatus = ref<{ type: 'success' | 'error', message: string } | null>(null)

// Yearly target editing
const editingYearly = ref(false)
const editYearlyValue = ref('')

// TEMP Add these reactive refs (like yearly target)
const editingJune = ref(false)
const editJuneValue = ref('')

// Monthly target editing
interface MonthData {
  key: string
  label: string
  isPast: boolean
  isCurrent: boolean
  isEditing: boolean
  editValue: string
  actual: number
  hasUserTarget: boolean
  isAutoCalculated: boolean
  userTarget?: TargetResponse
}

// Constants
const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1
const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

// Composable for target calculations
const useTargetCalculations = () => {
  const yearlyTarget = computed(() => {
    return targets.value.find(t => t.target_type === 'yearly' && t.period === currentYear.toString())
  })

  const yearlyActual = computed(() => {
    return calculateYearlyTotal(allRuns.value, currentYear.toString())
  })

  const monthlyTargets = computed(() => {
    return targets.value.filter(t => t.target_type === 'monthly')
  })

  const getMonthlyActual = (monthIndex: number): number => {
    const monthKey = `${currentYear}-${(monthIndex + 1).toString().padStart(2, '0')}`
    return calculateMonthlyTotal(allRuns.value, monthKey)
  }

  const calculateAutoMonthlyTargets = (): Record<string, number> => {
    if (!yearlyTarget.value) return {}

    const totalYearTarget = yearlyTarget.value.distance_km
    let remainingTarget = totalYearTarget

    // Subtract actual distance from completed months
    for (let i = 0; i < currentMonth - 1; i++) {
      remainingTarget -= getMonthlyActual(i)
    }

    // Subtract user-set monthly targets for remaining months
    const userSetMonths = new Set<number>()
    monthlyTargets.value.forEach(target => {
      const [year, month] = target.period.split('-')
      if (year === currentYear.toString()) {
        const monthIndex = parseInt(month) - 1
        if (monthIndex >= currentMonth - 1) { // Current month and future
          remainingTarget -= target.distance_km
          userSetMonths.add(monthIndex)
        }
      }
    })

    // Calculate months without user targets (from current month onwards)
    const monthsWithoutTargets = []
    for (let i = currentMonth - 1; i < 12; i++) {
      if (!userSetMonths.has(i)) {
        monthsWithoutTargets.push(i)
      }
    }

    // Distribute remaining target across months without user targets
    const autoTargets: Record<string, number> = {}
    if (monthsWithoutTargets.length > 0 && remainingTarget > 0) {
      const autoTargetPerMonth = remainingTarget / monthsWithoutTargets.length
      monthsWithoutTargets.forEach(monthIndex => {
        const monthKey = `${currentYear}-${(monthIndex + 1).toString().padStart(2, '0')}`
        autoTargets[monthKey] = Math.round(autoTargetPerMonth * 10) / 10 // Round to 1 decimal
      })
    }

    return autoTargets
  }

  return {
    yearlyTarget,
    yearlyActual,
    monthlyTargets,
    getMonthlyActual,
    calculateAutoMonthlyTargets
  }
}

// Use composables
const {
  yearlyTarget,
  yearlyActual,
  monthlyTargets,
  getMonthlyActual,
  calculateAutoMonthlyTargets
} = useTargetCalculations()

// Computed months data
const monthsData = computed((): MonthData[] => {
  const autoTargets = calculateAutoMonthlyTargets()

  return monthNames.map((name, index) => {
    const monthKey = `${currentYear}-${(index + 1).toString().padStart(2, '0')}`
    const userTarget = monthlyTargets.value.find(t => t.period === monthKey)
    const hasUserTarget = !!userTarget
    const isAutoCalculated = !hasUserTarget && !!autoTargets[monthKey]

    return {
      key: monthKey,
      label: name,
      isPast: index < currentMonth - 1,
      isCurrent: index === currentMonth - 1,
      isEditing: false,
      editValue: '',
      actual: getMonthlyActual(index),
      hasUserTarget,
      isAutoCalculated,
      userTarget
    }
  })
})

// Display helpers
const getMonthlyTargetDisplay = (month: MonthData): string => {
  if (month.hasUserTarget && month.userTarget) {
    return `${month.userTarget.distance_km.toFixed(1)} km`
  }
  if (month.isAutoCalculated) {
    const autoTargets = calculateAutoMonthlyTargets()
    return `Auto: ${autoTargets[month.key].toFixed(1)} km`
  }
  return 'Click to set'
}

// Yearly target editing
const editYearlyTarget = async () => {
  editingYearly.value = true
  editYearlyValue.value = yearlyTarget.value ? yearlyTarget.value.distance_km.toString() : ''
  await nextTick()
  const input = document.querySelector('.target-input') as HTMLInputElement
  input?.focus()
  input?.select()
}

const saveYearlyTarget = async () => {
  const value = parseFloat(editYearlyValue.value)
  if (isNaN(value) || value < 0) {
    showSaveStatus('error', 'Please enter a valid distance')
    return
  }

  try {
    if (yearlyTarget.value) {
      // Update existing target
      await targetApi.updateTarget(yearlyTarget.value.target_id, {
        target_type: 'yearly',
        period: currentYear.toString(),
        distance_km: value
      })
    } else {
      // Create new target
      await targetApi.createTarget({
        target_type: 'yearly',
        period: currentYear.toString(),
        distance_km: value
      })
    }

    await loadTargets()
    showSaveStatus('success', 'Yearly target saved!')
  } catch (error) {
    console.error('Failed to save yearly target:', error)
    showSaveStatus('error', 'Failed to save target')
  }

  editingYearly.value = false
}

const cancelYearlyEdit = () => {
  editingYearly.value = false
  editYearlyValue.value = ''
}

// TEMP Add this function (like yearly target)
const editJuneTarget = async () => {
  console.log('June target clicked - using yearly-style approach')
  editingJune.value = true
  editJuneValue.value = '' // or existing value
  await nextTick()
  // Focus logic here
}

const saveJuneTarget = async () => {
  const value = parseFloat(editJuneValue.value)
  // Save logic here...
  editingJune.value = false
}

// Monthly target editing
const editMonthlyTarget = async (month: MonthData) => {

  console.log('Monthly target clicked:', month.label, month) // Add this
  console.log('isPast:', month.isPast, 'hasUserTarget:', month.hasUserTarget) // Add this

  if (month.isPast) return // Don't allow editing past months

  month.isEditing = true
  month.editValue = month.hasUserTarget && month.userTarget
    ? month.userTarget.distance_km.toString()
    : ''

  await nextTick()
  const input = document.querySelector(`[ref="monthlyInput-${month.key}"]`) as HTMLInputElement
  input?.focus()
  input?.select()
}

const saveMonthlyTarget = async (month: MonthData) => {
  const value = parseFloat(month.editValue)
  if (isNaN(value) || value < 0) {
    showSaveStatus('error', 'Please enter a valid distance')
    return
  }

  // Add loading state
  const originalValue = month.editValue
  month.editValue = 'Saving...'

  try {
    if (month.hasUserTarget && month.userTarget) {
      // Update existing target
      await targetApi.updateTarget(month.userTarget.target_id, {
        target_type: 'monthly',
        period: month.key,
        distance_km: value
      })
    } else {
      // Create new target
      await targetApi.createTarget({
        target_type: 'monthly',
        period: month.key,
        distance_km: value
      })
    }

    await loadTargets()
    showSaveStatus('success', `${month.label} target saved!`)
  } catch (error) {
    console.error('Failed to save monthly target:', error)
    showSaveStatus('error', 'Failed to save target')
    month.isEditing = false
  }


}

const cancelMonthlyEdit = (month: MonthData) => {
  month.isEditing = false
  month.editValue = ''
}

// Data loading
const loadTargets = async () => {
  try {
    targets.value = await targetApi.getTargets()
  } catch (error) {
    console.error('Failed to load targets:', error)
  }
}

const loadRuns = async () => {
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
  }
}

// Utility functions
const showSaveStatus = (type: 'success' | 'error', message: string) => {
  saveStatus.value = { type, message }
  setTimeout(() => {
    saveStatus.value = null
  }, 3000)
}

// Lifecycle
onMounted(async () => {
  console.log('Component mounted, loading data...')
  isLoading.value = true
  try {
    await Promise.all([loadTargets(), loadRuns()])
  } finally {
    isLoading.value = false
  }
})

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

.target-table-container {
  max-width: 600px;
  margin: 0 auto;
}

.section-title {
  color: var(--white-off);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  text-align: center;
}

.loading-message {
  text-align: center;
  color: var(--gray-cool);
  padding: 2rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-cool);
}

.target-table {
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-cool);
  overflow: hidden;
}

.target-row {
  display: grid;
  grid-template-columns: 2fr 2fr 1.5fr;
  align-items: center;
  min-height: 3rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--gray-cool);
}

.target-row:last-child {
  border-bottom: none;
}

.yearly-row {
  background-color: var(--charcoal-dark);
  font-weight: 600;
}

.monthly-row:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.past-month {
  opacity: 0.7;
}

.current-month {
  background-color: rgba(255, 193, 7, 0.1);
}

.table-separator {
  height: 2px;
  background-color: var(--yellow-safety);
  margin: 0;
}

.period-label {
  color: var(--white-off);
  font-weight: 500;
}

.target-cell {
  text-align: center;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.target-cell:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.past-month .target-cell {
  cursor: default;
}

.past-month .target-cell:hover {
  background-color: transparent;
}

.target-value {
  font-weight: 600;
  font-size: 0.95rem;
}

.yearly-target {
  color: var(--yellow-safety);
  font-size: 1.1rem;
}

.user-target {
  color: var(--yellow-safety);
}

.auto-target {
  color: var(--yellow-safety);
  font-style: italic;
  opacity: 0.8;
}

.past-target {
  color: var(--gray-cool);
}

.target-input {
  width: 80px;
  padding: 0.25rem 0.5rem;
  background-color: red !important; /* Make it obvious var(--white-off); */
  border: 2px solid var(--yellow-safety);
  border-radius: 0.25rem;
  color: var(--charcoal-dark);
  font-size: 0.9rem;
  text-align: center;
}

.target-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 193, 7, 0.3);
}

.actual-cell {
  text-align: right;
}

.actual-value {
  color: var(--blue-cyan);
  font-weight: 600;
  font-size: 0.95rem;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.5rem;
  border: 1px solid var(--gray-cool);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--white-off);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  font-weight: 600;
}

.legend-color.your-targets {
  background-color: var(--yellow-safety);
}

.legend-color.actual-value {
  background-color: var(--blue-cyan);
}

.save-status {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  text-align: center;
  font-weight: 500;
}

.save-status.success {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.save-status.error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--red-alert);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .header-content {
    height: 3rem;
  }

  .app-title {
    font-size: 1.75rem;
    margin-top: 0.25rem;
  }

  .main-content {
    padding: 1rem 1.5rem;
  }

  .target-table-container {
    margin: 0;
  }

  .section-title {
    font-size: 1.25rem;
    margin-bottom: 1rem;
  }

  .target-row {
    grid-template-columns: 2fr 1.5fr 1fr;
    min-height: 2.5rem;
    padding: 0.5rem 0.75rem;
  }

  .period-label {
    font-size: 0.9rem;
  }

  .target-value {
    font-size: 0.85rem;
  }

  .yearly-target {
    font-size: 1rem;
  }

  .target-input {
    width: 70px;
    font-size: 0.85rem;
  }

  .legend {
    gap: 0.75rem;
    padding: 0.75rem;
  }

  .legend-item {
    font-size: 0.8rem;
  }
}
</style>
