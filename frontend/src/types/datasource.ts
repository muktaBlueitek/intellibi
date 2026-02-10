export type DataSourceType = 'file' | 'postgresql' | 'mysql' | 'mongodb' | 'rest_api'

export interface DataSource {
  id: number
  name: string
  description?: string
  type: DataSourceType
  connection_config?: Record<string, any>
  file_path?: string
  file_name?: string
  host?: string
  port?: number
  database_name?: string
  username?: string
  api_url?: string
  is_active: boolean
  owner_id: number
  created_at: string
  updated_at?: string
}

export interface DataSourceCreate {
  name: string
  description?: string
  type: DataSourceType
  connection_config?: Record<string, any>
  file_path?: string
  host?: string
  port?: number
  database_name?: string
  username?: string
  api_url?: string
}
