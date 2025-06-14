// src/services/api.ts
import axios from 'axios'

// API configuration - Your deployed AWS API Gateway URL
const API_BASE_URL = 'https://wu63s38laa.execute-api.us-east-1.amazonaws.com/Prod'
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
}

export default api
