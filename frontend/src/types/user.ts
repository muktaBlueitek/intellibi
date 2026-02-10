export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  role: 'admin' | 'user' | 'viewer'
  created_at: string
  updated_at?: string
}
