<template>
  <nav class="bottom-navigation nav-container">
    <router-link
      to="/home"
      data-testid="nav-home"
      class="nav-item nav-item-layout"
      :class="{ active: $route.name === 'home' }"
    >
      <div class="nav-icon">
        <img src="@/assets/home.svg" alt="Home" class="nav-icon-svg" />
      </div>
      <span class="nav-label">Home</span>
    </router-link>

    <router-link
      to="/run"
      data-testid="nav-run"
      class="nav-item nav-item-layout"
      :class="{ active: $route.name === 'run' }"
    >
      <div class="nav-icon">
        <img src="@/assets/run.svg" alt="Run" class="nav-icon-svg" />
      </div>
      <span class="nav-label">Log Run</span>
    </router-link>

    <router-link
      to="/plan"
      data-testid="nav-plan"
      class="nav-item nav-item-layout"
      :class="{ active: $route.name === 'plan' }"
    >
      <div class="nav-icon">
        <img src="@/assets/plan.svg" alt="Plan" class="nav-icon-svg" />
      </div>
      <span class="nav-label">Plan</span>
    </router-link>

    <router-link
      to="/metrics"
      data-testid="nav-metrics"
      class="nav-item nav-item-layout"
      :class="{ active: $route.name === 'metrics' }"
    >
      <div class="nav-icon">
        <img src="@/assets/metrics.svg" alt="Metrics" class="nav-icon-svg" />
      </div>
      <span class="nav-label">Metrics</span>
    </router-link>
  </nav>
</template>

<style scoped>
/* Component-specific layout only */
.nav-container {
  position: static;
  display: flex;
  padding: 0.1rem 0;
}

.nav-item-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.25rem;
}

.nav-icon {
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon-svg {
  width: 20px;
  height: 20px;
  object-fit: contain;
  /* Convert black SVG to --white-off */
  filter: brightness(0) saturate(100%) invert(93%) sepia(8%) saturate(325%) hue-rotate(174deg) brightness(95%) contrast(89%);
  transition: filter 0.2s ease;
}

/* Active state - convert to --yellow-safety */
.nav-item.active .nav-icon-svg {
  filter: brightness(0) saturate(100%) invert(86%) sepia(95%) saturate(1352%) hue-rotate(1deg) brightness(119%) contrast(119%);
}

/* Hover state - slightly brighter */
.nav-item:hover .nav-icon-svg {
  filter: brightness(0) saturate(100%) invert(100%) sepia(0%) saturate(0%) hue-rotate(93deg) brightness(103%) contrast(103%);
}
</style>
