// frontend/src/services/assisted.js
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

// ============ CLIENT ROUTES ============

export async function createAssistedRequest(requestData) {
  const response = await client.post('/assisted/requests', requestData)
  return response.data
}

export async function getMyRequests(statusFilter = null) {
  const params = statusFilter ? { status_filter: statusFilter } : {}
  const response = await client.get('/assisted/requests/me', { params })
  return response.data
}

export async function getRequestDetail(requestId) {
  const response = await client.get(`/assisted/requests/${requestId}`)
  return response.data
}

export async function updateMyRequest(requestId, updateData) {
  const response = await client.patch(`/assisted/requests/${requestId}`, updateData)
  return response.data
}

export async function cancelRequest(requestId) {
  await client.delete(`/assisted/requests/${requestId}`)
}

// ============ PROPOSALS (CLIENT) ============

export async function getMyProposals(requestId) {
  const response = await client.get(`/assisted/requests/${requestId}/proposals`)
  return response.data
}

export async function updateProposalStatus(proposalId, status, rejectionReason = null) {
  const response = await client.patch(`/assisted/proposals/${proposalId}`, {
    status,
    rejection_reason: rejectionReason
  })
  return response.data
}

// ============ EXPERT ROUTES ============

export async function getAvailableRequests(statusFilter = 'PENDING') {
  const params = statusFilter ? { status_filter: statusFilter } : {}
  const response = await client.get('/assisted/requests', { params })
  return response.data
}

export async function acceptRequest(requestId) {
  const response = await client.post(`/assisted/requests/${requestId}/accept`)
  return response.data
}

export async function proposeVehicle(requestId, vehicleId, message = null) {
  const response = await client.post(`/assisted/requests/${requestId}/propose`, {
    vehicle_id: vehicleId,
    message
  })
  return response.data
}

export async function completeRequest(requestId) {
  const response = await client.post(`/assisted/requests/${requestId}/complete`)
  return response.data
}

// ============ EXPERT STATS ============

export async function getExpertStats() {
  const response = await client.get('/assisted/expert/stats')
  return response.data
}