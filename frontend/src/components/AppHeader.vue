<template>
  <header class="app-header">
    <div class="header-content">
      <h1 class="app-title">FINISH LINES</h1>
      <img
        src="@/assets/runner_noline.png"
        alt="Runner - Click to log a run"
        class="runner-icon-small runner-icon-clickable"
        @click="openQuickLogModal"
        title="Log a Run"
      />
    </div>
  </header>

  <!-- Quick Log Modal -->
  <QuickLogModal
    :isOpen="showQuickLogModal"
    @close="closeQuickLogModal"
    @runSaved="onRunSaved"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import QuickLogModal from './QuickLogModal.vue'

// Define emits for parent component to react to run updates
const emit = defineEmits<{
  runSaved: []
}>()

// Modal state
const showQuickLogModal = ref(false)

// Quick Log Modal functions
const openQuickLogModal = () => {
  showQuickLogModal.value = true
}

const closeQuickLogModal = () => {
  showQuickLogModal.value = false
}

const onRunSaved = () => {
  closeQuickLogModal()
  // Emit event so parent component can reload data if needed
  emit('runSaved')
}
</script>

<style scoped>
/* Header styles matching your app design */
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

.runner-icon-clickable {
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.runner-icon-clickable:hover {
  transform: scale(1.1);
  opacity: 0.8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .app-title {
    font-size: 1.5rem;
  }
}
</style>