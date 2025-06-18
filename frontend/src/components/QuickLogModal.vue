<template>
  <!-- Modal Overlay -->
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h2 class="modal-title">Quick Log</h2>
        <button @click="closeModal" class="close-button" type="button">
          <span>&times;</span>
        </button>
      </div>

      <!-- Modal Content -->
      <div class="modal-content">
        <!-- Show form when not saved -->
        <form
          v-if="!showSuccess"
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
                type="number"
                step="0.01"
                placeholder="5.00"
                class="form-input distance-input"
                :class="{ 'input-error': errors.distance }"
                v-model="formData.distance"
              />
              <span class="input-suffix">km</span>
            </div>
            <div v-if="errors.distance" class="error-message">
              {{ errors.distance }}
            </div>
          </div>

          <!-- Time Input -->
          <div class="form-group">
            <label class="form-label">Time:</label>
            <input
              type="text"
              placeholder="MM:SS or HH:MM:SS"
              class="form-input"
              :class="{ 'input-error': errors.time }"
              v-model="formData.time"
            />
            <div v-if="errors.time" class="error-message">
              {{ errors.time }}
            </div>
          </div>

          <!-- Run Type -->
          <div class="form-group">
            <label class="form-label">Run Type:</label>
            <div class="select-wrapper">
              <select class="form-input form-select" v-model="formData.runType">
                <option value="easy">Easy</option>
                <option value="tempo">Tempo</option>
                <option value="interval">Interval</option>
                <option value="long">Long</option>
                <option value="race">Race</option>
              </select>
              <div class="select-arrow">▼</div>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="save-button"
          >
            <span v-if="isLoading">Saving...</span>
            <span v-else>Save Run</span>
          </button>
        </form>

        <!-- Success message -->
        <div v-else class="success-message">
          <div class="success-header">✅ Run Saved!</div>
          <div class="run-summary">
            <div class="run-details">
              <p><strong>{{ savedRunData?.distance_km || formData.distance }} km</strong> in <strong>{{ savedRunData?.duration || formData.time }}</strong></p>
              <p>Pace: <strong>{{ savedRunData?.pace || calculatePace() }}</strong> per km</p>
              <p>Date: {{ formatDate(savedRunData?.date || formData.date) }}</p>
            </div>
          </div>
          <div class="action-buttons">
            <button @click="resetForm" class="log-another-button">
              Log Another Run
            </button>
            <button @click="closeModal" class="close-modal-button">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { runApi } from '@/services/api'

// Props
const props = defineProps<{
  isOpen: boolean
}>()

// Emits
const emit = defineEmits<{
  close: []
  runSaved: []
}>()

// State
const isLoading = ref(false)
const showSuccess = ref(false)
const savedRunData = ref<any>(null)

const formData = reactive({
  date: getTodaysDate(),
  distance: '',
  time: '',
  runType: 'easy'
})

const errors = reactive({
  distance: '',
  time: '',
  general: ''
})

