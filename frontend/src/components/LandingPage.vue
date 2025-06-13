<template>
  <div data-testid="landing-container" class="landing-container">

    <!-- Logo Section -->
    <div class="logo-section">
      <!-- Runner Icon (no yellow circle) -->
      <div data-testid="logo-circle" class="logo-container">
        <img
          data-testid="runner-icon"
          :src="runnerImage"
          alt="Runner icon"
          class="runner-icon"
        />
      </div>

      <!-- App Title -->
      <h1 data-testid="app-title" class="app-title">
        FINISH LINES
      </h1>

      <!-- Tagline -->
      <p data-testid="tagline" class="tagline">
        Track your runs. Hit your goals.
      </p>
    </div>

    <!-- Rest of component stays the same -->
    <div data-testid="login-card" class="login-card">
      <form data-testid="login-form">

        <!-- Email Input -->
        <div class="form-group">
          <label class="form-label">Email</label>
          <input
            data-testid="email-input"
            type="email"
            placeholder="Value"
            class="form-input"
          />
        </div>

        <!-- Password Input -->
        <div class="form-group">
          <label class="form-label">Password</label>
          <input
            data-testid="password-input"
            type="password"
            placeholder="Value"
            class="form-input"
          />
        </div>

        <!-- Sign In Button -->
        <button
          data-testid="login-button"
          type="submit"
          class="login-button"
        >
          Sign In
        </button>
      </form>

      <!-- Forgot Password Link -->
      <div class="text-left mt-4">
        <a href="#" class="forgot-link">
          Forgot password?
        </a>
      </div>

      <!-- Register Link -->
      <div class="text-left mt-4">
        <span class="register-text">Don't have an account? </span>
        <a data-testid="register-link" href="#" class="register-link">
          Register
        </a>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
// Import the image
import runnerImage from '@/assets/runner dark.png'
</script>
