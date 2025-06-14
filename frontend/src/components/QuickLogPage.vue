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

    <!-- Navigation directly below header -->
    <BottomNavigation />

    <!-- Main content -->
    <main class="main-content">
      <h2 data-testid="page-title" class="page-title">Quick Log</h2>

      <!-- Show form when not saved -->
      <form
        v-if="!showSuccess"
        data-testid="quick-log-form"
        @submit.prevent="handleSubmit"
        class="quick-log-form"
      >
        <!-- General error message -->
        <div v-if="errors.general" class="error-message general-error">
          {{ errors.general }}
        </div>
        <!-- Date Input -->
        <div class="form-group">
          <label class="form-label">Date:</label>
          <input
            data-testid="date-input"
            type="date"
            class="form-input"
            v-model="formData.date"
          />
        </div>

        <!-- Distance Input -->
        <div class="form-group">
          <label class="form-label">Distance:</label>
          <div class="input-with-suffix">
            <input
              data-testid="distance-input"
              type="number"
              step="0.1"
              placeholder="5.0"
              class="form-input distance-input"
              :class="{ 'input-error': errors.distance }"
              v-model="formData.distance"
            />
            <span class="input-suffix">km</span>
          </div>
          <div v-if="errors.distance" data-testid="distance-error" class="error-message">
            {{ errors.distance }}
          </div>
        </div>

        <!-- Time Input -->
        <div class="form-group">
          <label class="form-label">Time:</label>
          <input
            data-testid="time-input"
            type="text"
            placeholder="H:MM:SS"
            class="form-input"
            :class="{ 'input-error': errors.time }"
            v-model="formData.time"
          />
          <div v-if="errors.time" data-testid="time-error" class="error-message">
            {{ errors.time }}
          </div>
        </div>

        <!-- Run Type Select -->
        <div class="form-group">
          <label class="form-label">Run type:</label>
          <select
            data-testid="run-type-select"
            class="form-input form-select"
            v-model="formData.runType"
          >
            <option value="easy">Easy</option>
            <option value="tempo">Tempo</option>
            <option value="intervals">Intervals</option>
            <option value="long">Long Run</option>
          </select>
        </div>

        <!-- Save Button -->
        <button
          data-testid="save-button"
          type="submit"
          class="save-button"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Saving...' : 'Save Run' }}
        </button>
      </form>

      <!-- Success Message replaces form -->
      <div v-if="showSuccess && savedRunData" class="success-message">
        <div class="success-header">✅ Run Saved!</div>
        <div class="run-summary">
          <div class="run-details">
            <p><strong>{{ savedRunData.distance_km }} km</strong> in <strong>{{ savedRunData.duration }}</strong></p>
            <p>Pace: <strong>{{ savedRunData.pace }}</strong> per km</p>
            <p>Date: {{ formatDate(savedRunData.date) }}</p>
            <p v-if="savedRunData.notes" class="notes">{{ savedRunData.notes }}</p>
          </div>
        </div>

        <!-- Target Progress Section -->
        <div class="progress-section">
          <!-- Monthly Progress -->
          <div v-if="currentMonthTarget" class="progress-item" data-testid="monthly-progress">
            <h4 class="progress-title">{{ new Date().toLocaleDateString('en-US', { month: 'long' }) }} Progress</h4>
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
          <div v-if="currentYearTarget" class="progress-item" data-testid="yearly-progress">
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
          <div v-if="!currentMonthTarget && !currentYearTarget" class="no-targets">
            <p class="progress-note">No targets set for this period.</p>
            <p class="progress-note">
              <router-link to="/plan" class="target-link">Set targets</router-link> to track your progress!
            </p>
          </div>
        </div>

        <!-- Button to log another run -->
        <button
          @click="resetForm"
          class="save-button"
          style="margin-top: 1.5rem;"
        >
          Log Another Run
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import { runApi, targetApi, type RunRequest, type TargetResponse , type RunResponse } from '@/services/api'
import { calculateMonthlyTotal, calculateYearlyTotal, calculateProgress } from '@/services/progressCalculation'


const isLoading = ref(false)
const showSuccess = ref(false)
const savedRunData = ref<any>(null)
const targets = ref<TargetResponse[]>([])
const allRuns = ref<RunResponse[]>([])

// Validation errors
const errors = ref({
  distance: '',
  time: '',
  general: ''
})

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


// Get today's date in YYYY-MM-DD format
const getTodaysDate = () => {
  const today = new Date()
  return today.toISOString().split('T')[0]
}

// Format date for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formData = ref({
  date: getTodaysDate(),
  distance: '',
  time: '',
  runType: 'easy' // Default to easy instead of blank
})

// Load all runs for progress calculation
const loadAllRuns = async () => {
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
  }
}

// Load targets when component mounts or after saving a run
const loadTargets = async () => {
  try {
    targets.value = await targetApi.getTargets()
  } catch (error) {
    console.error('Failed to load targets:', error)
  }
}

