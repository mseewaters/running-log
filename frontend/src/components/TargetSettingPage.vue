<template>
  <div class="page-container">
    <!-- Header matching HomePage and QuickLogPage -->
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
      <h2 data-testid="page-title" class="page-title">Set Target</h2>

      <!-- Target Setting Form -->
      <form
        data-testid="target-setting-form"
        @submit.prevent="handleTargetCreation"
        class="target-setting-form"
      >
        <!-- General error message -->
        <div v-if="errors.general" data-testid="general-error" class="error-message general-error">
          {{ errors.general }}
        </div>

        <!-- Target Type Selection -->
        <div class="form-group">
          <label class="form-label">Target Type:</label>
          <select
            data-testid="target-type-select"
            class="form-input form-select"
            v-model="targetType"
          >
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>

        <!-- Period Input -->
        <div class="form-group">
          <label class="form-label">Period:</label>
          <input
            data-testid="period-input"
            type="text"
            :placeholder="targetType === 'monthly' ? 'YYYY-MM (e.g., 2025-06)' : 'YYYY (e.g., 2025)'"
            class="form-input"
            :class="{ 'input-error': errors.period }"
            v-model="period"
          />
          <div v-if="errors.period" data-testid="period-error" class="error-message">
            {{ errors.period }}
          </div>
        </div>

        <!-- Distance Input -->
        <div class="form-group">
          <label class="form-label">Target Distance:</label>
          <div class="input-with-suffix">
            <input
              data-testid="distance-input"
              type="number"
              step="0.1"
              min="0"
              placeholder="100"
              class="form-input distance-input"
              :class="{ 'input-error': errors.distance }"
              v-model.number="distanceKm"
            />
            <span class="input-suffix">km</span>
          </div>
          <div v-if="errors.distance" data-testid="distance-error" class="error-message">
            {{ errors.distance }}
          </div>
        </div>

        <!-- Create Target Button -->
        <button
          data-testid="create-target-button"
          type="submit"
          class="save-button"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Creating Target...' : 'Create Target' }}
        </button>
      </form>

      <!-- Existing Targets Section -->
      <section data-testid="targets-section" class="targets-section">
        <h3 class="section-title">Current Targets</h3>

        <div v-if="isLoadingTargets" class="loading-message">
          Loading targets...
        </div>

        <div v-else-if="!targets || targets.length === 0" data-testid="no-targets-message" class="no-targets">
          No targets set yet. Create your first target above!
        </div>

        <div v-else data-testid="targets-table" class="targets-table">
          <!-- Yearly Target -->
          <div v-for="yearlyTarget in yearlyTargets" :key="yearlyTarget.target_id"
               :data-testid="`target-row-yearly-${yearlyTarget.period}`"
               class="target-row">
            <span class="target-period">{{ yearlyTarget.period }}</span>
            <span class="target-distance">{{ yearlyTarget.distance_km }}km</span>
          </div>

          <!-- Monthly Targets for Current Year -->
          <div v-for="month in monthsInCurrentYear" :key="month.key"
               :data-testid="`target-row-monthly-${month.key}`"
               class="target-row">
            <span class="target-period">{{ month.display }}</span>
            <span class="target-distance">
              <span v-if="month.target">{{ month.target.distance_km }}km</span>
              <span v-else class="no-target">Not set</span>
            </span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { targetApi, type TargetResponse } from '@/services/api'
import BottomNavigation from './BottomNavigation.vue'

const router = useRouter()

// Reactive state
const targetType = ref<'monthly' | 'yearly'>('monthly')
const period = ref('')
const distanceKm = ref<number | null>(null)
const isLoading = ref(false)
const isLoadingTargets = ref(false)
const targets = ref<TargetResponse[]>([])
const errors = ref({
  period: '',
  distance: '',
  general: ''
})

// Get current year
const currentYear = new Date().getFullYear()

// Computed: Yearly targets
const yearlyTargets = computed(() => {
  return targets.value?.filter(target => target.target_type === 'yearly') || []
})

