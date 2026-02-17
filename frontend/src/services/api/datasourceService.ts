import apiClient from './client'
import { DataSource, DataSourceCreate, DataSourceUpdate } from '../../types/datasource'

export const datasourceService = {
  getDataSources: async (): Promise<DataSource[]> => {
    const response = await apiClient.get('/datasources')
    return response.data
  },

  getDataSource: async (id: number): Promise<DataSource> => {
    const response = await apiClient.get(`/datasources/${id}`)
    return response.data
  },

  createDataSource: async (data: DataSourceCreate): Promise<DataSource> => {
    const response = await apiClient.post('/datasources', data)
    return response.data
  },

  updateDataSource: async (id: number, data: DataSourceUpdate): Promise<DataSource> => {
    const response = await apiClient.put(`/datasources/${id}`, data)
    return response.data
  },

  deleteDataSource: async (id: number): Promise<void> => {
    await apiClient.delete(`/datasources/${id}`)
  },

  uploadFile: async (
    file: File,
    name?: string,
    description?: string,
    cleanData: boolean = true
  ): Promise<DataSource> => {
    const formData = new FormData()
    formData.append('file', file)
    if (name) formData.append('name', name)
    if (description) formData.append('description', description)
    formData.append('clean_data', String(cleanData))

    const response = await apiClient.post('/datasources/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  previewFile: async (
    file: File,
    cleanData: boolean = true,
    previewRows: number = 10
  ): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('clean_data', String(cleanData))
    formData.append('preview_rows', String(previewRows))

    const response = await apiClient.post('/upload/preview', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  testDatabaseConnection: async (connection: {
    type: string
    host: string
    port: number
    database_name: string
    username: string
    password: string
  }): Promise<{ success: boolean; message?: string }> => {
    const response = await apiClient.post('/database/test', connection)
    return response.data
  },

  createDatabaseConnection: async (
    connection: {
      type: string
      host: string
      port: number
      database_name: string
      username: string
      password: string
    },
    name: string,
    description?: string
  ): Promise<DataSource> => {
    const response = await apiClient.post('/database', {
      ...connection,
      name,
      description,
    })
    return response.data
  },
}
