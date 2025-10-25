// frontend/src/services/messages.js - VERSION COMPLÈTE
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let wsConnection = null

// ============ REST API ============

export async function getConversations() {
  const response = await client.get('/messages/conversations')
  return response.data
}

export async function getOrCreateConversation(otherUserId) {
  const response = await client.post(`/messages/conversations/${otherUserId}`)
  return response.data
}

export async function getConversationMessages(conversationId, limit = 100) {
  const response = await client.get(`/messages/${conversationId}`, {
    params: { limit }
  })
  return response.data
}

export async function sendMessage(messageData) {
  const response = await client.post('/messages', messageData)
  return response.data
}

export async function markMessageAsRead(messageId) {
  const response = await client.patch(`/messages/${messageId}/read`)
  return response.data
}

export async function getUnreadCount() {
  const response = await client.get('/messages/unread/count')
  return response.data
}

// ============ TEMPLATES ============

export async function getMessageTemplates() {
  const response = await client.get('/messages/templates')
  return response.data
}

// ============ ATTACHMENTS ============

export async function uploadAttachment(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await client.post('/messages/attachments', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}

// ============ WEBSOCKET ============

export function connectWebSocket(userId) {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    return wsConnection
  }

  const wsUrl = `${WS_BASE}/messages/ws/${userId}`
  
  wsConnection = new WebSocket(wsUrl)

  wsConnection.onopen = () => {
    console.log('✅ WebSocket connecté')
    
    // Ping pour keep-alive
    setInterval(() => {
      if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
  }

  wsConnection.onerror = (error) => {
    console.error('❌ Erreur WebSocket:', error)
  }

  wsConnection.onclose = () => {
    console.log('🔌 WebSocket déconnecté')
    wsConnection = null
  }

  return wsConnection
}

export function disconnectWebSocket() {
  if (wsConnection) {
    wsConnection.close()
    wsConnection = null
  }
}

export function sendTypingStatus(conversationId, recipientId, isTyping) {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    wsConnection.send(JSON.stringify({
      type: isTyping ? 'typing_start' : 'typing_stop',
      conversation_id: conversationId,
      recipient_id: recipientId
    }))
  }
}