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
        <h2 class="section-title">Click to set or edit your targets</h2>
        <p v-if="yearlyTarget" class="auto-explanation">Monthly targets calculated from yearly goal</p>
      </div>

      <!-- Loading state -->
      <div v-if="isLoading" class="loading-message">
        Loading your targets and progress...
      </div>

      <!-- Target table -->
      <div v-else class="target-table">
        <!-- Table Headers -->
        <div class="table-header">
          <div class="header-period">Period</div>
          <div class="header-target">Target</div>
          <div class="header-actual">Actual</div>
        </div>
        <!-- Yearly Target Row -->
        <div class="target-row yearly-row" @click="openYearlyModal">
          <div class="period-label">
            <strong>{{ currentYear }} Target</strong>
          </div>
          <div class="target-cell clickable">
            <span class="target-value yearly-target">
              {{ yearlyTarget ? `${yearlyTarget.distance_km.toFixed(1)} km` : 'Set target' }}
            </span>
          </div>
          <div class="actual-cell">
            <span class="actual-value yearly-actual">{{ yearlyActual.toFixed(1) }} km</span>
          </div>
        </div>

        <!-- Yearly to Monthly Separator -->
        <div class="table-separator"></div>

        <!-- Monthly Target Rows -->
        <div
          v-for="month in monthsData"
          :key="month.key"
          class="target-row monthly-row"
          :class="{
            'past-month': month.isPast,
            'current-month': month.isCurrent,
            'clickable': !month.isPast
          }"
          @click="openMonthlyModal(month)"
        >
          <div class="period-label">
            {{ month.label }}
          </div>
          <div class="target-cell">
            <span
              class="target-value"
              :class="{
                'past-target': month.isPast,
                'auto-target': month.isAutoCalculated,
                'user-target': month.hasUserTarget
              }"
            >
              {{ getMonthlyTargetDisplay(month) }}
            </span>
          </div>
          <div class="actual-cell">
            <span class="actual-value">{{ month.actual.toFixed(1) }} km</span>
          </div>
        </div>
      </div>

      <!-- Save Status Toast -->
      <div v-if="saveStatus" class="save-status" :class="saveStatus.type">
        {{ saveStatus.message }}
      </div>
    </main>

    <!-- Target Edit Modal -->
    <TargetEditModal
      :isOpen="modalOpen"
      :monthKey="selectedMonthKey"
      :displayName="selectedDisplayName"
      :existingTarget="selectedTarget"
      @close="closeModal"
      @success="handleModalSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import TargetEditModal from './TargetEditModal.vue'
import { targetApi, runApi, type TargetResponse, type RunResponse } from '@/services/api'
import { calculateMonthlyTotal, calculateYearlyTotal } from '@/services/progressCalculation'

// State management
const isLoading = ref(true)
const targets = ref<TargetResponse[]>([])
const allRuns = ref<RunResponse[]>([])
const saveStatus = ref<{ type: 'success' | 'error', message: string } | null>(null)

// Modal state
const modalOpen = ref(false)
const selectedMonthKey = ref('')
const selectedDisplayName = ref('')
const selectedTarget = ref<TargetResponse | null>(null)

// Monthly target data interface
interface MonthData {
  key: string
  label: string
  isPast: boolean
  isCurrent: boolean
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

// Computed: Yearly target and actual
const yearlyTarget = computed(() => {
  return targets.value.find(t => t.target_type === 'yearly' && t.period === currentYear.toString())
})

const yearlyActual = computed(() => {
  return calculateYearlyTotal(allRuns.value, currentYear.toString())
})

// Computed: Monthly targets
const monthlyTargets = computed(() => {
  return targets.value.filter(t => t.target_type === 'monthly')
})

// Helper: Get actual distance for a month
const getMonthlyActual = (monthIndex: number): number => {
  const monthKey = `${currentYear}-${(monthIndex + 1).toString().padStart(2, '0')}`
  return calculateMonthlyTotal(allRuns.value, monthKey)
}

// Helper: Calculate auto monthly targets
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

// Computed: Months data for display
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
      actual: getMonthlyActual(index),
      hasUserTarget,
      isAutoCalculated,
      userTarget
    }
  })
})

// Display helper: Get monthly target display text
const getMonthlyTargetDisplay = (month: MonthData): string => {
  if (month.hasUserTarget && month.userTarget) {
    return `${month.userTarget.distance_km.toFixed(1)} km`
  }
  if (month.isAutoCalculated) {
    const autoTargets = calculateAutoMonthlyTargets()
    return `${autoTargets[month.key].toFixed(1)} km`
  }
  return 'Set target'
}

// Helper: Check if target is auto-calculated for styling
const isAutoCalculated = (month: MonthData): boolean => {
  return month.isAutoCalculated
}

