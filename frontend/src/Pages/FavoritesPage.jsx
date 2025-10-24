import React from 'react'
import { Link } from 'react-router-dom'
import useSWR from 'swr'
import { getFavorites } from '../services/favorites'

export default function FavoritesPage() {
  const { data: vehicles, error, mutate } = useSWR('/favorites/me', getFavorites)

  if (error) return <div className="error">Erreur de chargement</div>
  if (!vehicles) return <div>Chargement...</div>

  if (vehicles.length === 0) {
    return (
      <div className="favorites-empty">
        <h2>Mes Favoris</h2>
        <p>Vous n'avez pas encore de favoris</p>
        <Link to="/" className="btn-primary">Rechercher des véhicules</Link>
      </div>
    )
  }

  return (
    <div className="favorites-page">
      <h2>Mes Favoris ({vehicles.length})</h2>
      
      <div className="results-grid">
        {vehicles.map(v => (
          <Link key={v.id} to={`/vehicle/${v.id}`} className="result-card">
            <div className="result-title">
              {v.title || `${v.make} ${v.model}`}
            </div>
            <div className="result-sub">
              {v.price ? `${v.price} €` : ''}
            </div>
            <div className="result-sub">
              {v.year} • {v.mileage} km
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}