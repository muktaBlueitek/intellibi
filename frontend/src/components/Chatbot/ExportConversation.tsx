import React from 'react'
import type { ChatMessage as ChatMessageType, ConversationList } from '../../types/chatbot'
import './ExportConversation.css'

interface ExportConversationProps {
  conversation: ConversationList | null
  messages: ChatMessageType[]
  onExport: (format: 'json' | 'text') => void
  disabled?: boolean
}

const ExportConversation: React.FC<ExportConversationProps> = ({
  conversation,
  messages,
  onExport,
  disabled = false,
}) => {
  if (!conversation || messages.length === 0) return null

  return (
    <div className="export-conversation">
      <button
        type="button"
        className="export-conversation-btn"
        onClick={() => onExport('text')}
        disabled={disabled}
        title="Export as text"
      >
        Export (TXT)
      </button>
      <button
        type="button"
        className="export-conversation-btn"
        onClick={() => onExport('json')}
        disabled={disabled}
        title="Export as JSON"
      >
        Export (JSON)
      </button>
    </div>
  )
}

export function exportConversationToText(
  title: string | null,
  messages: ChatMessageType[]
): string {
  const lines = [
    `IntelliBI Chat Export - ${title || 'Conversation'}`,
    `Exported: ${new Date().toISOString()}`,
    '',
    '--- Messages ---',
    '',
  ]
  messages.forEach((m) => {
    lines.push(`[${m.role.toUpperCase()}]`)
    lines.push(m.content)
    if (m.message_metadata?.sql_query) {
      lines.push('SQL: ' + m.message_metadata.sql_query)
    }
    lines.push('')
  })
  return lines.join('\n')
}

export function exportConversationToJson(
  conversation: ConversationList,
  messages: ChatMessageType[]
): string {
  return JSON.stringify(
    {
      conversation: {
        id: conversation.id,
        title: conversation.title,
        created_at: conversation.created_at,
        message_count: messages.length,
      },
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
        created_at: m.created_at,
        metadata: m.message_metadata,
      })),
      exported_at: new Date().toISOString(),
    },
    null,
    2
  )
}

export default ExportConversation