// Helper function
function getTodaysDate(): string {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Validation functions (using the proven ones from QuickLogPage)
const validateDistance = (distance: string | number): string => {
  const distanceStr = String(distance || '').trim()
  if (!distanceStr) return 'Distance is required'
  const num = parseFloat(distanceStr)
  if (isNaN(num) || num <= 0) return 'Distance must be a positive number'
  if (num > 200) return 'Distance seems too high'
  return ''
}

// Enhanced time validation that accepts multiple formats (from QuickLogPage)
const validateTime = (time: string): string => {
  if (!time) return 'Time is required'

  // Remove any whitespace
  const cleanTime = String(time || '').trim()

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

// Helper function to normalize time to HH:MM:SS format for API (from QuickLogPage)
const normalizeTimeFormat = (time: string): string => {
  const cleanTime = String(time || '').trim()

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

// Form submission
const handleSubmit = async () => {
  // Reset errors
  errors.distance = ''
  errors.time = ''
  errors.general = ''

  // Validate
  const distanceError = validateDistance(formData.distance)
  const timeError = validateTime(formData.time)

  if (distanceError) errors.distance = distanceError
  if (timeError) errors.time = timeError

  if (distanceError || timeError) return

  // Submit
  isLoading.value = true

  try {
    const runData = {
      date: formData.date,
      distance_km: parseFloat(formData.distance),
      duration: normalizeTimeFormat(formData.time),
      run_type: formData.runType,
      notes: ''
    }

    console.log('Sending run data:', runData) // Debug log
    console.log('Form date value:', formData.date)
    console.log('Form date type:', typeof formData.date)

    const response = await runApi.createRun(runData)
    savedRunData.value = response
    showSuccess.value = true
    emit('runSaved')

  } catch (error: any) {
    console.error('Failed to save run:', error)
    console.error('Error response:', error.response) // More detailed error log

    if (error.response?.status === 400 || error.response?.status === 422) {
      errors.general = error.response?.data?.detail || 'Invalid run data. Please check your inputs.'
    } else if (error.response?.status >= 500) {
      errors.general = 'Server error. Please try again later.'
    } else {
      errors.general = error.response?.data?.detail || 'Failed to save run. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  showSuccess.value = false
  savedRunData.value = null
  errors.distance = ''
  errors.time = ''
  errors.general = ''
  formData.date = getTodaysDate()
  formData.distance = ''
  formData.time = ''
  formData.runType = 'easy'
}

const closeModal = () => {
  resetForm()
  emit('close')
}

const formatDate = (dateStr: string): string => {
  // Parse the date string manually to avoid timezone issues
  const datePart = dateStr.split('T')[0] // Get just the date part (YYYY-MM-DD)
  const [year, month, day] = datePart.split('-').map(Number)

  // Create date in local timezone (not UTC)
  const date = new Date(year, month - 1, day) // month is 0-indexed

  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Calculate pace from distance and time (matching QuickLogPage logic)
const calculatePace = (): string => {
  try {
    const distance = parseFloat(formData.distance)
    const timeStr = normalizeTimeFormat(formData.time)

    if (!distance || !timeStr) return '--:--'

    // Parse HH:MM:SS to total seconds
    const [hours, minutes, seconds] = timeStr.split(':').map(Number)
    const totalSeconds = hours * 3600 + minutes * 60 + seconds

    // Calculate pace per km in seconds
    const paceSeconds = totalSeconds / distance

    // Convert back to MM:SS format
    const paceMinutes = Math.floor(paceSeconds / 60)
    const remainingSeconds = Math.round(paceSeconds % 60)

    return `${paceMinutes}:${remainingSeconds.toString().padStart(2, '0')}`
  } catch (error) {
    return '--:--'
  }
}

// Reset form when modal opens
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    resetForm()
  }
})
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background-color: var(--charcoal-dark);
  border-radius: 1rem;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid var(--gray-cool);
}

.modal-title {
  color: var(--yellow-safety);
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: var(--white-off);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: var(--gray-cool);
}

/* Modal Content */
.modal-content {
  padding: 1rem 1.5rem 1.5rem;
}

/* Form Styles */
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

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: var(--white-off);
  border: none;
  border-radius: 0.5rem;
  color: var(--charcoal-dark);
  font-size: 1rem;
  min-height: 44px;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: var(--gray-placeholder);
  font-style: italic;
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

/* Input with suffix */
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

/* Select dropdown */
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
}

.select-arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--charcoal-dark);
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
  transition: background-color 0.2s;
}

.save-button:hover:not(:disabled) {
  background-color: var(--yellow-bright);
}

.save-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Success message */
.success-message {
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

/* Action buttons */
.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.log-another-button,
.close-modal-button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.log-another-button {
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
}

.log-another-button:hover {
  background-color: var(--yellow-bright);
}

.close-modal-button {
  background-color: var(--gray-cool);
  color: var(--white-off);
}

.close-modal-button:hover {
  background-color: var(--gray-dark);
}

/* Mobile Responsiveness */
@media (max-width: 640px) {
  .modal-overlay {
    padding: 0.5rem;
  }

  .modal-container {
    border-radius: 0.75rem;
    max-height: 95vh;
  }

  .modal-header {
    padding: 1rem 1rem 0.75rem;
  }

  .modal-title {
    font-size: 1.25rem;
  }

  .modal-content {
    padding: 0.75rem 1rem 1rem;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
