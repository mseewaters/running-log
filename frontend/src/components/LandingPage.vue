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
          <label class="form-label">Password:</label>
          <div class="password-input-wrapper">
            <input
              data-testid="password-input"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Enter your password"
              class="form-input"
              :class="{ 'input-error': errors.password }"
              v-model="password"
            />
            <button
              type="button"
              class="password-toggle-btn"
              @click="togglePasswordVisibility"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
            >
              <!-- Eye icon for show/hide -->
              <svg v-if="!showPassword" class="eye-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <!-- Eye-off icon for hidden -->
              <svg v-else class="eye-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <div v-if="errors.password" class="error-message">
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
        <router-link data-testid="register-link" to="/register" class="register-link">
          Register
        </router-link>
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
const showPassword = ref(false)
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

// Toggle password visibility
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
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

<style scoped>

.password-input-wrapper {
  position: relative;
  display: block;
}

.password-input-wrapper .form-input {
  padding-right: 3rem; /* Space for toggle button */
}

.password-toggle-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-placeholder);
  transition: color 0.2s ease;
  z-index: 2;
}

.eye-icon {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

.password-toggle-btn:hover {
  color: var(--charcoal-medium);
}


</style>
