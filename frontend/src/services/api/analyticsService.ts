import apiClient from './client'
import { ChartResponse } from '../../types/chart'

export interface QueryRequest {
  datasource_id: number
  table_name?: string
  filters?: Array<{
    column: string
    operator: string
    value: any
  }>
  group_by?: string[]
  aggregations?: Record<string, string[]>
  sort_by?: Array<{
    column: string
    ascending: boolean
  }>
  limit?: number
  offset?: number
}

export interface SQLQueryRequest {
  datasource_id: number
  query: string
  password?: string
}

export const analyticsService = {
  executeQuery: async (request: QueryRequest): Promise<ChartResponse> => {
    const response = await apiClient.post('/analytics/query', request)
    return response.data
  },

  executeSQL: async (request: SQLQueryRequest): Promise<ChartResponse> => {
    const response = await apiClient.post('/analytics/sql', request)
    return response.data
  },

  processTimeSeries: async (request: {
    datasource_id: number
    time_column: string
    interval: string
    table_name?: string
    group_by?: string[]
    aggregations?: Record<string, string[]>
    filters?: Array<{
      column: string
      operator: string
      value: any
    }>
    limit?: number
  }): Promise<ChartResponse> => {
    const response = await apiClient.post('/analytics/timeseries', request)
    return response.data
  },
}
