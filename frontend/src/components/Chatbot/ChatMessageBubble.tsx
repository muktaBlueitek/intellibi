import React from 'react'
import DataTable from '../Charts/DataTable'
import type { ChatMessage as ChatMessageType } from '../../types/chatbot'
import type { ChartData } from '../../types/chart'
import './ChatMessageBubble.css'

interface ChatMessageBubbleProps {
  message: ChatMessageType
}

const ChatMessageBubble: React.FC<ChatMessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user'
  const meta = message.message_metadata

  return (
    <div className={`chat-message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="chat-message-content">
        <p className="chat-message-text">{message.content}</p>

        {meta?.sql_query && (
          <div className="chat-message-sql">
            <span className="chat-message-sql-label">SQL</span>
            <pre><code>{meta.sql_query}</code></pre>
          </div>
        )}

        {meta?.query_result && (
          <div className="chat-message-result">
            {meta.query_result.success === false && meta.query_result.error && (
              <p className="chat-message-error">{meta.query_result.error}</p>
            )}
            {meta.query_result.success && meta.query_result.data && meta.query_result.data.length > 0 && (
              <div className="chat-message-table-wrap">
                <DataTable
                  data={meta.query_result.data as ChartData[]}
                  columns={meta.query_result.columns}
                  config={{
                    pageSize: 5,
                    sortable: false,
                    searchable: false,
                  }}
                />
              </div>
            )}
            {meta.query_result.success && meta.query_result.row_count === 0 && (
              <p className="chat-message-muted">Query returned no rows.</p>
            )}
          </div>
        )}

        {meta?.visualization_suggestion && (
          <div className="chat-message-viz-suggestion">
            <span className="chat-badge">Suggested chart</span>
            <span>{meta.visualization_suggestion.chart_type}</span>
            {meta.visualization_suggestion.reasoning && (
              <p className="chat-message-muted">{meta.visualization_suggestion.reasoning}</p>
            )}
          </div>
        )}

        {meta?.statistical_summary && meta.statistical_summary.length > 0 && (
          <div className="chat-message-stats">
            <span className="chat-badge">Summary</span>
            <ul>
              {meta.statistical_summary.map((s, i) => (
                <li key={i}>
                  <strong>{s.column}</strong>: count={s.count ?? '-'}
                  {s.mean != null && `, mean=${Number(s.mean).toFixed(2)}`}
                  {s.min != null && `, min=${s.min}`}
                  {s.max != null && `, max=${s.max}`}
                </li>
              ))}
            </ul>
          </div>
        )}

        {meta?.insights?.summary && (
          <div className="chat-message-insights">
            <span className="chat-badge">Insights</span>
            <p>{meta.insights.summary}</p>
            {meta.insights.trends && meta.insights.trends.length > 0 && (
              <ul>
                {meta.insights.trends.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessageBubble
