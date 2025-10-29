import { apiPost, apiGet, apiPatch } from './api'

export async function login(email, password) {
  return await apiPost('/auth/login', { email, password })
}

export async function register(userData) {
  return await apiPost('/auth/register', userData)
}

export async function getCurrentUser() {
  return await apiGet('/auth/me')
}

export async function updateProfile(data) {
  return await apiPatch('/auth/me', data)
}

export async function logout() {
  // Côté client, on supprime juste les tokens
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')

  // On pourrait aussi appeler l'API si on veut invalider le token côté serveur
  try {
    await apiPost('/auth/logout', {})
  } catch (error) {
    // Ignorer les erreurs de logout
    console.log('Logout API call failed:', error)
  }
}
