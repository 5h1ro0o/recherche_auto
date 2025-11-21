import React, { useState } from 'react'

// Simulation de données - remplacer par de vrais appels API
const mockVehicleData = {
  id: 'v123',
  title: 'Peugeot 208 Active 1.2 PureTech',
  price: 14500,
  year: 2020,
  mileage: 35000,
  fuel_type: 'Essence',
  transmission: 'Manuelle',
  vin: 'VF3XXXXXXXXXXXXXXX',
  seller_type: 'PRO',
  location: 'Paris 15ème',
  description: 'Magnifique Peugeot 208 en excellent état. Première main, entretien complet chez le concessionnaire, carnet d\'entretien à jour. Equipements : climatisation automatique, régulateur de vitesse, écran tactile 7", aide au stationnement arrière.',
  images: [
    'https://via.placeholder.com/800x600/667eea/ffffff?text=Photo+1',
    'https://via.placeholder.com/800x600/764ba2/ffffff?text=Photo+2',
    'https://via.placeholder.com/800x600/28a745/ffffff?text=Photo+3',
    'https://via.placeholder.com/800x600/ffc107/ffffff?text=Photo+4'
  ],
  seller: {
    id: 'seller1',
    name: 'Auto Premium Paris',
    phone: '01 23 45 67 89',
    email: 'contact@autopremium.fr',
    is_pro: true
  },
  features: [
    'Climatisation automatique',
    'Régulateur de vitesse',
    'Écran tactile 7"',
    'Aide au stationnement',
    'Bluetooth',
    'Volant multifonction'
  ],
  technical_specs: {
    engine: '1.2 PureTech 75ch',
    power: '75 ch',
    co2: '105 g/km',
    consumption: '4.5 L/100km',
    doors: 5,
    seats: 5,
    color: 'Blanc Banquise'
  },
  price_history: [
    { date: '2025-01-15', price: 15200 },
    { date: '2025-02-01', price: 14900 },
    { date: '2025-02-15', price: 14500 }
  ],
  expert_opinion: {
    score: 8.5,
    pros: [
      'Prix très compétitif pour l\'année et le kilométrage',
      'Excellent état général',
      'Faible consommation',
      'Vendeur professionnel fiable'
    ],
    cons: [
      'Puissance modeste (75ch)',
      'Options limitées'
    ],
    verdict: 'Excellent choix pour un usage urbain. Le rapport qualité-prix est très intéressant.'
  },
  similar_vehicles: [
    { id: 's1', title: 'Renault Clio 1.0 TCe', price: 13800, year: 2019, mileage: 42000 },
    { id: 's2', title: 'Peugeot 208 1.2', price: 14200, year: 2020, mileage: 38000 },
    { id: 's3', title: 'Citroën C3 1.2', price: 13500, year: 2019, mileage: 40000 }
  ],
  created_at: new Date().toISOString()
}

