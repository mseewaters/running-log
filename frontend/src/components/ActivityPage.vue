<!-- frontend/src/components/ActivityPage.vue -->
<template>
  <div class="page-container">
    <!-- Header matching other pages -->
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
      <h2 class="page-title">Activity</h2>

      <!-- Loading state -->
      <div v-if="isLoading" class="loading-message">
        Loading your runs...
      </div>

      <div v-else>
        <!-- RunCalendar Component -->
        <section class="calendar-section">
          <RunCalendar :runs="allRuns" />
        </section>

        <!-- Run List Section -->
        <section class="runs-section">
          <h3 class="section-title">Your Runs</h3>

          <!-- Empty state -->
          <div v-if="allRuns.length === 0" class="empty-state">
            <div class="empty-icon">🏃‍♂️</div>
            <h3 class="empty-title">No runs yet</h3>
            <p class="empty-subtitle">Start logging your runs to see them here!</p>
            <router-link to="/home" class="cta-button">
              Log Your First Run
            </router-link>
          </div>

          <!-- Runs list -->
          <div v-else class="runs-list">
            <div
              v-for="run in sortedRuns"
              :key="run.run_id"
              class="run-item"
            >
              <!-- Display mode -->
              <div v-if="editingRunId !== run.run_id" class="run-display">
                <div class="run-type-sidebar">
                  {{ getRunTypeLetter(run.run_type || 'easy') }}
                </div>
                <div class="run-content">
                  <div class="run-header">
                    <div class="run-date">{{ formatDateShort(run.date || new Date().toISOString()) }}</div>
                    <div class="run-actions">
                      <button
                        @click="startEditing(run)"
                        class="action-button edit-button"
                        title="Edit run"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                          <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                      </button>
                      <button
                        @click="confirmDelete(run)"
                        class="action-button delete-button"
                        title="Delete run"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="3,6 5,6 21,6"/>
                          <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div class="run-metrics">
                    <div class="metric-item">
                      <div class="metric-value">{{ formatDistance(run.distance_km || 0) }}</div>
                      <div class="metric-label">Kms</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-value">{{ run.pace || '--:--' }}</div>
                      <div class="metric-label">Pace</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-value">{{ formatTime(run.duration || '--:--') }}</div>
                      <div class="metric-label">Time</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Edit mode -->
              <div v-else class="run-edit">
                <div class="edit-header">
                  <h4 class="edit-title">Edit Run</h4>
                  <div class="edit-actions">
                    <button
                      @click="saveEdit()"
                      class="action-button save-button"
                      :disabled="isSaving"
                    >
                      ✅
                    </button>
                    <button
                      @click="cancelEdit()"
                      class="action-button cancel-button"
                    >
                      ❌
                    </button>
                  </div>
                </div>

                <!-- Edit form -->
                <div class="edit-form">
                  <div class="form-row">
                    <label class="form-label">Date:</label>
                    <input
                      type="date"
                      v-model="editForm.date"
                      class="form-input"
                    />
                  </div>
                  <div class="form-row">
                    <label class="form-label">Distance (km):</label>
                    <input
                      type="number"
                      step="0.01"
                      v-model="editForm.distance_km"
                      class="form-input"
                    />
                  </div>
                  <div class="form-row">
                    <label class="form-label">Duration:</label>
                    <input
                      type="text"
                      v-model="editForm.duration"
                      placeholder="MM:SS or HH:MM:SS"
                      class="form-input"
                    />
                  </div>
                  <div class="form-row">
                    <label class="form-label">Type:</label>
                    <select v-model="editForm.run_type" class="form-input">
                      <option value="easy">Recovery</option>
                      <option value="tempo">Tempo</option>
                      <option value="interval">Interval</option>
                      <option value="long">Long</option>
                    </select>
                  </div>
                </div>

                <!-- Edit errors -->
                <div v-if="editErrors" class="edit-error">
                  {{ editErrors }}
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Delete confirmation modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Delete Run</h3>
        </div>
        <div class="modal-content">
          <p>Are you sure you want to delete this run?</p>
          <div class="run-preview" v-if="runToDelete">
            <strong>{{ runToDelete.distance_km }}km</strong> in <strong>{{ runToDelete.duration }}</strong> on {{ formatDate(runToDelete.date) }}
          </div>
          <div class="modal-actions">
            <button @click="cancelDelete" class="cancel-button">Cancel</button>
            <button @click="deleteRun" class="delete-confirm-button" :disabled="isDeleting">
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import RunCalendar from './RunCalendar.vue'
import { runApi, type RunResponse } from '@/services/api'

