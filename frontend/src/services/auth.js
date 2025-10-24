import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 8000
})

// Intercepteur pour ajouter le token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Intercepteur pour gérer les erreurs 401
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export async function login(email, password) {
  const response = await client.post('/auth/login', { email, password })
  return response.data
}

export async function register(userData) {
  const response = await client.post('/auth/register', userData)
  return response.data
}

export async function getCurrentUser() {
  const response = await client.get('/auth/me')
  return response.data
}

export async function updateProfile(data) {
  const response = await client.patch('/auth/me', data)
  return response.data
}