// Convert user input to strict HH:MM:SS format for backend
const formatTimeForAPI = (timeInput: string): string => {
  // If already in HH:MM:SS format, return as-is
  if (/^\d{2}:\d{2}:\d{2}$/.test(timeInput)) {
    return timeInput
  }

  // If in H:MM:SS format, pad the hour with zero
  if (/^\d{1}:\d{2}:\d{2}$/.test(timeInput)) {
    return `0${timeInput}`
  }

  // If in MM:SS format, add hours as 00:
  if (/^\d{1,2}:\d{2}$/.test(timeInput)) {
    const [minutes, seconds] = timeInput.split(':')
    return `00:${minutes.padStart(2, '0')}:${seconds}`
  }

  // Fallback - return as-is (will fail backend validation)
  return timeInput
}

// Validation functions
const validateForm = () => {
  errors.value = { distance: '', time: '', general: '' }
  let isValid = true

  // Validate distance
  if (!formData.value.distance || formData.value.distance <= 0) {
    errors.value.distance = 'Distance is required and must be greater than 0'
    isValid = false
  }

  // Validate time format (flexible: MM:SS or H:MM:SS)
  if (!formData.value.time) {
    errors.value.time = 'Time is required'
    isValid = false
  } else {
    // Allow MM:SS or H:MM:SS or HH:MM:SS
    const timeRegex = /^(\d{1,2}:)?\d{1,2}:\d{2}$/
    if (!timeRegex.test(formData.value.time)) {
      errors.value.time = 'Time must be in MM:SS or H:MM:SS format'
      isValid = false
    }
  }

  return isValid
}

// Form submission
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errors.value.general = ''

  try {
    // Format the run data with proper time format for backend
    const runData: RunRequest = {
      date: formData.value.date,
      distance_km: parseFloat(formData.value.distance),
      duration: formatTimeForAPI(formData.value.time), // Convert to HH:MM:SS
      notes: `${formData.value.runType} run`
    }

    // Save the run
    const response = await runApi.createRun(runData)

    // Store the response for display
    savedRunData.value = response

    // Load targets to show progress
    await loadTargets()
    // Reload all runs to get updated totals for progress calculation
    await loadAllRuns()

    // Show success message
    showSuccess.value = true

  } catch (error: any) {
    console.error('Run save failed:', error)

    if (error.response?.status === 422) {
      errors.value.general = 'Please check your inputs.'
    } else if (error.response?.status >= 500) {
      errors.value.general = 'Server error. Please try again later.'
    } else {
      errors.value.general = error.response?.data?.detail || 'Failed to save run. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  showSuccess.value = false
  savedRunData.value = null
  targets.value = []
  errors.value = { distance: '', time: '', general: '' }
  formData.value = {
    date: getTodaysDate(),
    distance: '',
    time: '',
    runType: 'easy'
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
}

/* Reuse header styles from HomePage */
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

.page-title {
  color: var(--white-off);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.quick-log-form {
  max-width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 500;
  display: block;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: var(--white-off);
  border: none;
  border-radius: 0.5rem;
  color: var(--charcoal-dark);
  font-size: 1rem;
  min-height: 44px;
}

.form-select {
  cursor: pointer;
}

.form-input::placeholder {
  color: var(--gray-placeholder);
}

.input-with-suffix {
  position: relative;
  display: flex;
  align-items: center;
}

.distance-input {
  padding-right: 2.5rem; /* Space for suffix */
}

.input-suffix {
  position: absolute;
  right: 1rem;
  color: var(--gray-placeholder);
  font-size: 1rem;
  pointer-events: none;
  font-weight: 500;
}

.input-error {
  border: 2px solid var(--red-alert) !important;
}

.error-message {
  color: var(--red-alert);
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

.general-error {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: 0.5rem;
  text-align: center;
}

.save-button {
  width: 100%;
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1.125rem;
  margin-top: 1.5rem;
  min-height: 44px;
  cursor: pointer;
}

.save-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.success-message {
  margin-top: 1.5rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid var(--gray-cool);
}

.success-header {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--white-off);
  text-align: center;
}

.run-summary {
  background-color: var(--charcoal-dark);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.run-details p {
  color: var(--white-off);
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

.run-details p:last-child {
  margin-bottom: 0;
}

.notes {
  font-style: italic;
  color: var(--gray-cool) !important;
  margin-top: 0.75rem;
}

/* Progress Section Styles */
.progress-section {
  margin-bottom: 1rem;
}

.progress-item {
  background-color: var(--charcoal-dark);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.progress-item:last-child {
  margin-bottom: 0;
}

.progress-title {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
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
  margin-bottom: 0.75rem;
}

.current-distance {
  color: var(--yellow-safety);
  font-weight: 600;
  font-size: 1.1rem;
}

.progress-separator {
  color: var(--gray-cool);
  font-size: 0.9rem;
}

.target-distance {
  color: var(--white-off);
  font-weight: 500;
  font-size: 1.1rem;
}

.progress-bar {
  background-color: var(--charcoal-medium);
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  background-color: var(--yellow-safety);
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-percentage {
  color: var(--gray-cool);
  font-size: 0.875rem;
}

.no-targets {
  text-align: center;
  padding: 1rem;
  background-color: var(--charcoal-dark);
  border-radius: 0.5rem;
}

.target-link {
  color: var(--blue-cyan);
  text-decoration: none;
  font-weight: 500;
}

.target-link:hover {
  text-decoration: underline;
}
</style>
