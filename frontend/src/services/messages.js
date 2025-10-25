// frontend/src/services/messages.js
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

/**
 * Récupérer toutes les conversations
 */
export async function getConversations() {
  const response = await client.get('/messages/conversations')
  return response.data
}

/**
 * Créer ou récupérer une conversation avec un utilisateur
 */
export async function getOrCreateConversation(otherUserId) {
  const response = await client.post(`/messages/conversations/${otherUserId}`)
  return response.data
}

/**
 * Récupérer l'historique d'une conversation
 */
export async function getConversationMessages(conversationId, limit = 100) {
  const response = await client.get(`/messages/${conversationId}`, {
    params: { limit }
  })
  return response.data
}

/**
 * Envoyer un message
 */
export async function sendMessage(messageData) {
  const response = await client.post('/messages', messageData)
  return response.data
}

/**
 * Marquer un message comme lu
 */
export async function markMessageAsRead(messageId) {
  const response = await client.patch(`/messages/${messageId}/read`)
  return response.data
}

/**
 * Obtenir le nombre de messages non lus
 */
export async function getUnreadCount() {
  const response = await client.get('/messages/unread/count')
  return response.data
}

/**
 * Connexion WebSocket pour messages temps réel
 */
export function connectWebSocket(userId) {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    return wsConnection
  }

  const token = localStorage.getItem('access_token')
  const wsUrl = `${WS_BASE}/messages/ws/${userId}`
  
  wsConnection = new WebSocket(wsUrl)

  wsConnection.onopen = () => {
    console.log('✅ WebSocket connecté')
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

/**
 * Déconnexion WebSocket
 */
export function disconnectWebSocket() {
  if (wsConnection) {
    wsConnection.close()
    wsConnection = null
  }
}