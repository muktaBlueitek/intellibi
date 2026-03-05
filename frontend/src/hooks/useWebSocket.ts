import { useEffect, useRef, useCallback, useState } from 'react'
import { getWebSocketClient } from '../services/websocket/websocketClient'
import { useAppSelector } from './redux'

type MessageHandler = (data: any) => void

export const useWebSocket = () => {
  const { token } = useAppSelector((state) => state.auth)
  const wsClientRef = useRef(getWebSocketClient())
  const handlersRef = useRef<Map<string, MessageHandler>>(new Map())
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!token) {
      setIsConnected(false)
      return
    }

    const client = wsClientRef.current
    let cancelled = false

    const connect = async () => {
      try {
        await client.connect(token)
        if (!cancelled) setIsConnected(true)
      } catch (error) {
        console.error('Failed to connect WebSocket:', error)
        if (!cancelled) setIsConnected(false)
      }
    }

    connect()

    return () => {
      cancelled = true
      client.disconnect()
      setIsConnected(false)
    }
  }, [token])

  const subscribe = useCallback((messageType: string, handler: MessageHandler) => {
    const client = wsClientRef.current
    client.on(messageType, handler)
    handlersRef.current.set(messageType, handler)
  }, [])

  const unsubscribe = useCallback((messageType: string) => {
    const client = wsClientRef.current
    const handler = handlersRef.current.get(messageType)
    if (handler) {
      client.off(messageType, handler)
      handlersRef.current.delete(messageType)
    }
  }, [])

  useEffect(() => {
    return () => {
      handlersRef.current.forEach((handler, messageType) => {
        wsClientRef.current.off(messageType, handler)
      })
      handlersRef.current.clear()
    }
  }, [])

  return {
    client: wsClientRef.current,
    subscribe,
    unsubscribe,
    isConnected,
  }
}
