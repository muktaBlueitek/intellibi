export interface Dashboard {
  id: number
  name: string
  description?: string
  layout_config?: Record<string, any>
  owner_id: number
  version: number
  created_at: string
  updated_at?: string
}

export interface DashboardCreate {
  name: string
  description?: string
  layout_config?: Record<string, any>
}

export interface DashboardUpdate {
  name?: string
  description?: string
  layout_config?: Record<string, any>
}
