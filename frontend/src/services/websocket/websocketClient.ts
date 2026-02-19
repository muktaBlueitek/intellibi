type MessageHandler = (data: any) => void
type ErrorHandler = (error: Event) => void

interface WebSocketMessage {
  type: string
  [key: string]: any
}

class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private handlers: Map<string, MessageHandler[]> = new Map()
  private errorHandler: ErrorHandler | null = null
  private isConnecting = false
  private shouldReconnect = true

  constructor(baseUrl: string = '') {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = baseUrl || window.location.host.replace(':3000', ':8000')
    this.url = `${wsProtocol}//${wsHost}/api/v1/ws`
  }

  connect(token: string): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return Promise.resolve()
    }

    this.token = token
    this.isConnecting = true
    this.shouldReconnect = true

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.url}?token=${encodeURIComponent(token)}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          if (this.errorHandler) {
            this.errorHandler(error)
          }
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.isConnecting = false
          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnect()
          }
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  private reconnect() {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    setTimeout(() => {
      if (this.token && this.shouldReconnect) {
        this.connect(this.token).catch(() => {
          // Reconnection failed, will retry
        })
      }
    }, delay)
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.handlers.clear()
  }

  private handleMessage(message: WebSocketMessage) {
    const handlers = this.handlers.get(message.type) || []
    handlers.forEach(handler => handler(message))
  }

  on(messageType: string, handler: MessageHandler) {
    if (!this.handlers.has(messageType)) {
      this.handlers.set(messageType, [])
    }
    this.handlers.get(messageType)!.push(handler)
  }

  off(messageType: string, handler: MessageHandler) {
    const handlers = this.handlers.get(messageType)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  onError(handler: ErrorHandler) {
    this.errorHandler = handler
  }

  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  subscribeToDashboard(dashboardId: number) {
    this.send({
      type: 'subscribe_dashboard',
      dashboard_id: dashboardId,
    })
  }

  unsubscribeFromDashboard(dashboardId: number) {
    this.send({
      type: 'unsubscribe_dashboard',
      dashboard_id: dashboardId,
    })
  }

  subscribeToChat(conversationId: number) {
    this.send({
      type: 'subscribe_chat',
      conversation_id: conversationId,
    })
  }

  unsubscribeFromChat(conversationId: number) {
    this.send({
      type: 'unsubscribe_chat',
      conversation_id: conversationId,
    })
  }

  ping() {
    this.send({
      type: 'ping',
      timestamp: Date.now(),
    })
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// Singleton instance
let wsClientInstance: WebSocketClient | null = null

export const getWebSocketClient = (): WebSocketClient => {
  if (!wsClientInstance) {
    wsClientInstance = new WebSocketClient()
  }
  return wsClientInstance
}

export default WebSocketClient
