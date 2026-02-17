import apiClient from './client'
import type {
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationList,
} from '../../types/chatbot'

export const chatbotService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/chatbot/chat', request)
    return response.data
  },

  listConversations: async (skip = 0, limit = 50): Promise<ConversationList[]> => {
    const response = await apiClient.get<ConversationList[]>('/chatbot/conversations', {
      params: { skip, limit },
    })
    return response.data
  },

  createConversation: async (title?: string): Promise<Conversation> => {
    const response = await apiClient.post<Conversation>('/chatbot/conversations', {
      title: title ?? null,
    })
    return response.data
  },

  getConversation: async (conversationId: number): Promise<Conversation> => {
    const response = await apiClient.get<Conversation>(
      `/chatbot/conversations/${conversationId}`
    )
    return response.data
  },

  deleteConversation: async (conversationId: number): Promise<void> => {
    await apiClient.delete(`/chatbot/conversations/${conversationId}`)
  },
}
