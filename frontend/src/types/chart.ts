export interface ChartData {
  [key: string]: string | number | Date | null
}

export interface ChartConfig {
  // Common chart configuration
  title?: string
  xAxisKey?: string
  yAxisKey?: string
  dataKey?: string
  colors?: string[]
  showLegend?: boolean
  showGrid?: boolean
  showTooltip?: boolean
  
  // Line/Area chart specific
  strokeWidth?: number
  dot?: boolean
  
  // Bar chart specific
  barSize?: number
  layout?: 'horizontal' | 'vertical'
  
  // Pie chart specific
  innerRadius?: number
  outerRadius?: number
  labelKey?: string
  valueKey?: string
  
  // Responsive
  responsive?: boolean
}

export interface ChartResponse {
  success: boolean
  columns: string[]
  data: ChartData[]
  row_count: number
  total_rows: number
}
