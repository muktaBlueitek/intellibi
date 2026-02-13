import apiClient from './client'
import { Widget, WidgetCreate, WidgetUpdate } from '../../types/widget'

export const widgetService = {
  getWidgets: async (dashboardId: number): Promise<Widget[]> => {
    const response = await apiClient.get(`/widgets/dashboard/${dashboardId}`)
    return response.data
  },

  getWidget: async (id: number): Promise<Widget> => {
    const response = await apiClient.get(`/widgets/${id}`)
    return response.data
  },

  createWidget: async (data: WidgetCreate): Promise<Widget> => {
    const response = await apiClient.post('/widgets', data)
    return response.data
  },

  updateWidget: async (id: number, data: WidgetUpdate): Promise<Widget> => {
    const response = await apiClient.put(`/widgets/${id}`, data)
    return response.data
  },

  deleteWidget: async (id: number): Promise<void> => {
    await apiClient.delete(`/widgets/${id}`)
  },
}
