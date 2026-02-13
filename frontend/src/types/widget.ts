export type WidgetType = 
  | 'line_chart'
  | 'bar_chart'
  | 'pie_chart'
  | 'area_chart'
  | 'table'
  | 'heatmap'
  | 'metric'
  | 'text'

export interface Widget {
  id: number
  name: string
  type: WidgetType
  description?: string
  config?: Record<string, any>
  query?: string
  datasource_id?: number
  position_x: number
  position_y: number
  width: number
  height: number
  dashboard_id: number
  created_at: string
  updated_at?: string
}

export interface WidgetCreate {
  name: string
  type: WidgetType
  description?: string
  config?: Record<string, any>
  query?: string
  datasource_id?: number
  position_x?: number
  position_y?: number
  width?: number
  height?: number
}

export interface WidgetUpdate {
  name?: string
  description?: string
  config?: Record<string, any>
  query?: string
  datasource_id?: number
  position_x?: number
  position_y?: number
  width?: number
  height?: number
}

export interface LayoutItem {
  i: string // widget id as string
  x: number
  y: number
  w: number
  h: number
  minW?: number
  minH?: number
  maxW?: number
  maxH?: number
}
