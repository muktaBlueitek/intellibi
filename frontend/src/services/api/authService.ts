import apiClient from './client'

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    // OAuth2PasswordRequestForm expects form-urlencoded data
    const params = new URLSearchParams()
    params.append('username', credentials.username)
    params.append('password', credentials.password)
    
    const response = await apiClient.post('/auth/login', params.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  register: async (data: RegisterData): Promise<void> => {
    await apiClient.post('/auth/register', data)
  },

  logout: async (): Promise<void> => {
    // Token is removed in the auth slice
  },
}