// Computed: Months in current year with targets
const monthsInCurrentYear = computed(() => {
  const months = [
    { key: `${currentYear}-01`, display: 'January', month: 1 },
    { key: `${currentYear}-02`, display: 'February', month: 2 },
    { key: `${currentYear}-03`, display: 'March', month: 3 },
    { key: `${currentYear}-04`, display: 'April', month: 4 },
    { key: `${currentYear}-05`, display: 'May', month: 5 },
    { key: `${currentYear}-06`, display: 'June', month: 6 },
    { key: `${currentYear}-07`, display: 'July', month: 7 },
    { key: `${currentYear}-08`, display: 'August', month: 8 },
    { key: `${currentYear}-09`, display: 'September', month: 9 },
    { key: `${currentYear}-10`, display: 'October', month: 10 },
    { key: `${currentYear}-11`, display: 'November', month: 11 },
    { key: `${currentYear}-12`, display: 'December', month: 12 }
  ]

  return months.map(month => {
    const target = targets.value?.find(t =>
      t.target_type === 'monthly' && t.period === month.key
    )
    return { ...month, target }
  })
})

// Load targets on component mount
onMounted(async () => {
  await loadTargets()
})

// Load targets from API
const loadTargets = async () => {
  isLoadingTargets.value = true
  try {
    targets.value = await targetApi.getTargets()
  } catch (error) {
    console.error('Failed to load targets:', error)
  } finally {
    isLoadingTargets.value = false
  }
}

// Form validation
const validateForm = () => {
  errors.value = {
    period: '',
    distance: '',
    general: ''
  }

  // Period validation
  if (!period.value.trim()) {
    errors.value.period = 'Period is required'
  } else if (targetType.value === 'monthly') {
    // Validate YYYY-MM format
    if (!/^\d{4}-\d{2}$/.test(period.value)) {
      errors.value.period = 'Invalid format. Use YYYY-MM (e.g., 2025-06)'
    } else {
      const [year, month] = period.value.split('-')
      if (parseInt(month) < 1 || parseInt(month) > 12) {
        errors.value.period = 'Invalid month. Must be 01-12'
      }
    }
  } else if (targetType.value === 'yearly') {
    // Validate YYYY format
    if (!/^\d{4}$/.test(period.value)) {
      errors.value.period = 'Invalid format. Use YYYY (e.g., 2025)'
    }
  }

  // Distance validation
  if (!distanceKm.value || distanceKm.value <= 0) {
    errors.value.distance = 'Distance must be greater than 0'
  }

  // Return true if no errors
  return !Object.values(errors.value).some(error => error !== '')
}

// Handle target creation submission
const handleTargetCreation = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errors.value.general = ''

  try {
    // Call target API
    const response = await targetApi.createTarget({
      target_type: targetType.value,
      period: period.value.trim(),
      distance_km: distanceKm.value!
    })

    console.log('Target created successfully:', response)

    // Reload targets to show the new one
    await loadTargets()

    // Clear form
    period.value = ''
    distanceKm.value = null

  } catch (error: any) {
    console.error('Target creation failed:', error)

    // Handle different error types
    if (error.response?.status === 400) {
      errors.value.general = error.response.data?.detail || 'Target creation failed'
    } else if (error.response?.status === 409) {
      errors.value.general = 'A target for this period already exists'
    } else if (error.response?.status === 422) {
      errors.value.general = 'Please check your inputs.'
    } else if (error.response?.status >= 500) {
      errors.value.general = 'Server error. Please try again later.'
    } else {
      errors.value.general = error.response?.data?.detail || 'Target creation failed. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
}

/* Reuse header styles from HomePage and QuickLogPage */
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

.target-setting-form {
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

/* Targets Section Styles */
.targets-section {
  margin-top: 2rem;
  max-width: 400px;
}

.section-title {
  color: var(--white-off);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.loading-message {
  text-align: center;
  color: var(--gray-cool);
  padding: 1rem;
}

.no-targets {
  text-align: center;
  color: var(--gray-cool);
  padding: 1.5rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.5rem;
  border: 1px solid var(--gray-cool);
}

.targets-table {
  background-color: var(--charcoal-medium);
  border-radius: 0.5rem;
  border: 1px solid var(--gray-cool);
  overflow: hidden;
}

.target-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--gray-cool);
}

.target-row:last-child {
  border-bottom: none;
}

.target-period {
  color: var(--white-off);
  font-weight: 500;
  font-size: 0.95rem;
}

.target-distance {
  color: var(--yellow-safety);
  font-weight: 600;
  font-size: 1rem;
}

.no-target {
  color: var(--gray-cool);
  font-style: italic;
  font-weight: normal;
}
</style>
