import { useEffect, useState, useRef } from 'react'
import { chatbotService } from '../services/api/chatbotService'
import { datasourceService } from '../services/api/datasourceService'
import type {
  Conversation,
  ConversationList,
  ChatMessage as ChatMessageType,
  ChatResponse,
} from '../types/chatbot'
import type { DataSource } from '../types/datasource'
import ChatMessageBubble from '../components/Chatbot/ChatMessageBubble'
import TypingIndicator from '../components/Chatbot/TypingIndicator'
import QuerySuggestions from '../components/Chatbot/QuerySuggestions'
import ExportConversation, {
  exportConversationToText,
  exportConversationToJson,
} from '../components/Chatbot/ExportConversation'
import './ChatbotPage.css'

const DEFAULT_SUGGESTIONS = [
  'What are the total sales by region?',
  'Show me the top 10 products by revenue',
  'Summarize the data in this datasource',
]

function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const ChatbotPage = () => {
  const [conversations, setConversations] = useState<ConversationList[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [suggestedQueries, setSuggestedQueries] = useState<string[]>(DEFAULT_SUGGESTIONS)
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [datasources, setDatasources] = useState<DataSource[]>([])
  const [datasourceId, setDatasourceId] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const listLoadingRef = useRef(false)

  const loadConversations = async () => {
    if (listLoadingRef.current) return
    listLoadingRef.current = true
    try {
      const list = await chatbotService.listConversations()
      setConversations(list)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load conversations')
    } finally {
      listLoadingRef.current = false
    }
  }

  const loadDatasources = async () => {
    try {
      const list = await datasourceService.getDataSources()
      setDatasources(list.filter((d) => d.type === 'postgresql' || d.type === 'mysql'))
    } catch {
      // Non-blocking
    }
  }

  useEffect(() => {
    loadConversations()
    loadDatasources()
  }, [])

  useEffect(() => {
    if (!currentConversation) {
      setMessages([])
      setSuggestedQueries(DEFAULT_SUGGESTIONS)
      return
    }
    setMessages(currentConversation.messages || [])
    const lastAssistant = [...(currentConversation.messages || [])]
      .reverse()
      .find((m) => m.role === 'assistant')
    const suggested = (lastAssistant?.message_metadata?.suggested_queries) || DEFAULT_SUGGESTIONS
    setSuggestedQueries(Array.isArray(suggested) ? suggested : DEFAULT_SUGGESTIONS)
  }, [currentConversation])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const selectConversation = async (conv: ConversationList) => {
    setError(null)
    try {
      const full = await chatbotService.getConversation(conv.id)
      setCurrentConversation(full)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load conversation')
    }
  }

  const startNewConversation = () => {
    setCurrentConversation(null)
    setMessages([])
    setSuggestedQueries(DEFAULT_SUGGESTIONS)
    setError(null)
  }

  const sendMessage = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setError(null)
    setInputValue('')

    let conversationId = currentConversation?.id ?? null

    if (!conversationId) {
      try {
        const newConv = await chatbotService.createConversation()
        conversationId = newConv.id
        setCurrentConversation({ ...newConv, messages: [] })
        setConversations((prev) => [
          { id: newConv.id, user_id: newConv.user_id, title: newConv.title, created_at: newConv.created_at, updated_at: newConv.updated_at, message_count: 0 },
          ...prev,
        ])
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Failed to create conversation')
        return
      }
    }

    const userMessage: ChatMessageType = {
      id: 0,
      conversation_id: conversationId!,
      role: 'user',
      content: trimmed,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      const response: ChatResponse = await chatbotService.sendMessage({
        message: trimmed,
        conversation_id: conversationId!,
        datasource_id: datasourceId ?? undefined,
      })

      const assistantMessage: ChatMessageType = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.message,
        message_metadata: {
          sql_query: response.sql_query ?? undefined,
          query_result: response.execution_result ?? undefined,
          visualization_suggestion: response.visualization_suggestion ?? undefined,
          statistical_summary: response.statistical_summary ?? undefined,
          insights: response.insights ?? undefined,
          suggested_queries: response.suggested_queries ?? undefined,
        },
        created_at: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])
      if (response.suggested_queries && response.suggested_queries.length > 0) {
        setSuggestedQueries(response.suggested_queries)
      }

      setCurrentConversation((prev) => {
        if (!prev || prev.id !== response.conversation_id) return prev
        return {
          ...prev,
          messages: [...(prev.messages || []), userMessage, assistantMessage],
          updated_at: new Date().toISOString(),
        }
      })
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to get response')
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputValue)
  }

  const handleExport = (format: 'json' | 'text') => {
    if (!currentConversation || messages.length === 0) return
    const listItem: ConversationList = {
      id: currentConversation.id,
      user_id: currentConversation.user_id,
      title: currentConversation.title,
      created_at: currentConversation.created_at,
      updated_at: currentConversation.updated_at ?? null,
      message_count: messages.length,
    }
    if (format === 'text') {
      const text = exportConversationToText(listItem.title, messages)
      downloadBlob(text, `chat-${currentConversation.id}.txt`, 'text/plain')
    } else {
      const json = exportConversationToJson(listItem, messages)
      downloadBlob(json, `chat-${currentConversation.id}.json`, 'application/json')
    }
  }

  return (
    <div className="chatbot-page">
      <aside className="chatbot-sidebar">
        <button type="button" className="chatbot-new-chat" onClick={startNewConversation}>
          + New chat
        </button>
        <div className="chatbot-conversations-list">
          {conversations.map((c) => (
            <button
              key={c.id}
              type="button"
              className={`chatbot-conv-item ${currentConversation?.id === c.id ? 'active' : ''}`}
              onClick={() => selectConversation(c)}
            >
              <span className="chatbot-conv-title">{c.title || `Chat ${c.id}`}</span>
              <span className="chatbot-conv-meta">{c.message_count ?? 0} messages</span>
            </button>
          ))}
        </div>
      </aside>

      <section className="chatbot-main">
        <div className="chatbot-header">
          <h1>AI Chatbot</h1>
          <div className="chatbot-header-actions">
            {datasources.length > 0 && (
              <select
                className="chatbot-datasource-select"
                value={datasourceId ?? ''}
                onChange={(e) => setDatasourceId(e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">No datasource</option>
                {datasources.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            )}
            <ExportConversation
              conversation={
                currentConversation
                  ? {
                      id: currentConversation.id,
                      user_id: currentConversation.user_id,
                      title: currentConversation.title,
                      created_at: currentConversation.created_at,
                      updated_at: currentConversation.updated_at ?? null,
                      message_count: messages.length,
                    }
                  : null
              }
              messages={messages}
              onExport={handleExport}
              disabled={messages.length === 0}
            />
          </div>
        </div>

        {error && (
          <div className="chatbot-error" role="alert">
            {error}
          </div>
        )}

        <div className="chatbot-messages">
          {messages.length === 0 && !loading && (
            <div className="chatbot-welcome">
              <p>Ask anything about your data. You can ask for summaries, trends, or specific metrics.</p>
              <QuerySuggestions
                suggestions={suggestedQueries}
                onSelect={(q) => setInputValue(q)}
                disabled={loading}
              />
            </div>
          )}
          {messages.map((m) => (
            <ChatMessageBubble key={m.id || `${m.role}-${m.created_at}`} message={m} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        <form className="chatbot-input-area" onSubmit={handleSubmit}>
          <QuerySuggestions
            suggestions={suggestedQueries}
            onSelect={(q) => sendMessage(q)}
            disabled={loading}
          />
          <div className="chatbot-input-row">
            <input
              type="text"
              className="chatbot-input"
              placeholder="Type your question..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading}
              aria-label="Message"
            />
            <button type="submit" className="chatbot-send" disabled={loading || !inputValue.trim()}>
              Send
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

export default ChatbotPage
