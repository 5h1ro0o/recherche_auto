import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import useSWR from 'swr'
import { apiGet } from '../services/api'

export default function VehiclePage(){
  const { id } = useParams()
  const [showSimilar, setShowSimilar] = useState(false)
  
  const { data, error } = useSWR(id ? `/vehicles/${id}` : null, () => apiGet(`/vehicles/${id}`))
  const { data: similarData } = useSWR(
    showSimilar && id ? `/vehicles/${id}/similar` : null,
    () => apiGet(`/vehicles/${id}/similar`)
  )

  if(error) return <div className="error">Erreur chargement véhicule</div>
  if(!data) return <div>Chargement...</div>

  const v = data
  
  return (
    <div className="vehicle-detail">
      <h2>{v.title || `${v.make} ${v.model}`}</h2>
      
      <div className="vehicle-info">
        <div>💰 Prix : {v.price ? v.price + ' €' : '—'}</div>
        <div>📅 Année : {v.year}</div>
        <div>🛣️ Kilométrage : {v.mileage} km</div>
        <div>🔧 VIN : {v.vin || '—'}</div>
        {v.fuel_type && <div>⛽ Carburant : {v.fuel_type}</div>}
        {v.transmission && <div>⚙️ Transmission : {v.transmission}</div>}
      </div>
      
      {v.description && (
        <div className="vehicle-description">
          <h3>Description</h3>
          <p>{v.description}</p>
        </div>
      )}
      
      <div className="images">
        {(v.images || []).map((u,i)=>(<img key={i} src={u} alt="photo"/>))}
      </div>

      <div className="vehicle-actions">
        <button 
          onClick={() => setShowSimilar(!showSimilar)}
          className="btn-similar"
        >
          {showSimilar ? '❌ Masquer' : '🔍 Voir véhicules similaires'}
        </button>
      </div>

      {showSimilar && similarData && (
        <div className="similar-section">
          <h3>Véhicules similaires ({similarData.total})</h3>
          
          {similarData.total === 0 ? (
            <p>Aucun véhicule similaire trouvé</p>
          ) : (
            <div className="results-grid">
              {similarData.hits.map(h => (
                <Link key={h.id} to={`/vehicle/${h.id}`} className="result-card">
                  <div className="result-title">
                    {h.source?.title || `${h.source?.make} ${h.source?.model}`}
                  </div>
                  <div className="result-sub">
                    {h.source?.price ? `${h.source.price} €` : ''}
                  </div>
                  <div className="result-sub">
                    {h.source?.year} • {h.source?.mileage} km
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}