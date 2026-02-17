export interface ChatMessage {
  id: number
  conversation_id: number
  role: string
  content: string
  message_metadata?: {
    sql_query?: string
    query_result?: ExecutionResult
    visualization_suggestion?: VisualizationSuggestion
    statistical_summary?: StatisticalSummary[]
    insights?: QueryInsights
    suggested_queries?: string[]
  }
  created_at: string
}

export interface ExecutionResult {
  success: boolean
  columns?: string[]
  data?: Record<string, unknown>[]
  row_count?: number
  total_rows?: number
  error?: string
  execution_time?: number
}

export interface VisualizationSuggestion {
  chart_type: string
  config?: Record<string, unknown>
  reasoning?: string
}

export interface StatisticalSummary {
  column: string
  mean?: number
  median?: number
  min?: number
  max?: number
  std_dev?: number
  count?: number
}

export interface QueryInsights {
  summary?: string
  trends?: string[]
  anomalies?: string[]
  correlations?: string[]
}

export interface Conversation {
  id: number
  user_id: number
  title: string | null
  created_at: string
  updated_at: string | null
  messages: ChatMessage[]
}

export interface ConversationList {
  id: number
  user_id: number
  title: string | null
  created_at: string
  updated_at: string | null
  message_count?: number
}

export interface ChatRequest {
  message: string
  conversation_id?: number | null
  datasource_id?: number | null
}

export interface ChatResponse {
  message: string
  conversation_id: number
  sql_query?: string | null
  execution_result?: ExecutionResult | null
  visualization_suggestion?: VisualizationSuggestion | null
  statistical_summary?: StatisticalSummary[] | null
  insights?: QueryInsights | null
  suggested_queries?: string[] | null
  message_id: number
}
