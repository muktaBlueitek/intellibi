import apiClient from './client'
import { User } from '../../types/user'

export const userService = {
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/users/me')
    return response.data
  },
}
