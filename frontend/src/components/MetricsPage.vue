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

    <!-- Navigation -->
    <BottomNavigation />

    <!-- Main content -->
    <main class="main-content">
      <section class="metrics-section">
        <h2 class="section-title">Metrics</h2>

        <!-- Coming Soon Placeholder -->
        <div class="metrics-placeholder">
          <div class="placeholder-icon">📊</div>
          <h3 class="placeholder-title">Advanced Analytics Coming Soon!</h3>
          <div class="placeholder-content">
            <p>We're building powerful insights for your running journey:</p>
            <ul class="feature-list">
              <li>📈 <strong>Performance Trends</strong> - Track your pace improvements over time</li>
              <li>🎯 <strong>Goal Analytics</strong> - Detailed progress breakdowns and predictions</li>
              <li>📅 <strong>Training Patterns</strong> - Discover your optimal running schedule</li>
              <li>🏃‍♂️ <strong>Personal Records</strong> - Celebrate your achievements and milestones</li>
              <li>📊 <strong>Data Visualizations</strong> - Beautiful charts and graphs</li>
            </ul>
            <p class="placeholder-note">
              Your run data is already being collected and will power these insights when they launch!
            </p>
          </div>

          <!-- Call to Action -->
          <div class="cta-section">
            <p class="cta-text">Keep logging runs to unlock these features:</p>
            <router-link to="/run" class="cta-button">
              Log a Run
            </router-link>
          </div>
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

/* Header styles matching HomePage */
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

/* Metrics placeholder styles */
.metrics-section {
  margin-bottom: 2rem;
}

.metrics-placeholder {
  background-color: var(--charcoal-medium);
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  border: 1px solid var(--gray-cool);
  max-width: 600px;
  margin: 0 auto;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.placeholder-title {
  color: var(--yellow-safety);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.placeholder-content {
  text-align: left;
  margin-bottom: 2rem;
}

.placeholder-content p {
  color: var(--white-off);
  margin-bottom: 1rem;
  line-height: 1.6;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
}

.feature-list li {
  color: var(--white-off);
  margin-bottom: 0.75rem;
  padding-left: 0;
  line-height: 1.5;
}

.feature-list strong {
  color: var(--yellow-safety);
}

.placeholder-note {
  background-color: var(--charcoal-dark);
  padding: 1rem;
  border-radius: 0.5rem;
  border-left: 4px solid var(--blue-cyan);
  margin-top: 1.5rem;
  font-style: italic;
  color: var(--gray-cool);
}

/* Call to action section */
.cta-section {
  border-top: 1px solid var(--gray-cool);
  padding-top: 1.5rem;
  margin-top: 1.5rem;
}

.cta-text {
  color: var(--white-off);
  margin-bottom: 1rem;
  font-size: 1rem;
}

.cta-button {
  display: inline-block;
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  transition: background-color 0.2s ease;
}

.cta-button:hover {
  background-color: rgba(255, 193, 7, 0.9);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .metrics-placeholder {
    padding: 1.5rem;
    margin: 0 0.5rem;
  }

  .placeholder-title {
    font-size: 1.25rem;
  }

  .placeholder-icon {
    font-size: 2.5rem;
  }
}
</style>