export default function EnhancedVehiclePage() {
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [showLightbox, setShowLightbox] = useState(false)
  const [showContactModal, setShowContactModal] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)

  const vehicle = mockVehicleData

  function nextImage() {
    setCurrentImageIndex((prev) => (prev + 1) % vehicle.images.length)
  }

  function prevImage() {
    setCurrentImageIndex((prev) => (prev - 1 + vehicle.images.length) % vehicle.images.length)
  }

  async function handleExportPDF() {
    alert('Génération du PDF en cours...')
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Breadcrumb */}
      <div style={{ marginBottom: '20px', fontSize: '14px', color: '#6a737d' }}>
        <a href="/" style={{ color: '#667eea', textDecoration: 'none' }}>Accueil</a>
        {' > '}
        <span>{vehicle.title}</span>
      </div>

      {/* Header avec actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '24px',
        gap: '20px',
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: 1 }}>
          <h1 style={{ margin: '0 0 12px 0', fontSize: '32px', fontWeight: 700 }}>
            {vehicle.title}
          </h1>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '14px', color: '#6a737d' }}>
              📍 {vehicle.location}
            </span>
            {vehicle.seller_type === 'PRO' && (
              <span style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '4px 12px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: 600
              }}>
                🏢 Professionnel
              </span>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setIsFavorite(!isFavorite)}
            style={{
              padding: '12px 20px',
              background: isFavorite ? '#e91e63' : 'white',
              border: `2px solid ${isFavorite ? '#e91e63' : '#ddd'}`,
              color: isFavorite ? 'white' : '#24292e',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            {isFavorite ? '❤️ Ajouté' : '🤍 Ajouter'}
          </button>

          <button
            onClick={handleExportPDF}
            style={{
              padding: '12px 20px',
              background: 'white',
              border: '2px solid #e1e4e8',
              color: '#24292e',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            📄 Export PDF
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '24px' }}>
        {/* Colonne principale */}
        <div>
          <PhotoGallery
            images={vehicle.images}
            currentIndex={currentImageIndex}
            onPrev={prevImage}
            onNext={nextImage}
            onImageClick={() => setShowLightbox(true)}
          />

          <PriceSection vehicle={vehicle} />

          <Section title="📝 Description">
            <p style={{ lineHeight: 1.8, color: '#24292e', margin: 0 }}>
              {vehicle.description}
            </p>
          </Section>

          <Section title="🔧 Caractéristiques techniques">
            <SpecsGrid specs={vehicle.technical_specs} />
          </Section>

          <Section title="✨ Équipements">
            <FeaturesList features={vehicle.features} />
          </Section>

          <Section title="📊 Historique des prix">
            <PriceHistory history={vehicle.price_history} />
          </Section>

          <Section title="⭐ Avis de nos experts">
            <ExpertOpinion opinion={vehicle.expert_opinion} />
          </Section>

          <Section title="🔍 Véhicules similaires">
            <SimilarVehicles vehicles={vehicle.similar_vehicles} />
          </Section>
        </div>

        {/* Sidebar */}
        <div>
          <ContactCard
            seller={vehicle.seller}
            onContact={() => setShowContactModal(true)}
          />
          <LegalInfo vehicle={vehicle} />
        </div>
      </div>

      {showLightbox && (
        <Lightbox
          images={vehicle.images}
          currentIndex={currentImageIndex}
          onClose={() => setShowLightbox(false)}
          onPrev={prevImage}
          onNext={nextImage}
        />
      )}

      {showContactModal && (
        <ContactModal
          seller={vehicle.seller}
          vehicle={vehicle}
          onClose={() => setShowContactModal(false)}
        />
      )}
    </div>
  )
}

function PhotoGallery({ images, currentIndex, onPrev, onNext, onImageClick }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      overflow: 'hidden',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      marginBottom: '24px'
    }}>
      <div style={{
        position: 'relative',
        height: '500px',
        background: '#f0f0f0',
        cursor: 'zoom-in'
      }}
      onClick={onImageClick}>
        <img
          src={images[currentIndex]}
          alt={`Photo ${currentIndex + 1}`}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain'
          }}
        />

        {images.length > 1 && (
          <>
            <button
              onClick={(e) => { e.stopPropagation(); onPrev(); }}
              style={{
                position: 'absolute',
                left: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'rgba(0,0,0,0.7)',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: '48px',
                height: '48px',
                fontSize: '24px',
                cursor: 'pointer'
              }}
            >
              ‹
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onNext(); }}
              style={{
                position: 'absolute',
                right: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'rgba(0,0,0,0.7)',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: '48px',
                height: '48px',
                fontSize: '24px',
                cursor: 'pointer'
              }}
            >
              ›
            </button>

            <div style={{
              position: 'absolute',
              bottom: '16px',
              right: '16px',
              background: 'rgba(0,0,0,0.7)',
              color: 'white',
              padding: '6px 12px',
              borderRadius: '16px',
              fontSize: '14px',
              fontWeight: 600
            }}>
              {currentIndex + 1} / {images.length}
            </div>
          </>
        )}
      </div>

      {images.length > 1 && (
        <div style={{
          display: 'flex',
          gap: '8px',
          padding: '16px',
          overflowX: 'auto'
        }}>
          {images.map((img, idx) => (
            <div
              key={idx}
              onClick={() => onImageClick(idx)}
              style={{
                width: '80px',
                height: '60px',
                borderRadius: '8px',
                overflow: 'hidden',
                cursor: 'pointer',
                border: idx === currentIndex ? '3px solid #667eea' : '3px solid transparent',
                flexShrink: 0
              }}
            >
              <img
                src={img}
                alt={`Miniature ${idx + 1}`}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function PriceSection({ vehicle }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      marginBottom: '24px'
    }}>
      <div style={{
        fontSize: '40px',
        fontWeight: 700,
        color: '#28a745',
        marginBottom: '20px'
      }}>
        {vehicle.price.toLocaleString()} €
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '16px'
      }}>
        <InfoItem icon="📅" label="Année" value={vehicle.year} />
        <InfoItem icon="🛣️" label="Kilométrage" value={`${vehicle.mileage.toLocaleString()} km`} />
        <InfoItem icon="⛽" label="Carburant" value={vehicle.fuel_type} />
        <InfoItem icon="⚙️" label="Transmission" value={vehicle.transmission} />
        <InfoItem icon="🔢" label="VIN" value={vehicle.vin.slice(0, 10) + '...'} />
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
        fontSize: '16px',
        fontWeight: 600,
        color: '#24292e'
      }}>
        {value}
      </div>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      marginBottom: '24px'
    }}>
      <h2 style={{
        margin: '0 0 20px 0',
        fontSize: '20px',
        fontWeight: 600
      }}>
        {title}
      </h2>
      {children}
    </div>
  )
}

