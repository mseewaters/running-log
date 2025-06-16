<!-- frontend/src/components/QuickLogPage.vue - UPDATED -->
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
              step="0.01"
              placeholder="5.00"
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
            placeholder="MM:SS or HH:MM:SS"
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
          <div class="select-wrapper">
            <select
              data-testid="run-type-select"
              class="form-input form-select"
              v-model="formData.runType"
            >
              <option value="easy">Recovery</option>
              <option value="tempo">Tempo</option>
              <option value="interval">Interval</option>
              <option value="long">Long</option>
            </select>
            <div class="select-arrow">
              <svg width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 1L6 6L11 1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
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

        <!-- Progress Section - Now using reusable component -->
        <ProgressSection
          :isLoading="false"
          :targets="targets"
          :allRuns="allRuns"
        />

        <!-- Action buttons -->
        <div class="action-buttons">
          <button @click="resetForm" class="secondary-button">
            Log Another Run
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import ProgressSection from './ProgressSection.vue'
import { runApi, targetApi, type RunResponse, type TargetResponse } from '@/services/api'

// State management
const isLoading = ref(false)
const showSuccess = ref(false)
const savedRunData = ref<RunResponse | null>(null)
const targets = ref<TargetResponse[]>([])
const allRuns = ref<RunResponse[]>([])

// Form data
const formData = ref({
  date: getTodaysDate(),
  distance: '',
  time: '',
  runType: 'easy'
})

// Error handling
const errors = ref({
  distance: '',
  time: '',
  general: ''
})

// Load initial data
onMounted(async () => {
  await loadTargets()
  await loadAllRuns()
})

// Utility function to get today's date in YYYY-MM-DD format
function getTodaysDate(): string {
  const today = new Date()
  return today.toISOString().split('T')[0]
}

// Format date for display
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Validation functions
const validateDistance = (distance: string): string => {
  if (!distance) return 'Distance is required'
  const num = parseFloat(distance)
  if (isNaN(num) || num <= 0) return 'Distance must be a positive number'
  if (num > 200) return 'Distance seems too high'
  return ''
}

// Enhanced time validation that accepts multiple formats
const validateTime = (time: string): string => {
  if (!time) return 'Time is required'

  // Remove any whitespace
  const cleanTime = time.trim()

  // Accept these formats:
  // MM:SS (e.g., "30:00" = 30 minutes)
  // H:MM:SS (e.g., "1:30:00" = 1 hour 30 minutes)
  // HH:MM:SS (e.g., "01:30:00" = 1 hour 30 minutes)
  const timePatterns = [
    /^(\d{1,2}):(\d{2})$/, // MM:SS format
    /^(\d{1,2}):(\d{2}):(\d{2})$/ // H:MM:SS or HH:MM:SS format
  ]

  let isValidFormat = false
  let hours = 0, minutes = 0, seconds = 0

  // Check MM:SS format first
  const mmssMatch = cleanTime.match(timePatterns[0])
  if (mmssMatch) {
    minutes = parseInt(mmssMatch[1])
    seconds = parseInt(mmssMatch[2])
    isValidFormat = true
  } else {
    // Check HH:MM:SS format
    const hhmmssMatch = cleanTime.match(timePatterns[1])
    if (hhmmssMatch) {
      hours = parseInt(hhmmssMatch[1])
      minutes = parseInt(hhmmssMatch[2])
      seconds = parseInt(hhmmssMatch[3])
      isValidFormat = true
    }
  }

  if (!isValidFormat) {
    return 'Time must be in MM:SS or HH:MM:SS format (e.g., "30:00" or "1:30:00")'
  }

  // Validate ranges
  if (seconds >= 60) return 'Seconds must be less than 60'
  if (minutes >= 60) return 'Minutes must be less than 60'
  if (hours > 12) return 'Hours seems too high for a run'

  // Check for reasonable run times
  const totalMinutes = hours * 60 + minutes + seconds / 60
  if (totalMinutes < 1) return 'Run time seems too short'
  if (totalMinutes > 600) return 'Run time seems too long (over 10 hours)'

  return ''
}

// Helper function to normalize time to HH:MM:SS format for API
const normalizeTimeFormat = (time: string): string => {
  const cleanTime = time.trim()

  // Check if it's MM:SS format
  const mmssMatch = cleanTime.match(/^(\d{1,2}):(\d{2})$/)
  if (mmssMatch) {
    const minutes = mmssMatch[1].padStart(2, '0')
    const seconds = mmssMatch[2]
    return `00:${minutes}:${seconds}`
  }

  // Check if it's H:MM:SS format (need to pad hour)
  const hmmssMatch = cleanTime.match(/^(\d{1}):(\d{2}):(\d{2})$/)
  if (hmmssMatch) {
    const hours = hmmssMatch[1].padStart(2, '0')
    const minutes = hmmssMatch[2]
    const seconds = hmmssMatch[3]
    return `${hours}:${minutes}:${seconds}`
  }

  // Already in HH:MM:SS format
  return cleanTime
}

