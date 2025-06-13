// src/services/authService.ts - Frontend service for authentication
import axios from 'axios'

// Your backend API URL (replace with your actual SAM deploy URL)
const API_BASE_URL = 'https://wu63s38laa.execute-api.us-east-1.amazonaws.com/Prod'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user_id: string
  email: string
}

export interface AuthError {
  message: string
  code?: string
}

class AuthService {

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: credentials.email,
        password: credentials.password
      })

      if (response.data.access_token) {
        // Store token in localStorage for future requests
        localStorage.setItem('authToken', response.data.access_token)
        localStorage.setItem('userId', response.data.user_id)
        localStorage.setItem('userEmail', response.data.email)
      }

      return response.data
    } catch (error: any) {
      console.error('Login error:', error)

      if (error.response?.status === 401) {
        throw new Error('Invalid email or password')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else {
        throw new Error('Login failed. Please try again.')
      }
    }
  }

  logout(): void {
    localStorage.removeItem('authToken')
    localStorage.removeItem('userId')
    localStorage.removeItem('userEmail')
  }

  getToken(): string | null {
    return localStorage.getItem('authToken')
  }

  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  getUserId(): string | null {
    return localStorage.getItem('userId')
  }

  getUserEmail(): string | null {
    return localStorage.getItem('userEmail')
  }
}

export const authService = new AuthService()
