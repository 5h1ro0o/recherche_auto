// frontend/src/services/chatbot.js
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000  // Plus long pour l'IA
})

// Intercepteur token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Recherche conversationnelle complète
 */
export async function chatSearch(message, context = null) {
  const response = await client.post('/chat/search', {
    message,
    context
  })
  return response.data
}

/**
 * Parse uniquement (sans recherche)
 */
export async function chatParse(message) {
  const response = await client.post('/chat/parse', {
    message
  })
  return response.data
}