// State
const isLoading = ref(true)
const allRuns = ref<RunResponse[]>([])
const editingRunId = ref<string | null>(null)
const isSaving = ref(false)
const showDeleteModal = ref(false)
const runToDelete = ref<RunResponse | null>(null)
const isDeleting = ref(false)
const editErrors = ref<string>('')

// Edit form data
const editForm = ref({
  date: '',
  distance_km: 0,
  duration: '',
  run_type: 'easy'
})

// Computed
const sortedRuns = computed(() => {
  return [...allRuns.value].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

// Load data when component mounts
onMounted(async () => {
  await loadRuns()
})

// Load all runs
const loadRuns = async () => {
  isLoading.value = true
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
  } finally {
    isLoading.value = false
  }
}

// Edit functionality
const startEditing = (run: RunResponse) => {
  editingRunId.value = run.run_id
  editForm.value = {
    date: run.date,
    distance_km: run.distance_km,
    duration: run.duration,
    run_type: run.run_type
  }
  editErrors.value = ''
}

const cancelEdit = () => {
  editingRunId.value = null
  editErrors.value = ''
}

const saveEdit = async () => {
  if (!editingRunId.value) return

  // Basic validation
  if (!editForm.value.date || !editForm.value.distance_km || !editForm.value.duration) {
    editErrors.value = 'All fields are required'
    return
  }

  if (editForm.value.distance_km <= 0) {
    editErrors.value = 'Distance must be greater than 0'
    return
  }

  isSaving.value = true
  editErrors.value = ''

  try {
    await runApi.updateRun(editingRunId.value, {
      date: editForm.value.date,
      distance_km: editForm.value.distance_km,
      duration: editForm.value.duration,
      run_type: editForm.value.run_type,
      notes: ''
    })

    // Refresh the runs list
    await loadRuns()
    editingRunId.value = null
  } catch (error: any) {
    console.error('Failed to update run:', error)
    editErrors.value = error.response?.data?.detail || 'Failed to update run'
  } finally {
    isSaving.value = false
  }
}

// Delete functionality
const confirmDelete = (run: RunResponse) => {
  runToDelete.value = run
  showDeleteModal.value = true
}

const cancelDelete = () => {
  runToDelete.value = null
  showDeleteModal.value = false
}

const deleteRun = async () => {
  if (!runToDelete.value) return

  isDeleting.value = true

  try {
    await runApi.deleteRun(runToDelete.value.run_id)
    await loadRuns()
    showDeleteModal.value = false
    runToDelete.value = null
  } catch (error: any) {
    console.error('Failed to delete run:', error)
    // You might want to show an error message here
  } finally {
    isDeleting.value = false
  }
}

// Helper functions
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const today = new Date()
  const diffTime = today.getTime() - date.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`

  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateShort = (dateStr: string): string => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const year = date.getFullYear().toString().slice(-2) // Get last 2 digits
  return `${month}/${day}/${year}`
}

const formatRunType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'easy': 'Recovery',
    'tempo': 'Tempo',
    'interval': 'Interval',
    'long': 'Long'
  }
  return typeMap[type] || type
}

const getRunTypeLetter = (type: string): string => {
  // Handle undefined or null type
  if (!type) return 'R' // Default to 'R' for Recovery

  const letterMap: Record<string, string> = {
    'easy': 'R',
    'tempo': 'T',
    'interval': 'I',
    'long': 'L'
  }
  return letterMap[type.toLowerCase()] || type.charAt(0).toUpperCase()
}

const formatTime = (duration: string): string => {
  if (!duration) return '--:--'

  // Check if it's already in HH:MM:SS format
  const parts = duration.split(':')
  if (parts.length === 3) {
    const hours = parseInt(parts[0])
    const minutes = parts[1]
    const seconds = parts[2]

    // If less than 1 hour, show MM:SS
    if (hours === 0) {
      return `${minutes}:${seconds}`
    }
    // Otherwise show H:MM:SS (without leading zero on hours)
    return `${hours}:${minutes}:${seconds}`
  }

  // If it's MM:SS format, return as is
  return duration
}

const formatDistance = (distance: number): string => {
  return distance ? distance.toFixed(2) : '0.00'
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
  padding-bottom: 80px;
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
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.loading-message {
  text-align: center;
  color: var(--gray-cool);
  padding: 2rem;
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-cool);
}

/* Calendar section */
.calendar-section {
  margin-bottom: 2rem;
}

/* Runs section */
.runs-section {
  margin-bottom: 2rem;
}

.section-title {
  color: var(--white-off);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  border-bottom: 2px solid var(--gray-medium);
  padding-bottom: 0.5rem;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--gray-light);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-title {
  color: var(--white-off);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.cta-button {
  display: inline-block;
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 600;
  transition: background-color 0.2s;
}

.cta-button:hover {
  background-color: var(--yellow-bright);
}

/* Runs list */
.runs-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.run-item {
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-medium);
  overflow: hidden;
}

/* Run display mode */
.run-display {
  display: flex;
  padding: 0;
  min-height: 5rem;
}

.run-type-sidebar {
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
  width: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
  border-top-left-radius: 0.75rem;
  border-bottom-left-radius: 0.75rem;
  flex-shrink: 0;
}

.run-content {
  flex: 1;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.run-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.run-date {
  color: var(--gray-light);
  font-size: 0.875rem;
  font-weight: 500;
}

.run-actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  color: var(--gray-light);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-button:hover {
  background-color: var(--gray-medium);
  color: var(--white-off);
}

.delete-button:hover {
  background-color: rgba(239, 68, 68, 0.2);
  color: var(--red-alert);
}

.run-metrics {
  display: flex;
  justify-content: space-between;
  margin-top: 0.25rem;
  padding-right: 1rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-value {
  color: var(--white-off);
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
}

.metric-label {
  color: var(--gray-light);
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Edit mode */
.run-edit {
  padding: 1rem;
  background-color: var(--charcoal-dark);
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.edit-title {
  color: var(--yellow-safety);
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
}

.save-button:hover {
  background-color: rgba(34, 197, 94, 0.2);
}

.cancel-button:hover {
  background-color: rgba(239, 68, 68, 0.2);
}

.edit-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label {
  color: var(--gray-light);
  font-size: 0.875rem;
  font-weight: 500;
}

.form-input {
  padding: 0.5rem;
  background-color: var(--white-off);
  border: none;
  border-radius: 0.25rem;
  color: var(--charcoal-dark);
  font-size: 0.875rem;
}

.edit-error {
  color: var(--red-alert);
  font-size: 0.875rem;
  padding: 0.5rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: 0.25rem;
}

/* Delete modal */
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
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid var(--gray-medium);
}

.modal-title {
  color: var(--yellow-safety);
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.modal-content {
  padding: 1rem 1.5rem 1.5rem;
}

.modal-content p {
  color: var(--white-off);
  margin-bottom: 1rem;
}

.run-preview {
  background-color: var(--charcoal-medium);
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: var(--gray-light);
}

.modal-actions {
  display: flex;
  gap: 1rem;
}

.cancel-button,
.delete-confirm-button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-button {
  background-color: var(--gray-medium);
  color: var(--white-off);
}

.cancel-button:hover {
  background-color: var(--gray-dark);
}

.delete-confirm-button {
  background-color: var(--red-alert);
  color: var(--white-off);
}

.delete-confirm-button:hover:not(:disabled) {
  background-color: #dc2626;
}

.delete-confirm-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.25rem;
  }

  .run-type-sidebar {
    width: 2.5rem;
    font-size: 1.1rem;
  }

  .run-content {
    padding: 0.5rem 0.75rem;
  }

  .run-metrics {
    gap: 1rem;
    justify-content: space-around;
    padding-right: 0;
  }

  .metric-value {
    font-size: 1.25rem;
  }

  .action-button {
    padding: 0.375rem;
  }

  .edit-form {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
