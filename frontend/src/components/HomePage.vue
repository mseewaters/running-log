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
      <!-- Progress Section - Now using reusable component -->
      <ProgressSection
        :isLoading="isLoading"
        :targets="targets"
        :allRuns="allRuns"
      />

      <!-- Activity Section -->
      <section class="activity-section">
        <h2 class="section-title">Activity</h2>

        <!-- RunCalendar Component -->
        <RunCalendar :runs="allRuns" />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import RunCalendar from './RunCalendar.vue'
import ProgressSection from './ProgressSection.vue'
import { runApi, targetApi, type TargetResponse, type RunResponse } from '@/services/api'

// State
const isLoading = ref(true)
const targets = ref<TargetResponse[]>([])
const allRuns = ref<RunResponse[]>([])

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
}
</style>
