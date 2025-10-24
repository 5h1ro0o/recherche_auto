// frontend/src/services/searchHistory.js
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

export async function getSearchHistory(limit = 20) {
  const response = await client.get(`/search-history/me?limit=${limit}`)
  return response.data
}

export async function clearSearchHistory() {
  await client.delete('/search-history/me')
}

export async function deleteSearchHistoryItem(historyId) {
  await client.delete(`/search-history/${historyId}`)
}