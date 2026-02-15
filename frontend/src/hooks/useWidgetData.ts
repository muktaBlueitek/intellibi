import { useState, useEffect, useCallback } from 'react'
import { Widget } from '../types/widget'
import { ChartData, ChartResponse } from '../types/chart'
import { analyticsService, QueryRequest } from '../services/api/analyticsService'

interface UseWidgetDataOptions {
  autoRefresh?: boolean
  refreshInterval?: number // in milliseconds
}

export const useWidgetData = (
  widget: Widget | null,
  options: UseWidgetDataOptions = {}
) => {
  const { autoRefresh = false, refreshInterval = 30000 } = options

  const [data, setData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [columns, setColumns] = useState<string[]>([])

  const fetchData = useCallback(async () => {
    if (!widget || !widget.query || !widget.datasource_id) {
      setData([])
      setColumns([])
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Parse widget query - could be SQL or JSON query config
      let response: ChartResponse

      // Try to parse as JSON query config first
      try {
        const queryConfig = JSON.parse(widget.query) as QueryRequest
        response = await analyticsService.executeQuery({
          ...queryConfig,
          datasource_id: widget.datasource_id,
        })
      } catch {
        // If not JSON, treat as SQL query
        response = await analyticsService.executeSQL({
          datasource_id: widget.datasource_id,
          query: widget.query,
        })
      }

      if (response.success) {
        setData(response.data)
        setColumns(response.columns)
      } else {
        setError('Failed to fetch data')
        setData([])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch widget data')
      setData([])
      setColumns([])
    } finally {
      setLoading(false)
    }
  }, [widget])

  useEffect(() => {
    fetchData()

    let intervalId: NodeJS.Timeout | null = null
    if (autoRefresh) {
      intervalId = setInterval(fetchData, refreshInterval)
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [fetchData, autoRefresh, refreshInterval])

  return {
    data,
    columns,
    loading,
    error,
    refetch: fetchData,
  }
}
