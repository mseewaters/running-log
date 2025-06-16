<template>
  <div
    v-if="isOpen"
    data-testid="modal-overlay"
    class="modal-overlay"
  >
    <div class="modal-content">
      <h3 data-testid="modal-title" class="text-xl font-semibold mb-4">
        {{ existingTarget ? 'Edit' : 'Set' }} {{ displayName }} Target
      </h3>

      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Target Distance (km)</label>
        <input
          data-testid="distance-input"
          v-model="inputValue"
          type="number"
          min="0"
          max="500"
          step="0.1"
          class="distance-input"
          placeholder="Enter distance"
        />
        <div v-if="validationError" data-testid="validation-error" class="validation-error">
          {{ validationError }}
        </div>
      </div>

      <div class="button-container">
        <div class="left-buttons">
          <button
            v-if="existingTarget"
            data-testid="delete-button"
            @click="handleDelete"
            class="delete-button"
          >
            Delete
          </button>
        </div>

        <div class="right-buttons">
          <button
            data-testid="cancel-button"
            @click="handleCancel"
            class="cancel-button"
          >
            Cancel
          </button>
          <button
            data-testid="save-button"
            @click="handleSave"
            class="save-button"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { targetApi, type TargetResponse } from '@/services/api'

// Props
interface Props {
  isOpen: boolean
  monthKey: string
  displayName: string  // Changed from monthName to displayName
  existingTarget: TargetResponse | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  success: []
}>()

// State
const inputValue = ref('')
const validationError = ref('')

// Computed: Determine if this is a yearly target
const isYearlyTarget = computed(() => {
  // If monthKey is just a year (4 digits), it's yearly
  return /^\d{4}$/.test(props.monthKey)
})

// Computed: Target type for API calls
const targetType = computed(() => {
  return isYearlyTarget.value ? 'yearly' : 'monthly'
})

// Watch for existing target changes to populate input
watch(() => props.existingTarget, (newTarget) => {
  if (newTarget) {
    inputValue.value = newTarget.distance_km.toString()
  } else {
    inputValue.value = ''
  }
}, { immediate: true })

// Validation
const validateInput = (): boolean => {
  validationError.value = ''

  const value = parseFloat(inputValue.value)

  if (!inputValue.value || isNaN(value)) {
    validationError.value = 'Please enter a valid distance'
    return false
  }

  if (value <= 0) {
    validationError.value = 'Distance must be greater than 0'
    return false
  }

  return true
}

// Handlers
const handleCancel = () => {
  inputValue.value = ''
  validationError.value = ''
  emit('close')
}

const handleSave = async () => {
  if (!validateInput()) {
    return
  }

  const distance = parseFloat(inputValue.value)

  try {
    if (props.existingTarget) {
      // Update existing target
      await targetApi.updateTarget(props.existingTarget.target_id, {
        target_type: targetType.value,  // Use computed target type
        period: props.monthKey,
        distance_km: distance
      })
    } else {
      // Create new target
      await targetApi.createTarget({
        target_type: targetType.value,  // Use computed target type
        period: props.monthKey,
        distance_km: distance
      })
    }

    // Clear form and emit success
    inputValue.value = ''
    validationError.value = ''
    emit('success')

  } catch (error) {
    console.error('Failed to save target:', error)
    validationError.value = 'Failed to save target. Please try again.'
  }
}

const handleDelete = async () => {
  if (!props.existingTarget) {
    return
  }

  try {
    await targetApi.deleteTarget(props.existingTarget.target_id)
    emit('success')
  } catch (error) {
    console.error('Failed to delete target:', error)
    validationError.value = 'Failed to delete target. Please try again.'
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background-color: var(--charcoal-medium);
  padding: 2rem;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 400px;
  border: 1px solid var(--gray-cool);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  color: var(--white-off);
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-content label {
  color: var(--white-off);
  font-weight: 500;
}

.distance-input {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--charcoal-dark);
  border: 2px solid var(--gray-cool);
  border-radius: 0.5rem;
  color: var(--white-off);
  font-size: 1rem;
}

.distance-input:focus {
  outline: none;
  border-color: var(--yellow-safety);
  box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.1);
}

.distance-input::placeholder {
  color: var(--gray-cool);
}

.validation-error {
  color: var(--red-alert);
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

.button-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
}

.left-buttons {
  flex: 1;
}

.right-buttons {
  display: flex;
  gap: 0.75rem;
}

.delete-button {
  background-color: var(--red-alert);
  color: white;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-button:hover {
  background-color: #dc2626;
  transform: translateY(-1px);
}

.cancel-button {
  background-color: var(--charcoal-dark);
  color: var(--white-off);
  padding: 0.75rem 1rem;
  border: 2px solid var(--gray-cool);
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button:hover {
  background-color: var(--gray-cool);
  transform: translateY(-1px);
}

.save-button {
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.save-button:hover {
  background-color: #eab308;
  transform: translateY(-1px);
}
</style>
