// src/services/api.ts
import axios from 'axios'

// Environment-based API URL configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://wu63s38laa.execute-api.us-east-1.amazonaws.com/Prod'
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || 'production'

console.log(`🚀 API Service running in ${ENVIRONMENT} mode`)
console.log(`📡 API Base URL: ${API_BASE_URL}`)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('Adding Authorization header:', `Bearer ${token.substring(0, 20)}...`)
    } else {
      console.log('No JWT token found in localStorage')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle JWT expiration
api.interceptors.response.use(
  (response) => {
    // Return successful responses unchanged
    return response
  },
  (error) => {
    // Handle 401 Unauthorized errors (expired/invalid JWT)
    if (error.response?.status === 401) {
      console.log('JWT token expired or invalid, logging out user')

      // Clear all auth data from localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_email')
      localStorage.removeItem('user_id')

      // Redirect to landing page
      window.location.href = '/'

      // Optional: Show a toast/notification
      console.log('Session expired. Please log in again.')
    }

    // Re-throw the error for handling by the calling code
    return Promise.reject(error)
  }
)

// Types for API requests/responses
export interface RunRequest {
  date: string         // YYYY-MM-DD format
  distance_km: number  // Distance in km
  duration: string     // HH:MM:SS format
  notes?: string       // Optional notes
}

export interface RunResponse {
  run_id: string
  date: string
  distance_km: number
  duration: string
  pace: string
  notes: string
}

export interface AuthRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user_id: string
  email: string
}

export interface TargetRequest {
  target_type: 'monthly' | 'yearly'
  period: string         // YYYY-MM for monthly, YYYY for yearly
  distance_km: number    // Target distance in km
}

export interface TargetResponse {
  target_id: string
  user_id: string
  target_type: 'monthly' | 'yearly'
  period: string
  period_display: string // Human readable: "June 2025" or "2025"
  distance_km: number
  created_at: string
}

// API functions
export const runApi = {
  // Create a new run
  createRun: async (runData: RunRequest): Promise<RunResponse> => {
    const response = await api.post('/runs', runData)
    return response.data
  },

  // Get all runs for the user
  getRuns: async (): Promise<RunResponse[]> => {
    const response = await api.get('/runs')
    return response.data
  },

  // Update an existing run
  updateRun: async (runId: string, runData: RunRequest): Promise<RunResponse> => {
    const response = await api.put(`/runs/${runId}`, runData)
    return response.data
  },

  // Delete a run
  deleteRun: async (runId: string): Promise<void> => {
    await api.delete(`/runs/${runId}`)
  },
}

export const authApi = {
  // Login user
  login: async (credentials: AuthRequest): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },

  // Register user
  register: async (userData: AuthRequest & { first_name: string; last_name: string }): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
}

export const targetApi = {
  // Create a new target
  createTarget: async (targetData: TargetRequest): Promise<TargetResponse> => {
    const response = await api.post('/targets', targetData)
    return response.data
  },

  // Get all targets for the user
  getTargets: async (): Promise<TargetResponse[]> => {
    const response = await api.get('/targets')
    return response.data
  },

  // Update an existing target
  updateTarget: async (targetId: string, targetData: TargetRequest): Promise<TargetResponse> => {
    const response = await api.put(`/targets/${targetId}`, targetData)
    return response.data
  },

  // Delete a target
  deleteTarget: async (targetId: string): Promise<void> => {
    await api.delete(`/targets/${targetId}`)
  },
}

export default api
