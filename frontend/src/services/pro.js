// frontend/src/services/pro.js
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

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

// ============ GESTION STOCK ============

export async function getMyStock(page = 1, size = 20, status = null, search = null) {
  const params = { page, size }
  if (status) params.status = status
  if (search) params.search = search
  
  const response = await client.get('/pro/stock', { params })
  return response.data
}

export async function getMyVehicle(vehicleId) {
  const response = await client.get(`/pro/stock/${vehicleId}`)
  return response.data
}

export async function addVehicle(vehicleData) {
  const response = await client.post('/pro/stock', vehicleData)
  return response.data
}

export async function updateVehicle(vehicleId, vehicleData) {
  const response = await client.patch(`/pro/stock/${vehicleId}`, vehicleData)
  return response.data
}

export async function deleteVehicle(vehicleId) {
  await client.delete(`/pro/stock/${vehicleId}`)
}

export async function toggleVisibility(vehicleId) {
  const response = await client.post(`/pro/stock/${vehicleId}/toggle-visibility`)
  return response.data
}

// ============ STATISTIQUES ============

export async function getMyStats() {
  const response = await client.get('/pro/stats')
  return response.data
}

export async function getVehiclesByMonth(months = 6) {
  const response = await client.get('/pro/stats/vehicles-by-month', {
    params: { months }
  })
  return response.data
}

export async function getPriceDistribution() {
  const response = await client.get('/pro/stats/price-distribution')
  return response.data
}