function SpecsGrid({ specs }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '16px'
    }}>
      {Object.entries(specs).map(([key, value]) => (
        <div key={key} style={{
          background: '#f8f9fa',
          padding: '12px',
          borderRadius: '8px'
        }}>
          <div style={{
            fontSize: '12px',
            color: '#6a737d',
            marginBottom: '4px',
            textTransform: 'capitalize'
          }}>
            {key.replace('_', ' ')}
          </div>
          <div style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#24292e'
          }}>
            {value}
          </div>
        </div>
      ))}
    </div>
  )
}

function FeaturesList({ features }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '12px'
    }}>
      {features.map((feature, idx) => (
        <div key={idx} style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '10px',
          background: '#f8f9fa',
          borderRadius: '8px'
        }}>
          <span style={{ fontSize: '18px' }}>✓</span>
          <span style={{ fontSize: '14px', color: '#24292e' }}>{feature}</span>
        </div>
      ))}
    </div>
  )
}

function PriceHistory({ history }) {
  const maxPrice = Math.max(...history.map(h => h.price))
  
  return (
    <div>
      {history.map((entry, idx) => (
        <div key={idx} style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 0',
          borderBottom: idx < history.length - 1 ? '1px solid #e1e4e8' : 'none'
        }}>
          <span style={{ fontSize: '14px', color: '#6a737d' }}>
            {new Date(entry.date).toLocaleDateString('fr-FR')}
          </span>
          <div style={{ flex: 1, margin: '0 20px' }}>
            <div style={{
              height: '8px',
              background: '#e1e4e8',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${(entry.price / maxPrice) * 100}%`,
                height: '100%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                transition: 'width 0.5s ease'
              }} />
            </div>
          </div>
          <span style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#28a745'
          }}>
            {entry.price.toLocaleString()} €
          </span>
        </div>
      ))}
      <div style={{
        marginTop: '12px',
        padding: '12px',
        background: '#d4edda',
        borderRadius: '8px',
        fontSize: '14px',
        color: '#155724'
      }}>
        💰 Baisse de {(history[0].price - history[history.length - 1].price).toLocaleString()} € depuis le début
      </div>
    </div>
  )
}

function ExpertOpinion({ opinion }) {
  return (
    <div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        marginBottom: '20px',
        padding: '16px',
        background: 'linear-gradient(135deg, #fff9e6 0%, #ffe8cc 100%)',
        borderRadius: '12px'
      }}>
        <div style={{
          fontSize: '48px',
          fontWeight: 700,
          color: '#ffc107'
        }}>
          {opinion.score}/10
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontWeight: 600,
            marginBottom: '4px',
            color: '#856404'
          }}>
            Note globale
          </div>
          <div style={{
            height: '8px',
            background: '#fff',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${opinion.score * 10}%`,
              height: '100%',
              background: '#ffc107'
            }} />
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h4 style={{
          margin: '0 0 12px 0',
          fontSize: '16px',
          fontWeight: 600,
          color: '#28a745'
        }}>
          ✓ Points forts
        </h4>
        {opinion.pros.map((pro, idx) => (
          <div key={idx} style={{
            padding: '8px 0',
            fontSize: '14px',
            color: '#24292e'
          }}>
            • {pro}
          </div>
        ))}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h4 style={{
          margin: '0 0 12px 0',
          fontSize: '16px',
          fontWeight: 600,
          color: '#dc3545'
        }}>
          ✗ Points à considérer
        </h4>
        {opinion.cons.map((con, idx) => (
          <div key={idx} style={{
            padding: '8px 0',
            fontSize: '14px',
            color: '#24292e'
          }}>
            • {con}
          </div>
        ))}
      </div>

      <div style={{
        padding: '16px',
        background: '#e7f3ff',
        borderRadius: '8px',
        borderLeft: '4px solid #667eea'
      }}>
        <strong style={{ display: 'block', marginBottom: '8px' }}>
          Verdict de l'expert :
        </strong>
        <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.6 }}>
          {opinion.verdict}
        </p>
      </div>
    </div>
  )
}

