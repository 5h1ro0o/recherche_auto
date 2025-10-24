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

export async function getFavorites() {
  const response = await client.get('/favorites/me')
  return response.data
}

export async function addFavorite(vehicleId) {
  const response = await client.post(`/favorites/${vehicleId}`)
  return response.data
}

export async function removeFavorite(vehicleId) {
  await client.delete(`/favorites/${vehicleId}`)
}

export async function checkFavorite(vehicleId) {
  const response = await client.get(`/favorites/check/${vehicleId}`)
  return response.data
}