// Load targets and runs for progress display
const loadTargets = async () => {
  try {
    targets.value = await targetApi.getTargets()
  } catch (error) {
    console.error('Failed to load targets:', error)
  }
}

const loadAllRuns = async () => {
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
  }
}

// Form submission
const handleSubmit = async () => {
  // Reset errors
  errors.value = { distance: '', time: '', general: '' }

  // Validate
  const distanceError = validateDistance(formData.value.distance)
  const timeError = validateTime(formData.value.time)

  if (distanceError) errors.value.distance = distanceError
  if (timeError) errors.value.time = timeError

  if (distanceError || timeError) return

  // Submit
  isLoading.value = true

  try {
    const runData = {
      date: formData.value.date,
      distance_km: parseFloat(formData.value.distance),
      duration: normalizeTimeFormat(formData.value.time), // Normalize time format
      run_type: formData.value.runType,
      notes: ''
    }

    const response = await runApi.createRun(runData)
    savedRunData.value = response
    showSuccess.value = true

    // Reload data to show updated progress
    await Promise.all([loadTargets(), loadAllRuns()])

  } catch (error: any) {
    console.error('Failed to save run:', error)
    if (error.response?.status === 400) {
      errors.value.general = error.response?.data?.detail || 'Invalid run data. Please check your inputs.'
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
  allRuns.value = []
  errors.value = { distance: '', time: '', general: '' }
  formData.value = {
    date: getTodaysDate(),
    distance: '',
    time: '',
    runType: 'easy'
  }
  // Reload data for next use
  loadTargets()
  loadAllRuns()
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
}

/* Header styles */
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
  padding: 0.75rem 1.5rem;
}

.page-title {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.quick-log-form {
  max-width: 600px;
}

.form-group {
  margin-bottom: 0.75rem;
}

.form-label {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 500;
  display: block;
  margin-bottom: 0.1rem;
}

/* Form inputs - consolidated and consistent */
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

.form-input::placeholder {
  color: var(--gray-placeholder);
  font-style: italic;
}

/* Date input specific fixes */
input[type="date"] {
  position: relative;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  right: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  opacity: 0.7;
}

input[type="date"]::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

/* Firefox date input */
input[type="date"]::-moz-calendar-picker-indicator {
  position: absolute;
  right: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
}

input[type="date"].form-input {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  display: flex;
  align-items: center;
  height: 44px;
}

/* Select dropdown styling */
.select-wrapper {
  position: relative;
}

.form-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: var(--white-off);
  cursor: pointer;
  padding-right: 2.5rem;
  background-image: none;
}

.form-select::-moz-focus-inner {
  border: 0;
}

.form-select::-ms-expand {
  display: none;
}

.select-arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--charcoal-dark);
}

/* Input with suffix (distance field) */
.input-with-suffix {
  position: relative;
}

.distance-input {
  padding-right: 2.5rem;
}

.input-suffix {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--gray-placeholder);
  font-size: 1rem;
  pointer-events: none;
  font-weight: 500;
}

/* Error states */
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

/* Save button */
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

/* Success message */
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

/* Action buttons */
.action-buttons {
  margin-top: 1rem;
  text-align: center;
}

.secondary-button {
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
}

.secondary-button:hover {
  background-color: rgba(255, 193, 7, 0.9);
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .page-title {
    font-size: 1rem;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
  }

  .main-content {
    padding: 1rem 1.5rem;
  }

  .header-content {
    height: 3rem;
  }

  .app-title {
    font-size: 1.75rem;
    margin-top: 0.25rem;
  }

  .form-input {
    font-size: 16px; /* Prevents iOS zoom */
    padding: 0.875rem 1rem;
    min-height: 48px;
    height: 48px; /* Force consistent height */
  }


  input[type="date"].form-input {
    height: 48px;
    padding: 0.875rem 1rem;
    line-height: normal;
  }

  /* iOS date picker fixes */
  input[type="date"].form-input::-webkit-datetime-edit {
    padding: 0;
    margin: 0;
    display: flex;
    align-items: center;
    height: 100%;
  }

  input[type="date"].form-input::-webkit-datetime-edit-fields-wrapper {
    padding: 0;
    margin: 0;
  }

  input[type="date"].form-input::-webkit-calendar-picker-indicator {
    margin: 0;
    padding: 0.25rem;
  }

  .distance-input {
    padding-right: 3.5rem;
    height: 48px;
  }

  .form-group {
    margin-bottom: 0.75rem;
  }

  .save-button {
    min-height: 48px;
    font-size: 1rem;
    padding: 1rem;
  }
}
</style>
