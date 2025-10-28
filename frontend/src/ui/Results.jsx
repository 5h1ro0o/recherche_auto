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
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '20px',
        marginBottom: '32px'
      }}>
        {results.map((vehicle) => (
          <VehicleCard
            key={vehicle.id}
            vehicle={vehicle}
            onQuickView={() => setQuickViewVehicle(vehicle)}
          />
        ))}
      </div>

      {total > 10 && (
        <Pagination
          currentPage={page}
          totalPages={Math.ceil(total / 10)}
          onPageChange={onPageChange}
        />
      )}

      {quickViewVehicle && (
        <QuickViewModal
          vehicle={quickViewVehicle}
          onClose={() => setQuickViewVehicle(null)}
        />
      )}
    </div>
  )
}

function VehicleCard({ vehicle, onQuickView }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      style={{
        background: 'white',
        borderRadius: '16px',
        overflow: 'hidden',
        boxShadow: isHovered ? '0 8px 24px rgba(0,0,0,0.15)' : '0 2px 12px rgba(0,0,0,0.08)',
        transition: 'all 0.3s ease',
        transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
        position: 'relative'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Link to={`/vehicle/${vehicle.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
        <div style={{
          position: 'relative',
          height: '200px',
          background: '#f0f0f0'
        }}>
          {vehicle.image_url ? (
            <img
              src={vehicle.image_url}
              alt={vehicle.title}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
            />
          ) : (
            <div style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '48px',
              color: '#ccc'
            }}>
              🚗
            </div>
          )}

          {vehicle.seller_type === 'PRO' && (
            <div style={{
              position: 'absolute',
              top: '12px',
              left: '12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '11px',
              fontWeight: 600,
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
            }}>
              🏢 PRO
            </div>
          )}
        </div>

        <div style={{ padding: '16px' }}>
          <h3 style={{
            margin: '0 0 8px 0',
            fontSize: '16px',
            fontWeight: 600,
            color: '#24292e',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {vehicle.title || `${vehicle.make} ${vehicle.model}`}
          </h3>

          <div style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#28a745',
            marginBottom: '12px'
          }}>
            {vehicle.price?.toLocaleString()} €
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '8px',
            fontSize: '13px',
            color: '#6a737d'
          }}>
            <div>📅 {vehicle.year}</div>
            <div>🛣️ {vehicle.mileage?.toLocaleString()} km</div>
            <div>⛽ {vehicle.fuel_type}</div>
            <div>⚙️ {vehicle.transmission}</div>
          </div>

          {vehicle.location && (
            <div style={{
              marginTop: '12px',
              fontSize: '13px',
              color: '#6a737d',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              📍 {vehicle.location}
            </div>
          )}
        </div>
      </Link>

      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid #e1e4e8',
        display: 'flex',
        gap: '8px'
      }}>
        <button
          onClick={onQuickView}
          style={{
            flex: 1,
            padding: '8px 12px',
            background: 'white',
            border: '2px solid #e1e4e8',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600,
            color: '#24292e',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = '#f8f9fa'
            e.target.style.borderColor = '#667eea'
            e.target.style.color = '#667eea'
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'white'
            e.target.style.borderColor = '#e1e4e8'
            e.target.style.color = '#24292e'
          }}
        >
          👁️ Aperçu rapide
        </button>
      </div>
    </div>
  )
}

function Pagination({ currentPage, totalPages, onPageChange }) {
  const pages = []
  const maxVisiblePages = 5

  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2))
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)

  if (endPage - startPage < maxVisiblePages - 1) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '8px',
      marginTop: '32px'
    }}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        style={{
          padding: '10px 16px',
          background: 'white',
          border: '2px solid #e1e4e8',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
          opacity: currentPage === 1 ? 0.5 : 1,
          transition: 'all 0.2s'
        }}
      >
        ‹ Précédent
      </button>

      <div style={{ display: 'flex', gap: '8px' }}>
        {startPage > 1 && (
          <>
            <PageButton page={1} currentPage={currentPage} onPageChange={onPageChange} />
            {startPage > 2 && <span style={{ padding: '10px', color: '#6a737d' }}>...</span>}
          </>
        )}

        {pages.map(page => (
          <PageButton key={page} page={page} currentPage={currentPage} onPageChange={onPageChange} />
        ))}

        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span style={{ padding: '10px', color: '#6a737d' }}>...</span>}
            <PageButton page={totalPages} currentPage={currentPage} onPageChange={onPageChange} />
          </>
        )}
      </div>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        style={{
          padding: '10px 16px',
          background: 'white',
          border: '2px solid #e1e4e8',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
          opacity: currentPage === totalPages ? 0.5 : 1,
          transition: 'all 0.2s'
        }}
      >
        Suivant ›
      </button>
    </div>
  )
}

function PageButton({ page, currentPage, onPageChange }) {
  const isActive = page === currentPage

  return (
    <button
      onClick={() => onPageChange(page)}
      style={{
        padding: '10px 16px',
        background: isActive ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white',
        border: isActive ? 'none' : '2px solid #e1e4e8',
        borderRadius: '8px',
        fontSize: '14px',
        fontWeight: 600,
        color: isActive ? 'white' : '#24292e',
        cursor: 'pointer',
        transition: 'all 0.2s',
        minWidth: '44px'
      }}
      onMouseEnter={(e) => {
        if (!isActive) {
          e.target.style.background = '#f8f9fa'
          e.target.style.borderColor = '#667eea'
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          e.target.style.background = 'white'
          e.target.style.borderColor = '#e1e4e8'
        }
      }}
    >
      {page}
    </button>
  )
}

function QuickViewModal({ vehicle, onClose }) {
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.6)',
        zIndex: 10000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        backdropFilter: 'blur(4px)'
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '20px',
          maxWidth: '700px',
          width: '100%',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ position: 'relative' }}>
          <div style={{
            height: '350px',
            background: '#f0f0f0',
            position: 'relative'
          }}>
            {vehicle.image_url ? (
              <img
                src={vehicle.image_url}
                alt={vehicle.title}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
            ) : (
              <div style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '80px',
                color: '#ccc'
              }}>
                🚗
              </div>
            )}
          </div>

          <button
            onClick={onClose}
            style={{
              position: 'absolute',
              top: '16px',
              right: '16px',
              background: 'rgba(0,0,0,0.7)',
              border: 'none',
              color: 'white',
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              fontSize: '24px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.background = 'rgba(0,0,0,0.9)'}
            onMouseLeave={(e) => e.target.style.background = 'rgba(0,0,0,0.7)'}
          >
            ✕
          </button>
        </div>

        <div style={{ padding: '32px' }}>
          <h2 style={{
            margin: '0 0 8px 0',
            fontSize: '28px',
            fontWeight: 700,
            color: '#24292e'
          }}>
            {vehicle.title || `${vehicle.make} ${vehicle.model}`}
          </h2>

          <div style={{
            fontSize: '36px',
            fontWeight: 700,
            color: '#28a745',
            marginBottom: '24px'
          }}>
            {vehicle.price?.toLocaleString()} €
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '16px',
            marginBottom: '24px',
            padding: '20px',
            background: '#f8f9fa',
            borderRadius: '12px'
          }}>
            <InfoItem icon="📅" label="Année" value={vehicle.year} />
            <InfoItem icon="🛣️" label="Kilométrage" value={`${vehicle.mileage?.toLocaleString()} km`} />
            <InfoItem icon="⛽" label="Carburant" value={vehicle.fuel_type} />
            <InfoItem icon="⚙️" label="Transmission" value={vehicle.transmission} />
            {vehicle.location && (
              <InfoItem icon="📍" label="Localisation" value={vehicle.location} />
            )}
            {vehicle.seller_type && (
              <InfoItem icon="👤" label="Vendeur" value={vehicle.seller_type === 'PRO' ? 'Professionnel' : 'Particulier'} />
            )}
          </div>

          {vehicle.description && (
            <div style={{
              marginBottom: '24px',
              padding: '16px',
              background: '#f8f9fa',
              borderRadius: '12px'
            }}>
              <h4 style={{
                margin: '0 0 12px 0',
                fontSize: '16px',
                fontWeight: 600,
                color: '#24292e'
              }}>
                Description
              </h4>
              <p style={{
                margin: 0,
                fontSize: '14px',
                lineHeight: 1.6,
                color: '#586069'
              }}>
                {vehicle.description}
              </p>
            </div>
          )}

          <Link
            to={`/vehicle/${vehicle.id}`}
            style={{
              display: 'block',
              width: '100%',
              padding: '16px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              textAlign: 'center',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: 600,
              boxShadow: '0 4px 12px rgba(102,126,234,0.3)',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 6px 20px rgba(102,126,234,0.4)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = '0 4px 12px rgba(102,126,234,0.3)'
            }}
          >
            Voir les détails complets →
          </Link>
        </div>
      </div>
    </div>
  )
}

function InfoItem({ icon, label, value }) {
  return (
    <div>
      <div style={{
        fontSize: '12px',
        color: '#6a737d',
        marginBottom: '4px',
        fontWeight: 500
      }}>
        {icon} {label}
      </div>
      <div style={{
        fontSize: '15px',
        fontWeight: 600,
        color: '#24292e'
      }}>
        {value}
      </div>
    </div>
  )
}
