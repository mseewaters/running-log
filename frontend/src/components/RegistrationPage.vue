<template>
  <div data-testid="registration-container" class="landing-container">

    <!-- Logo Section (same as LandingPage) -->
    <div class="logo-section">
      <div data-testid="logo-circle" class="logo-container">
        <img
          data-testid="runner-icon"
          :src="runnerImage"
          alt="Runner icon"
          class="runner-icon"
        />
      </div>

      <h1 data-testid="app-title" class="app-title">
        FINISH LINES
      </h1>

      <p data-testid="tagline" class="tagline">
        Create your account
      </p>
    </div>

    <!-- Registration Card -->
    <div data-testid="registration-card" class="login-card">
      <!-- General error message -->
      <div v-if="errors.general" data-testid="general-error" class="error-message general-error">
        {{ errors.general }}
      </div>

      <form data-testid="registration-form" @submit.prevent="handleRegistration">

        <!-- First Name Input -->
        <div class="form-group">
          <label class="form-label">First Name</label>
          <input
            data-testid="first-name-input"
            type="text"
            placeholder="John"
            class="form-input"
            v-model="firstName"
          />
          <div v-if="errors.firstName" data-testid="first-name-error" class="error-message">
            {{ errors.firstName }}
          </div>
        </div>

        <!-- Last Name Input -->
        <div class="form-group">
          <label class="form-label">Last Name</label>
          <input
            data-testid="last-name-input"
            type="text"
            placeholder="Doe"
            class="form-input"
            v-model="lastName"
          />
          <div v-if="errors.lastName" data-testid="last-name-error" class="error-message">
            {{ errors.lastName }}
          </div>
        </div>

        <!-- Email Input -->
        <div class="form-group">
          <label class="form-label">Email</label>
          <input
            data-testid="email-input"
            type="email"
            placeholder="john@example.com"
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
            placeholder="Password"
            class="form-input"
            v-model="password"
          />
          <div v-if="errors.password" data-testid="password-error" class="error-message">
            {{ errors.password }}
          </div>
        </div>

        <!-- Confirm Password Input -->
        <div class="form-group">
          <label class="form-label">Confirm Password</label>
          <input
            data-testid="confirm-password-input"
            type="password"
            placeholder="Confirm Password"
            class="form-input"
            v-model="confirmPassword"
          />
          <div v-if="errors.confirmPassword" data-testid="confirm-password-error" class="error-message">
            {{ errors.confirmPassword }}
          </div>
        </div>

        <!-- Register Button -->
        <button
          data-testid="register-button"
          type="submit"
          class="login-button"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <!-- Login Link -->
      <div class="text-center mt-4">
        <span class="register-text">Already have an account? </span>
        <a data-testid="login-link" href="#" @click.prevent="goToLogin" class="register-link">
          Sign In
        </a>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/services/api'

// Import the image (same as LandingPage)
import runnerImage from '@/assets/runner.png'

const router = useRouter()

// Reactive state
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const errors = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  general: ''
})

// Form validation
const validateForm = () => {
  errors.value = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    general: ''
  }

  // Required field validation
  if (!firstName.value.trim()) {
    errors.value.firstName = 'First name is required'
  }

  if (!lastName.value.trim()) {
    errors.value.lastName = 'Last name is required'
  }

  if (!email.value.trim()) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.value.email = 'Please enter a valid email address'
  }

  if (!password.value) {
    errors.value.password = 'Password is required'
  } else if (password.value.length < 8) {
    errors.value.password = 'Password must be at least 8 characters'
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password.value)) {
    errors.value.password = 'Password must contain uppercase, lowercase, and number'
  }

  if (!confirmPassword.value) {
    errors.value.confirmPassword = 'Please confirm your password'
  } else if (password.value !== confirmPassword.value) {
    errors.value.confirmPassword = 'Passwords do not match'
  }

  // Return true if no errors
  return !Object.values(errors.value).some(error => error !== '')
}

// Handle registration submission
const handleRegistration = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errors.value.general = ''

  try {
    // Call real backend API
    const response = await authApi.register({
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
      email: email.value.trim(),
      password: password.value
    })

    console.log('Registration successful:', response)

    // Store the JWT token in localStorage
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('user_email', response.email)
    localStorage.setItem('user_id', response.user_id)

    // Redirect to home page
    router.push('/home')

  } catch (error: any) {
    console.error('Registration failed:', error)

    // Handle different error types
    if (error.response?.status === 400) {
      errors.value.general = error.response.data?.detail || 'Registration failed'
    } else if (error.response?.status === 409) {
      errors.value.general = 'An account with this email already exists'
    } else if (error.response?.status >= 500) {
      errors.value.general = 'Server error. Please try again later.'
    } else {
      errors.value.general = 'Registration failed. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

// Navigate to login page
const goToLogin = () => {
  router.push('/')
}
</script>

<style scoped>
/* Registration page styles using project CSS variables */

.landing-container {
  min-height: 100vh;
  padding: var(--spacing-lg);
  background-color: var(--charcoal-dark);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.logo-section {
  text-align: center;
  margin-bottom: var(--spacing-3xl);
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.0rem;
}

.runner-icon {
  width: 15rem;
  height: 12rem;
  object-fit: contain;
}

.app-title {
  color: var(--yellow-safety);
  font-size: var(--font-size-5xl);
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-bottom: 0.2rem;
}

.tagline {
  color: var(--yellow-safety);
  font-size: var(--font-size-lg);
  font-weight: 500;
  font-style: italic;
  text-align: center;
}

.login-card {
  width: 100%;
  max-width: 24rem;
  background-color: var(--charcoal-medium);
  border-radius: var(--radius-lg);
  border: 1px solid var(--gray-cool);
  padding: var(--spacing-xl);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-label {
  color: var(--white-off);
  font-size: var(--font-size-base);
  font-weight: 500;
  display: block;
  margin-bottom: var(--spacing-sm);
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: var(--white-off);
  border: none;
  border-radius: var(--radius-md);
  color: var(--charcoal-dark);
  font-size: var(--font-size-base);
  min-height: var(--touch-target);
}

.form-input::placeholder {
  color: var(--gray-placeholder);
}

.form-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--yellow-safety);
}

.login-button {
  width: 100%;
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: var(--font-size-lg);
  margin-top: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
  min-height: var(--touch-target);
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-button:hover:not(:disabled) {
  background-color: #d4e600;
  transform: translateY(-1px);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.text-center {
  text-align: center;
}

.mt-4 {
  margin-top: 0.2rem;
}

.register-text {
  color: var(--white-off);
  font-size: var(--font-size-sm);
  padding-right: var(--spacing-sm);
}

.register-link {
  color: var(--blue-cyan);
  text-decoration: none;
  font-weight: 500;
  font-size: var(--font-size-sm);
}

.register-link:hover {
  text-decoration: underline;
}

.error-message {
  color: var(--red-alert);
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
  font-weight: 500;
}

.general-error {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-sm);
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm);
  text-align: center;
}
</style>