// Modal handlers
const openYearlyModal = () => {
  selectedMonthKey.value = currentYear.toString()
  selectedDisplayName.value = `${currentYear}`  // Just the year
  selectedTarget.value = yearlyTarget.value || null
  modalOpen.value = true
}

const openMonthlyModal = (month: MonthData) => {
  // Don't allow editing past months
  if (month.isPast) return

  selectedMonthKey.value = month.key
  selectedDisplayName.value = `${month.label} ${currentYear}`  // "June 2025"
  selectedTarget.value = month.userTarget || null
  modalOpen.value = true
}

const closeModal = () => {
  modalOpen.value = false
  selectedMonthKey.value = ''
  selectedDisplayName.value = ''
  selectedTarget.value = null
}

const handleModalSuccess = async () => {
  // Reload data and close modal
  await loadTargets()
  closeModal()
  showSaveStatus('success', 'Target saved successfully!')
}

// Data loading
const loadTargets = async () => {
  try {
    targets.value = await targetApi.getTargets()
  } catch (error) {
    console.error('Failed to load targets:', error)
    showSaveStatus('error', 'Failed to load targets')
  }
}

const loadRuns = async () => {
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
    showSaveStatus('error', 'Failed to load runs')
  }
}

// Utility: Show save status toast
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
/* Base styles - same as original but with clickable improvements */
.page-container {
  min-height: 100vh;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
  padding-bottom: 80px;
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
  padding: 1rem;
}

.target-table-container {
  max-width: 800px;
  margin: 0 auto;
}

.section-title {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 0.1rem;
  text-align: left;
  opacity: 0.9;
}

.auto-explanation {
  color: var(--yellow-safety);
  font-size: 0.75rem;
  font-style: italic;
  text-align: left;
  margin-bottom: 0.5rem;
  opacity: 0.8;
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

.table-header {
  display: grid;
  grid-template-columns: 1.5fr 2.5fr 1.5fr;  /* More space for target column */
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--charcoal-dark);
  border-bottom: 2px solid var(--yellow-safety);
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--white-off);
}

.header-period {
  color: var(--white-off);
}

.header-target {
  text-align: center;
  color: var(--yellow-safety);
}

.header-actual {
  text-align: right;
  color: var(--blue-cyan);
}

.target-row {
  display: grid;
  grid-template-columns: 1.5fr 2.5fr 1.5fr;  /* Match header proportions */
  align-items: center;
  min-height: 3rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--gray-cool);
  transition: background-color 0.2s;
}

.target-row:last-child {
  border-bottom: none;
}

.target-row.clickable {
  cursor: pointer;
}

.target-row.clickable:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.yearly-row {
  background-color: var(--charcoal-dark);
  font-weight: 600;
}

.yearly-row:hover {
  background-color: rgba(255, 193, 7, 0.05);
}

.monthly-row {
  background-color: var(--charcoal-dark); /* Active months match yearly row */
}

.monthly-row:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.past-month {
  background-color: var(--charcoal-medium) !important; /* Past months are lighter/inactive */
  opacity: 0.7;
  cursor: default !important;
}

.past-month:hover {
  background-color: var(--charcoal-medium) !important; /* No hover effect for past months */
}

.current-month {
  background-color: rgba(255, 193, 7, 0.1); /* Current month gets yellow tint */
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
  padding: 0.1rem;
  border-radius: 0.25rem;
}

.target-value {
  font-weight: 600;
  font-size: 0.95rem;
}

.yearly-target {
  color: var(--yellow-safety);
  font-size: 0.95rem;
}

.yearly-actual {
  color: var(--blue-cyan);
  font-size: 0.95rem;
}

.user-target {
  color: var(--yellow-safety);
}

.auto-target {
  color: var(--yellow-safety);
  font-style: italic;
  opacity: 0.8;
}

.auto-prefix {
  font-size: 0.75rem;
  opacity: 0.7;
}

.past-target {
  color: var(--gray-cool);
}

.actual-cell {
  text-align: right;
  padding: 0rem;
}

.actual-value {
  color: var(--blue-cyan);
  font-weight: 500;
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
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.save-status.success {
  background-color: rgba(34, 197, 94, 0.9);
  color: white;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.save-status.error {
  background-color: rgba(239, 68, 68, 0.9);
  color: white;
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
    padding: 1rem 1rem;
  }

  .target-table-container {
    margin: 0;
  }

  .section-title {
    font-size: 1rem;
    margin-bottom: 0.1rem;
  }

  .table-header {
    grid-template-columns: 1.5fr 2fr 1fr;  /* Even more space for target on mobile */
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .target-row {
    grid-template-columns: 1.5fr 2fr 1fr;  /* Match header */
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

  .legend {
    gap: 0.75rem;
    padding: 0.75rem;
  }

  .legend-item {
    font-size: 0.8rem;
  }

  .save-status {
    top: 10px;
    right: 10px;
    left: 10px;
    text-align: center;
  }
}
</style>
