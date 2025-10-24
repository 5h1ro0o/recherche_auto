import React from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  if (!user) return <div>Chargement...</div>

  return (
    <div className="profile-container">
      <h2>Mon Profil</h2>
      
      <div className="profile-card">
        <div className="profile-field">
          <label>Email</label>
          <p>{user.email}</p>
        </div>

        <div className="profile-field">
          <label>Nom</label>
          <p>{user.full_name || '—'}</p>
        </div>

        <div className="profile-field">
          <label>Téléphone</label>
          <p>{user.phone || '—'}</p>
        </div>

        <div className="profile-field">
          <label>Type de compte</label>
          <p>
            {user.role === 'PRO' && '🏢 Professionnel'}
            {user.role === 'PARTICULAR' && '👤 Particulier'}
            {user.role === 'EXPERT' && '⭐ Expert'}
            {user.role === 'ADMIN' && '🔧 Administrateur'}
          </p>
        </div>

        <div className="profile-field">
          <label>Compte vérifié</label>
          <p>{user.is_verified ? '✅ Oui' : '⏳ En attente'}</p>
        </div>

        <div className="profile-field">
          <label>Membre depuis</label>
          <p>{new Date(user.created_at).toLocaleDateString()}</p>
        </div>

        <button onClick={handleLogout} className="logout-btn">
          Déconnexion
        </button>
      </div>
    </div>
  )
}