import React, { useState } from 'react'
import { Link } from 'react-router-dom'

// Composant principal Results enrichi
export default function EnrichedResults({ loading, results = [], total = 0, page = 1, onPageChange }) {
  const [quickViewVehicle, setQuickViewVehicle] = useState(null)

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
        <p style={{ color: '#6a737d' }}>Chargement des résultats...</p>
      </div>
    )
  }

  if (!results || results.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>🔍</div>
        <h3 style={{ fontSize: '24px', color: '#24292e', marginBottom: '12px' }}>
          Aucun résultat trouvé
        </h3>
        <p style={{ color: '#6a737d', fontSize: '16px' }}>
          Essayez d'élargir vos critères de recherche
        </p>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: '16px', color: '#586069' }}>
        {total} résultat{total > 1 ? 's' : ''} trouvé{total > 1 ? 's' : ''}.
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {results.map((vehicle) => (
          <div
            key={vehicle.id}
            style={{
              border: '1px solid #e1e4e8',
              borderRadius: '6px',
              padding: '16px',
              backgroundColor: '#fff',
              transition: 'box-shadow 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 3px 12px rgba(0,0,0,0.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div style={{ display: 'flex', gap: '16px' }}>
              {/* Image */}
              <div style={{ flexShrink: 0 }}>
                {vehicle.images && vehicle.images.length > 0 ? (
                  <img
                    src={vehicle.images[0]}
                    alt={vehicle.title}
                    style={{
                      width: '200px',
                      height: '150px',
                      objectFit: 'cover',
                      borderRadius: '4px',
                    }}
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/200x150?text=No+Image'
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: '200px',
                      height: '150px',
                      backgroundColor: '#f6f8fa',
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#959da5',
                      fontSize: '48px',
                    }}
                  >
                    🚗
                  </div>
                )}
              </div>

              {/* Informations */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '18px', color: '#24292e', fontWeight: 600 }}>
                    {vehicle.title}
                  </h3>
                  {vehicle.make && vehicle.model && (
                    <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#586069' }}>
                      {vehicle.make} {vehicle.model}
                    </p>
                  )}
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '14px' }}>
                  {vehicle.price && (
                    <div>
                      <span style={{ fontWeight: 600, fontSize: '20px', color: '#0366d6' }}>
                        {typeof vehicle.price === 'number'
                          ? vehicle.price.toLocaleString('fr-FR')
                          : vehicle.price}{' '}
                        €
                      </span>
                    </div>
                  )}

                  {vehicle.year && (
                    <div style={{ color: '#586069' }}>
                      📅 {vehicle.year}
                    </div>
                  )}

                  {vehicle.mileage && (
                    <div style={{ color: '#586069' }}>
                      🛣️{' '}
                      {typeof vehicle.mileage === 'number'
                        ? vehicle.mileage.toLocaleString('fr-FR')
                        : vehicle.mileage}{' '}
                      km
                    </div>
                  )}

                  {vehicle.fuel_type && (
                    <div style={{ color: '#586069' }}>⛽ {vehicle.fuel_type}</div>
                  )}

                  {vehicle.transmission && (
                    <div style={{ color: '#586069' }}>⚙️ {vehicle.transmission}</div>
                  )}

                  {vehicle.location_city && (
                    <div style={{ color: '#586069' }}>📍 {vehicle.location_city}</div>
                  )}
                </div>

                {/* Sources */}
                {vehicle.source_ids && (
                  <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                    {Object.keys(vehicle.source_ids).map((source) => (
                      <span
                        key={source}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          backgroundColor: '#f1f8ff',
                          color: '#0366d6',
                          borderRadius: '3px',
                          fontWeight: 500,
                        }}
                      >
                        {source}
                      </span>
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div style={{ display: 'flex', gap: '12px', marginTop: 'auto' }}>
                  <Link
                    to={`/vehicle/${vehicle.id}`}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#0366d6',
                      color: '#fff',
                      textDecoration: 'none',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: 500,
                      display: 'inline-block',
                    }}
                  >
                    Voir les détails
                  </Link>

                  {vehicle.url && (
                    <a
                      href={vehicle.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#fff',
                        color: '#0366d6',
                        textDecoration: 'none',
                        border: '1px solid #0366d6',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontWeight: 500,
                        display: 'inline-block',
                      }}
                    >
                      Voir l'annonce
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {total > 20 && onPageChange && (
        <div
          style={{
            marginTop: '32px',
            display: 'flex',
            justifyContent: 'center',
            gap: '8px',
          }}
        >
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            style={{
              padding: '8px 16px',
              backgroundColor: page <= 1 ? '#f6f8fa' : '#0366d6',
              color: page <= 1 ? '#959da5' : '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: page <= 1 ? 'not-allowed' : 'pointer',
              fontWeight: 500,
            }}
          >
            ← Précédent
          </button>

          <span
            style={{
              padding: '8px 16px',
              display: 'flex',
              alignItems: 'center',
              color: '#586069',
            }}
          >
            Page {page}
          </span>

          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page * 20 >= total}
            style={{
              padding: '8px 16px',
              backgroundColor: page * 20 >= total ? '#f6f8fa' : '#0366d6',
              color: page * 20 >= total ? '#959da5' : '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: page * 20 >= total ? 'not-allowed' : 'pointer',
              fontWeight: 500,
            }}
          >
            Suivant →
          </button>
        </div>
      )}
    </div>
  )
}
