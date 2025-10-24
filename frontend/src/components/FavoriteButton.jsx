import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { addFavorite, removeFavorite, checkFavorite } from '../services/favorites'

export default function FavoriteButton({ vehicleId }) {
  const { isAuthenticated } = useAuth()
  const [isFavorite, setIsFavorite] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      loadFavoriteStatus()
    }
  }, [vehicleId, isAuthenticated])

  async function loadFavoriteStatus() {
    try {
      const data = await checkFavorite(vehicleId)
      setIsFavorite(data.is_favorite)
    } catch (error) {
      console.error('Error checking favorite:', error)
    }
  }

  async function toggleFavorite() {
    if (!isAuthenticated) {
      alert('Vous devez être connecté pour ajouter des favoris')
      return
    }

    setLoading(true)
    try {
      if (isFavorite) {
        await removeFavorite(vehicleId)
        setIsFavorite(false)
      } else {
        await addFavorite(vehicleId)
        setIsFavorite(true)
      }
    } catch (error) {
      console.error('Error toggling favorite:', error)
      alert('Erreur lors de la modification')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={toggleFavorite}
      disabled={loading}
      className={`favorite-btn ${isFavorite ? 'active' : ''}`}
      title={isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
    >
      {loading ? '...' : isFavorite ? '❤️' : '🤍'}
    </button>
  )
}