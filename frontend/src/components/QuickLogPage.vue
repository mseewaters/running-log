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

        <div class="progress-placeholder">
          <p class="progress-note">Progress tracking coming soon!</p>
          <p class="progress-note">Connect targets to see monthly and yearly progress.</p>
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
import { ref } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import { runApi, type RunRequest } from '@/services/api'

const isLoading = ref(false)
const showSuccess = ref(false)
const savedRunData = ref<any>(null)

// Validation errors
const errors = ref({
  distance: '',
  time: '',
  general: ''
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

// Validation functions
const validateForm = () => {
  errors.value = { distance: '', time: '', general: '' }
  let isValid = true

  // Validate distance
  if (!formData.value.distance || formData.value.distance <= 0) {
    errors.value.distance = 'Distance is required and must be greater than 0'
    isValid = false
  }

  // Validate time format (H:MM:SS or MM:SS)
  if (!formData.value.time) {
    errors.value.time = 'Time is required'
    isValid = false
  } else {
    const timeRegex = /^(\d{1,2}:)?[0-5]?\d:[0-5]\d$/
    if (!timeRegex.test(formData.value.time)) {
      errors.value.time = 'Time must be in H:MM:SS format'
      isValid = false
    }
  }

  return isValid
}

// Convert time format to HH:MM:SS for API
const formatTimeForAPI = (timeInput: string): string => {
  // If already in proper HH:MM:SS format, return as-is
  if (/^\d{2}:\d{2}:\d{2}$/.test(timeInput)) {
    return timeInput
  }

  // If in H:MM:SS format, pad the hour
  if (/^\d{1}:\d{2}:\d{2}$/.test(timeInput)) {
    return `0${timeInput}`
  }

  // If in MM:SS format, prepend 00:
  if (/^\d{1,2}:\d{2}$/.test(timeInput)) {
    const parts = timeInput.split(':')
    const minutes = parts[0].padStart(2, '0')
    const seconds = parts[1]
    return `00:${minutes}:${seconds}`
  }

  // If in M:SS format, pad both
  if (/^\d{1}:\d{2}$/.test(timeInput)) {
    const parts = timeInput.split(':')
    const minutes = parts[0].padStart(2, '0')
    const seconds = parts[1]
    return `00:${minutes}:${seconds}`
  }

  // Default fallback - assume it's minutes:seconds and pad
  const parts = timeInput.split(':')
  if (parts.length === 2) {
    const minutes = parts[0].padStart(2, '0')
    const seconds = parts[1].padStart(2, '0')
    return `00:${minutes}:${seconds}`
  }

  // Last resort - return as-is and let backend validation catch it
  return timeInput
}

const handleSubmit = async () => {
  // Validate form first
  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    // Prepare data for API
    const runData: RunRequest = {
      date: formData.value.date,
      distance_km: parseFloat(formData.value.distance),
      duration: formatTimeForAPI(formData.value.time),
      notes: `Run type: ${formData.value.runType}`
    }

    // Call the real API!
    const savedRun = await runApi.createRun(runData)

    console.log('Run saved successfully:', savedRun)
    savedRunData.value = savedRun
    showSuccess.value = true

  } catch (error: any) {
    console.error('Error saving run:', error)

    // Handle different types of errors
    if (error.response?.status === 401) {
      errors.value.general = 'Please log in again to save your run'
    } else if (error.response?.status === 422) {
      errors.value.general = 'Invalid data format. Please check your inputs.'
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

.progress-placeholder {
  text-align: center;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.progress-note {
  color: var(--gray-cool);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}
</style>
