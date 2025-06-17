<!-- frontend/src/components/HomePage.vue - UPDATED -->
<template>
  <div class="page-container">
    <!-- Header matching Figma -->
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
      <!-- Quick Log Button Section -->
      <section class="quick-log-section">
        <button @click="openQuickLogModal" class="log-run-button">
          <div class="button-content">
            <span class="button-text">Log Run</span>
            <img
              src="@/assets/runner.png"
              alt="Runner"
              class="button-runner-icon"
            />
          </div>
        </button>
      </section>

      <!-- Progress Section - Now using reusable component -->
      <ProgressSection
        :isLoading="isLoading"
        :targets="targets"
        :allRuns="allRuns"
      />

    </main>

    <!-- Quick Log Modal -->
    <QuickLogModal
      :isOpen="showQuickLogModal"
      @close="closeQuickLogModal"
      @runSaved="onRunSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import RunCalendar from './RunCalendar.vue'
import ProgressSection from './ProgressSection.vue'
import QuickLogModal from './QuickLogModal.vue'
import { runApi, targetApi, type TargetResponse, type RunResponse } from '@/services/api'

// State
const isLoading = ref(true)
const targets = ref<TargetResponse[]>([])
const allRuns = ref<RunResponse[]>([])
const showQuickLogModal = ref(false)

// Load data when component mounts
onMounted(async () => {
  await loadData()
})

// Load all necessary data
const loadData = async () => {
  isLoading.value = true
  try {
    // Load targets and runs in parallel
    await Promise.all([
      loadTargets(),
      loadAllRuns()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    isLoading.value = false
  }
}

// Load targets from API
const loadTargets = async () => {
  try {
    targets.value = await targetApi.getTargets()
  } catch (error) {
    console.error('Failed to load targets:', error)
  }
}

// Load all runs for progress calculation
const loadAllRuns = async () => {
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
  }
}

// Modal methods
const openQuickLogModal = () => {
  showQuickLogModal.value = true
}

const closeQuickLogModal = () => {
  showQuickLogModal.value = false
}

const onRunSaved = () => {
  // Refresh data after a run is saved
  loadData()
}
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

.section-title {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

/* Quick Log Section */
.quick-log-section {
  text-align: center;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
}

.log-run-button {
  background-color: var(--charcoal-dark);
  color: var(--yellow-safety);
  border: 1px solid var(--yellow-safety);
  border-radius: 1rem;
  padding: 0rem 0rem;
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 16px rgba(255, 193, 7, 0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0rem;
  min-width: 200px;
  margin: 0 auto;
  position: relative;
}

.log-run-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 193, 7, 0.4);
  background-color: var(--charcoal-medium);
}

.log-run-button:active {
  transform: translateY(0);
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.button-text {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--yellow-safety);
}

.button-runner-icon {
  height: auto;
  width: auto;
  object-fit: contain;
  opacity: 0.9;
  transition: opacity 0.2s;
}

.log-run-button:hover .button-runner-icon {
  opacity: 1;
}

/* Activity Section Styles */
.activity-section {
  margin-bottom: 2rem;
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

  .section-title {
    font-size: 1rem;
    margin-bottom: 0.75rem;
  }

  .log-run-button {
    padding: 0.5rem 1rem;
    font-size: 1.3rem;
    min-width: 180px;
  }

  .button-runner-icon {
    height: 2.5rem;
  }

  .button-text {
    font-size: 1.2rem;
  }
}
</style>
