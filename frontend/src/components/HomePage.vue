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
      <section class="activity-section">
        <h2 class="section-title">Activity</h2>

        <!-- Placeholder for calendar - we'll build this later -->
        <div class="calendar-placeholder">
          <p>Calendar component coming soon...</p>
          <p>This will show your running activity for JUN 2025</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import BottomNavigation from './BottomNavigation.vue'
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
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.calendar-placeholder {
  background-color: var(--charcoal-medium);
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  border: 1px solid var(--gray-cool);
}

.calendar-placeholder p {
  margin-bottom: 0.5rem;
  color: var(--gray-cool);
}
</style>