function SimilarVehicles({ vehicles }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '16px'
    }}>
      {vehicles.map(v => (
        <a
          key={v.id}
          href={`/vehicle/${v.id}`}
          style={{
            display: 'block',
            background: '#f8f9fa',
            borderRadius: '12px',
            padding: '16px',
            textDecoration: 'none',
            color: 'inherit',
            border: '2px solid transparent',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#667eea'
            e.currentTarget.style.transform = 'translateY(-4px)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'transparent'
            e.currentTarget.style.transform = 'translateY(0)'
          }}
        >
          <div style={{
            fontWeight: 600,
            fontSize: '14px',
            marginBottom: '8px'
          }}>
            {v.title}
          </div>
          <div style={{
            fontSize: '16px',
            fontWeight: 700,
            color: '#28a745',
            marginBottom: '4px'
          }}>
            {v.price.toLocaleString()} €
          </div>
          <div style={{
            fontSize: '12px',
            color: '#6a737d'
          }}>
            {v.year} • {v.mileage.toLocaleString()} km
          </div>
        </a>
      ))}
    </div>
  )
}

function ContactCard({ seller, onContact }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      marginBottom: '24px',
      position: 'sticky',
      top: '20px'
    }}>
      <h3 style={{
        margin: '0 0 16px 0',
        fontSize: '18px',
        fontWeight: 600
      }}>
        {seller.is_pro ? '🏢 Vendeur professionnel' : '👤 Particulier'}
      </h3>

      <div style={{
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #e1e4e8'
      }}>
        <div style={{
          fontWeight: 600,
          marginBottom: '8px',
          fontSize: '16px'
        }}>
          {seller.name}
        </div>
        <div style={{
          fontSize: '14px',
          color: '#6a737d',
          marginBottom: '4px'
        }}>
          📧 {seller.email}
        </div>
        <div style={{
          fontSize: '14px',
          color: '#6a737d'
        }}>
          📞 {seller.phone}
        </div>
      </div>

      <button
        onClick={onContact}
        style={{
          width: '100%',
          padding: '14px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '10px',
          fontSize: '16px',
          fontWeight: 600,
          cursor: 'pointer',
          marginBottom: '12px',
          transition: 'transform 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
        onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
      >
        💬 Contacter le vendeur
      </button>

      <button
        style={{
          width: '100%',
          padding: '14px',
          background: 'white',
          border: '2px solid #e1e4e8',
          color: '#24292e',
          borderRadius: '10px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer'
        }}
      >
        📞 Appeler maintenant
      </button>
    </div>
  )
}

