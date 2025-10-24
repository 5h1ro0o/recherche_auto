// frontend/src/services/alerts.js
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 8000
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function getAlerts() {
  const response = await client.get('/alerts/me')
  return response.data
}

export async function createAlert(alertData) {
  const response = await client.post('/alerts', alertData)
  return response.data
}

export async function updateAlert(alertId, updateData) {
  const response = await client.patch(`/alerts/${alertId}`, updateData)
  return response.data
}

export async function deleteAlert(alertId) {
  await client.delete(`/alerts/${alertId}`)
}

export async function toggleAlert(alertId) {
  const response = await client.post(`/alerts/${alertId}/toggle`)
  return response.data
}