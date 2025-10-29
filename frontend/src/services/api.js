import axios from 'axios'

// Configuration de l'API
const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

// Créer une instance Axios
const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour ajouter le token d'authentification
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour gérer les erreurs de réponse
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Si 401 (non autorisé), déconnecter l'utilisateur
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      // Rediriger vers la page de connexion sauf si on est déjà sur /login ou /register
      if (!window.location.pathname.match(/\/(login|register)/)) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Fonctions helper pour les requêtes API
export async function apiGet(path, config = {}) {
  const response = await client.get(path, config)
  return response.data
}

export async function apiPost(path, data, config = {}) {
  const response = await client.post(path, data, config)
  return response.data
}

export async function apiPut(path, data, config = {}) {
  const response = await client.put(path, data, config)
  return response.data
}

export async function apiPatch(path, data, config = {}) {
  const response = await client.patch(path, data, config)
  return response.data
}

export async function apiDelete(path, config = {}) {
  const response = await client.delete(path, config)
  return response.data
}

// Export du client pour les cas d'usage avancés
export default client