function LegalInfo({ vehicle }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      padding: '20px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      fontSize: '13px',
      color: '#6a737d',
      lineHeight: 1.6
    }}>
      <h4 style={{
        margin: '0 0 12px 0',
        fontSize: '14px',
        fontWeight: 600,
        color: '#24292e'
      }}>
        ℹ️ Informations légales
      </h4>
      <p style={{ margin: '0 0 12px 0' }}>
        <strong>VIN:</strong> {vehicle.vin}
      </p>
      <p style={{ margin: '0 0 12px 0' }}>
        Annonce publiée le {new Date(vehicle.created_at).toLocaleDateString('fr-FR')}
      </p>
      <p style={{ margin: 0 }}>
        Les informations sont fournies par le vendeur et doivent être vérifiées lors de la visite.
      </p>
    </div>
  )
}

function Lightbox({ images, currentIndex, onClose, onPrev, onNext }) {
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.95)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
      onClick={onClose}
    >
      <img
        src={images[currentIndex]}
        alt={`Photo ${currentIndex + 1}`}
        style={{
          maxWidth: '90%',
          maxHeight: '90%',
          objectFit: 'contain'
        }}
        onClick={(e) => e.stopPropagation()}
      />

      <button
        onClick={onClose}
        style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          background: 'rgba(255,255,255,0.2)',
          border: 'none',
          color: 'white',
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          fontSize: '24px',
          cursor: 'pointer',
          transition: 'background 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.3)'}
        onMouseLeave={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
      >
        ✕
      </button>

      {images.length > 1 && (
        <>
          <button
            onClick={(e) => { e.stopPropagation(); onPrev(); }}
            style={{
              position: 'absolute',
              left: '20px',
              background: 'rgba(255,255,255,0.2)',
              border: 'none',
              color: 'white',
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              fontSize: '32px',
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.3)'}
            onMouseLeave={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
          >
            ‹
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onNext(); }}
            style={{
              position: 'absolute',
              right: '20px',
              background: 'rgba(255,255,255,0.2)',
              border: 'none',
              color: 'white',
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              fontSize: '32px',
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.3)'}
            onMouseLeave={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
          >
            ›
          </button>
        </>
      )}
    </div>
  )
}

function ContactModal({ seller, vehicle, onClose }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    // TODO: Envoyer le message au vendeur
    alert('Votre message a été envoyé au vendeur !')
    onClose()
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        zIndex: 10000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '16px',
          padding: '24px',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 2px 12px rgba(0,0,0,0.2)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, fontSize: '24px' }}>Contacter le vendeur</h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '28px',
              cursor: 'pointer',
              color: '#6a737d',
              padding: '0',
              width: '32px',
              height: '32px'
            }}
          >
            ✕
          </button>
        </div>

        <div style={{ marginBottom: '20px', padding: '16px', background: '#f6f8fa', borderRadius: '8px' }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: 600 }}>{seller.name}</p>
          {seller.phone && (
            <p style={{ margin: '4px 0', fontSize: '14px' }}>
              📞 {seller.phone}
            </p>
          )}
          {seller.email && (
            <p style={{ margin: '4px 0', fontSize: '14px' }}>
              ✉️ {seller.email}
            </p>
          )}
        </div>

        <div style={{ marginBottom: '20px', padding: '12px', background: '#f1f8ff', borderRadius: '8px', border: '1px solid #c8e1ff' }}>
          <p style={{ margin: 0, fontSize: '14px', color: '#0366d6' }}>
            <strong>Véhicule concerné :</strong> {vehicle.title}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              Votre message
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Bonjour, je suis intéressé par ce véhicule..."
              required
              rows={6}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '6px',
                border: '1px solid #d1d5db',
                fontSize: '14px',
                fontFamily: 'inherit',
                resize: 'vertical'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '10px 20px',
                background: '#f6f8fa',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500
              }}
            >
              Annuler
            </button>
            <button
              type="submit"
              style={{
                padding: '10px 20px',
                background: '#0366d6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500
              }}
            >
              Envoyer le message
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}