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
        Track your runs. Hit your goals
      </p>
    </div>

    <!-- Login Card -->
    <div data-testid="login-card" class="login-card">
      <!-- General error message -->
      <div v-if="errors.general" class="error-message general-error">
        {{ errors.general }}
      </div>

      <form data-testid="login-form" @submit.prevent="handleLogin">

        <!-- Email Input -->
        <div class="form-group">
          <label class="form-label">Email</label>
          <input
            data-testid="email-input"
            type="email"
            placeholder="Value"
            class="form-input"
            v-model="email"
          />
          <div v-if="errors.email" data-testid="email-error" class="error-message">
            {{ errors.email }}
          </div>
        </div>

        <!-- Password Input -->
        <div class="form-group">
          <label class="form-label">Password</label>
          <input
            data-testid="password-input"
            type="password"
            placeholder="Value"
            class="form-input"
            v-model="password"
          />
          <div v-if="errors.password" data-testid="password-error" class="error-message">
            {{ errors.password }}
          </div>
        </div>

        <!-- Sign In Button -->
        <button
          data-testid="login-button"
          type="submit"
          class="login-button"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Signing In...' : 'Sign In' }}
        </button>
      </form>

      <!-- Forgot Password Link -->
      <div class="text-center mt-4">
        <a href="#" class="forgot-link">
          Forgot password?
        </a>
      </div>

      <!-- Register Link -->
      <div class="text-center mt-4">
        <span class="register-text">Don't have an account? </span>
        <a data-testid="register-link" href="#" class="register-link">
          Register
        </a>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/services/api'

// Import the image
import runnerImage from '@/assets/runner.png'

const router = useRouter()

// Reactive state
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errors = ref({
  email: '',
  password: '',
  general: ''
})

// Form validation
const validateForm = () => {
  errors.value = { email: '', password: '', general: '' }

  if (!email.value) {
    errors.value.email = 'Email is required'
  }

  if (!password.value) {
    errors.value.password = 'Password is required'
  }

  return !errors.value.email && !errors.value.password
}

// Handle login submission
const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errors.value.general = ''

  try {
    // Call real backend API
    const response = await authApi.login({
      email: email.value,
      password: password.value
    })

    console.log('Login successful:', response)

    // Store the JWT token in localStorage
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('user_email', response.email)
    localStorage.setItem('user_id', response.user_id)

    // Redirect to home page
    router.push('/home')

  } catch (error: any) {
    console.error('Login failed:', error)

    // Handle different error types
    if (error.response?.status === 401) {
      errors.value.general = 'Invalid email or password'
    } else if (error.response?.status === 400) {
      errors.value.general = error.response.data?.detail || 'Invalid credentials'
    } else if (error.response?.status >= 500) {
      errors.value.general = 'Server error. Please try again later.'
    } else {
      errors.value.general = 'Login failed. Please check your credentials.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>
