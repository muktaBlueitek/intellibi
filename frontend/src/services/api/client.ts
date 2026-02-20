import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    // Normalize error message for consistent handling
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      error.message = Array.isArray(detail)
        ? detail.map((e: { msg?: string }) => e.msg || JSON.stringify(e)).join(', ')
        : typeof detail === 'string'
          ? detail
          : error.message
    }
    return Promise.reject(error)
  }
)

export default apiClient
