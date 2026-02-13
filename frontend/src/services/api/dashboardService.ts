import apiClient from './client'
import { Dashboard, DashboardCreate, DashboardUpdate } from '../../types/dashboard'
import { LayoutItem } from '../../types/widget'

export const dashboardService = {
  getDashboards: async (): Promise<Dashboard[]> => {
    const response = await apiClient.get('/dashboards')
    return response.data
  },

  getDashboard: async (id: number): Promise<Dashboard> => {
    const response = await apiClient.get(`/dashboards/${id}`)
    return response.data
  },

  createDashboard: async (data: DashboardCreate): Promise<Dashboard> => {
    const response = await apiClient.post('/dashboards', data)
    return response.data
  },

  updateDashboard: async (id: number, data: DashboardUpdate): Promise<Dashboard> => {
    const response = await apiClient.put(`/dashboards/${id}`, data)
    return response.data
  },

  deleteDashboard: async (id: number): Promise<void> => {
    await apiClient.delete(`/dashboards/${id}`)
  },

  updateLayout: async (id: number, layoutConfig: { widgets: LayoutItem[] }): Promise<Dashboard> => {
    const response = await apiClient.put(`/dashboards/${id}/layout`, { layout_config: layoutConfig })
    return response.data
  },
}
