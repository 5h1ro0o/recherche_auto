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

  const formatPrice = (price) => {
    if (!price) return 'N/A'
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
    }).format(price)
  }

  const formatMileage = (mileage) => {
    if (!mileage) return 'N/A'
    return new Intl.NumberFormat('fr-FR').format(mileage) + ' km'
  }

  return (
    <div>
      <div style={{ marginBottom: '16px', color: '#586069' }}>
        {total} résultat{total > 1 ? 's' : ''} trouvé{total > 1 ? 's' : ''}.
      </div>
      <div style={{ display: 'grid', gap: '16px' }}>
        {results.map((vehicle) => (
          <div
            key={vehicle.id}
            style={{
              border: '1px solid #e1e4e8',
              borderRadius: '6px',
              padding: '16px',
              backgroundColor: '#fff',
              transition: 'box-shadow 0.2s',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 3px 12px rgba(0,0,0,0.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div style={{ display: 'flex', gap: '16px' }}>
              {/* Image du véhicule */}
              <div
                style={{
                  width: '200px',
                  height: '150px',
                  backgroundColor: '#f6f8fa',
                  borderRadius: '6px',
                  overflow: 'hidden',
                  flexShrink: 0,
                }}
              >
                {vehicle.images && vehicle.images.length > 0 ? (
                  <img
                    src={vehicle.images[0]}
                    alt={vehicle.title}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '48px',
                    }}
                  >
                    🚗
                  </div>
                )}
              </div>

              {/* Informations du véhicule */}
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', color: '#24292e' }}>
                  <Link
                    to={`/vehicle/${vehicle.id}`}
                    style={{ color: '#0366d6', textDecoration: 'none' }}
                  >
                    {vehicle.title || `${vehicle.make || ''} ${vehicle.model || ''}`}
                  </Link>
                </h3>

                <div style={{ display: 'flex', gap: '16px', marginBottom: '12px', flexWrap: 'wrap' }}>
                  {vehicle.year && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      📅 {vehicle.year}
                    </span>
                  )}
                  {vehicle.mileage && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      🛣️ {formatMileage(vehicle.mileage)}
                    </span>
                  )}
                  {vehicle.fuel_type && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      ⛽ {vehicle.fuel_type}
                    </span>
                  )}
                  {vehicle.transmission && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      ⚙️ {vehicle.transmission}
                    </span>
                  )}
                </div>

                {vehicle.description && (
                  <p
                    style={{
                      color: '#6a737d',
                      fontSize: '14px',
                      margin: '0 0 12px 0',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {vehicle.description}
                  </p>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                    {formatPrice(vehicle.price)}
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => setQuickViewVehicle(vehicle)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#f6f8fa',
                        border: '1px solid #e1e4e8',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                      }}
                    >
                      Aperçu rapide
                    </button>
                    <Link
                      to={`/vehicle/${vehicle.id}`}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#0366d6',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '6px',
                        textDecoration: 'none',
                        fontSize: '14px',
                        display: 'inline-block',
                      }}
                    >
                      Voir détails
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {total > 20 && onPageChange && (
        <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'center', gap: '8px' }}>
          <button
            disabled={page === 1}
            onClick={() => onPageChange(page - 1)}
            style={{
              padding: '8px 16px',
              border: '1px solid #e1e4e8',
              borderRadius: '6px',
              backgroundColor: page === 1 ? '#f6f8fa' : '#fff',
              cursor: page === 1 ? 'not-allowed' : 'pointer',
            }}
          >
            Précédent
          </button>
          <span style={{ padding: '8px 16px', color: '#586069' }}>
            Page {page} / {Math.ceil(total / 20)}
          </span>
          <button
            disabled={page >= Math.ceil(total / 20)}
            onClick={() => onPageChange(page + 1)}
            style={{
              padding: '8px 16px',
              border: '1px solid #e1e4e8',
              borderRadius: '6px',
              backgroundColor: page >= Math.ceil(total / 20) ? '#f6f8fa' : '#fff',
              cursor: page >= Math.ceil(total / 20) ? 'not-allowed' : 'pointer',
            }}
          >
            Suivant
          </button>
        </div>
      )}

      {/* Modal d'aperçu rapide */}
      {quickViewVehicle && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
          onClick={() => setQuickViewVehicle(null)}
        >
          <div
            style={{
              backgroundColor: '#fff',
              borderRadius: '8px',
              padding: '24px',
              maxWidth: '600px',
              maxHeight: '80vh',
              overflow: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ margin: 0 }}>
                {quickViewVehicle.title || `${quickViewVehicle.make} ${quickViewVehicle.model}`}
              </h2>
              <button
                onClick={() => setQuickViewVehicle(null)}
                style={{
                  border: 'none',
                  background: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                }}
              >
                ✕
              </button>
            </div>

            {quickViewVehicle.images && quickViewVehicle.images.length > 0 && (
              <img
                src={quickViewVehicle.images[0]}
                alt={quickViewVehicle.title}
                style={{
                  width: '100%',
                  borderRadius: '6px',
                  marginBottom: '16px',
                }}
              />
            )}

            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#28a745', marginBottom: '12px' }}>
                {formatPrice(quickViewVehicle.price)}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                {quickViewVehicle.year && (
                  <div>
                    <strong>Année:</strong> {quickViewVehicle.year}
                  </div>
                )}
                {quickViewVehicle.mileage && (
                  <div>
                    <strong>Kilométrage:</strong> {formatMileage(quickViewVehicle.mileage)}
                  </div>
                )}
                {quickViewVehicle.fuel_type && (
                  <div>
                    <strong>Carburant:</strong> {quickViewVehicle.fuel_type}
                  </div>
                )}
                {quickViewVehicle.transmission && (
                  <div>
                    <strong>Transmission:</strong> {quickViewVehicle.transmission}
                  </div>
                )}
              </div>

              {quickViewVehicle.description && (
                <div>
                  <strong>Description:</strong>
                  <p style={{ color: '#6a737d' }}>{quickViewVehicle.description}</p>
                </div>
              )}
            </div>

            <Link
              to={`/vehicle/${quickViewVehicle.id}`}
              style={{
                display: 'block',
                textAlign: 'center',
                padding: '12px',
                backgroundColor: '#0366d6',
                color: '#fff',
                borderRadius: '6px',
                textDecoration: 'none',
              }}
            >
              Voir tous les détails
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
