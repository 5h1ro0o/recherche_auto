import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

// Simulation de données - remplacer par de vrais appels API (FALLBACK si API échoue)
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
  const { id: vehicleId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  // Use vehicle data from navigation state if available
  const vehicleFromState = location.state?.vehicle

  const [vehicle, setVehicle] = useState(vehicleFromState || null)
  const [loading, setLoading] = useState(!vehicleFromState)
  const [error, setError] = useState(null)

  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [showLightbox, setShowLightbox] = useState(false)
  const [showContactModal, setShowContactModal] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)

  // Charger les données du véhicule depuis l'API si pas déjà disponible
  useEffect(() => {
    // Skip if we already have vehicle data from navigation state
    if (vehicleFromState) {
      return
    }

    async function loadVehicle() {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(`${API_BASE}/vehicles/${vehicleId}`)

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Véhicule introuvable')
          }
          throw new Error('Erreur lors du chargement du véhicule')
        }

        const data = await response.json()

        // S'assurer que les images sont un tableau
        if (!data.images || !Array.isArray(data.images) || data.images.length === 0) {
          data.images = []  // Fallback sur tableau vide si pas d'images
        }

        // Ajouter les données manquantes pour l'interface (optionnel)
        if (!data.features) data.features = []
        if (!data.technical_specs) data.technical_specs = {}
        if (!data.seller) data.seller = { name: 'Vendeur', is_pro: false }

        setVehicle(data)
      } catch (err) {
        console.error('Erreur chargement véhicule:', err)
        setError(err.message)
        // Fallback sur mockData en cas d'erreur (pour le développement)
        setVehicle(mockVehicleData)
      } finally {
        setLoading(false)
      }
    }

    if (vehicleId) {
      loadVehicle()
    }
  }, [vehicleId, vehicleFromState])

  function nextImage() {
    if (!vehicle || !vehicle.images || vehicle.images.length === 0) return
    setCurrentImageIndex((prev) => (prev + 1) % vehicle.images.length)
  }

  function prevImage() {
    if (!vehicle || !vehicle.images || vehicle.images.length === 0) return
    setCurrentImageIndex((prev) => (prev - 1 + vehicle.images.length) % vehicle.images.length)
  }

  async function handleExportPDF() {
    alert('Génération du PDF en cours...')
  }

  // État de chargement
  if (loading) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '80px 20px', textAlign: 'center' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
        <p style={{ color: '#666666', fontSize: '18px' }}>Chargement du véhicule...</p>
      </div>
    )
  }

  // État d'erreur (avec fallback sur mockData)
  if (error && !vehicle) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '80px 20px', textAlign: 'center' }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>⚠️</div>
        <h3 style={{ fontSize: '24px', color: '#222222', marginBottom: '12px' }}>
          {error}
        </h3>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '12px 24px',
            background: '#DC2626',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 600,
            cursor: 'pointer',
            marginTop: '20px'
          }}
        >
          Retour à l'accueil
        </button>
      </div>
    )
  }

  // Vérifier que vehicle existe et a des images
  if (!vehicle) {
    return null
  }

  // S'assurer que vehicle.images est un tableau
  const images = Array.isArray(vehicle.images) && vehicle.images.length > 0
    ? vehicle.images
    : ['https://via.placeholder.com/800x600/EEEEEE/222222?text=Pas+d\'image']

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Breadcrumb */}
      <div style={{ marginBottom: '20px', fontSize: '14px', color: '#666666' }}>
        <a href="/" style={{ color: '#DC2626', textDecoration: 'none' }}>Accueil</a>
        {' > '}
        <span>{vehicle.title || 'Véhicule'}</span>
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
            <span style={{ fontSize: '14px', color: '#666666' }}>
              📍 {vehicle.location}
            </span>
            {vehicle.seller_type === 'PRO' && (
              <span style={{
                background: '#DC2626',
                color: 'white',
                padding: '4px 12px',
                borderRadius: '4px',
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
              background: isFavorite ? '#DC2626' : 'white',
              border: `1px solid ${isFavorite ? '#DC2626' : '#EEEEEE'}`,
              color: isFavorite ? 'white' : '#222222',
              borderRadius: '8px',
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
              border: '1px solid #EEEEEE',
              color: '#222222',
              borderRadius: '8px',
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
            images={images}
            currentIndex={currentImageIndex}
            onPrev={prevImage}
            onNext={nextImage}
            onImageClick={() => setShowLightbox(true)}
          />

          <PriceSection vehicle={vehicle} />

          <Section title="📝 Description">
            <p style={{ lineHeight: 1.8, color: '#222222', margin: 0 }}>
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
          images={images}
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
      borderRadius: '12px',
      overflow: 'hidden',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
      marginBottom: '24px'
    }}>
      <div style={{
        position: 'relative',
        height: '500px',
        background: '#FAFAFA',
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
                border: idx === currentIndex ? '2px solid #DC2626' : '2px solid #EEEEEE',
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
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
      marginBottom: '24px'
    }}>
      <div style={{
        fontSize: '40px',
        fontWeight: 700,
        color: '#222222',
        marginBottom: '20px'
      }}>
        {vehicle.price ? vehicle.price.toLocaleString() : 'Prix non disponible'} €
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '16px'
      }}>
        {vehicle.year && <InfoItem icon="📅" label="Année" value={vehicle.year} />}
        {vehicle.mileage && <InfoItem icon="🛣️" label="Kilométrage" value={`${vehicle.mileage.toLocaleString()} km`} />}
        {vehicle.fuel_type && <InfoItem icon="⛽" label="Carburant" value={vehicle.fuel_type} />}
        {vehicle.transmission && <InfoItem icon="⚙️" label="Transmission" value={vehicle.transmission} />}
        {vehicle.vin && <InfoItem icon="🔢" label="VIN" value={vehicle.vin.slice(0, 10) + '...'} />}
      </div>
    </div>
  )
}

function InfoItem({ icon, label, value }) {
  return (
    <div>
      <div style={{
        fontSize: '12px',
        color: '#666666',
        marginBottom: '4px',
        fontWeight: 500
      }}>
        {icon} {label}
      </div>
      <div style={{
        fontSize: '16px',
        fontWeight: 600,
        color: '#222222'
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
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
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
  if (!specs || Object.keys(specs).length === 0) {
    return <p style={{ color: '#666666' }}>Informations techniques non disponibles</p>
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '16px'
    }}>
      {Object.entries(specs).map(([key, value]) => (
        <div key={key} style={{
          background: '#FAFAFA',
          padding: '12px',
          borderRadius: '8px',
          border: '1px solid #EEEEEE'
        }}>
          <div style={{
            fontSize: '12px',
            color: '#666666',
            marginBottom: '4px',
            textTransform: 'capitalize'
          }}>
            {key.replace('_', ' ')}
          </div>
          <div style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#222222'
          }}>
            {value}
          </div>
        </div>
      ))}
    </div>
  )
}

function FeaturesList({ features }) {
  if (!features || features.length === 0) {
    return <p style={{ color: '#666666' }}>Équipements non disponibles</p>
  }

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
          background: '#FAFAFA',
          borderRadius: '8px',
          border: '1px solid #EEEEEE'
        }}>
          <span style={{ fontSize: '18px' }}>✓</span>
          <span style={{ fontSize: '14px', color: '#222222' }}>{feature}</span>
        </div>
      ))}
    </div>
  )
}

function PriceHistory({ history }) {
  if (!history || history.length === 0) {
    return <p style={{ color: '#666666' }}>Historique des prix non disponible</p>
  }

  const maxPrice = Math.max(...history.map(h => h.price))

  return (
    <div>
      {history.map((entry, idx) => (
        <div key={idx} style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 0',
          borderBottom: idx < history.length - 1 ? '1px solid #EEEEEE' : 'none'
        }}>
          <span style={{ fontSize: '14px', color: '#666666' }}>
            {new Date(entry.date).toLocaleDateString('fr-FR')}
          </span>
          <div style={{ flex: 1, margin: '0 20px' }}>
            <div style={{
              height: '8px',
              background: '#EEEEEE',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${(entry.price / maxPrice) * 100}%`,
                height: '100%',
                background: '#DC2626',
                transition: 'width 0.5s ease'
              }} />
            </div>
          </div>
          <span style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#222222'
          }}>
            {entry.price.toLocaleString()} €
          </span>
        </div>
      ))}
      <div style={{
        marginTop: '12px',
        padding: '12px',
        background: '#FAFAFA',
        borderRadius: '8px',
        border: '1px solid #EEEEEE',
        fontSize: '14px',
        color: '#222222'
      }}>
        💰 Baisse de {(history[0].price - history[history.length - 1].price).toLocaleString()} € depuis le début
      </div>
    </div>
  )
}

function ExpertOpinion({ opinion }) {
  if (!opinion) {
    return <p style={{ color: '#666666' }}>Avis expert non disponible</p>
  }

  return (
    <div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        marginBottom: '20px',
        padding: '16px',
        background: '#FAFAFA',
        borderRadius: '8px',
        border: '1px solid #EEEEEE'
      }}>
        <div style={{
          fontSize: '48px',
          fontWeight: 700,
          color: '#222222'
        }}>
          {opinion.score}/10
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontWeight: 600,
            marginBottom: '4px',
            color: '#222222'
          }}>
            Note globale
          </div>
          <div style={{
            height: '8px',
            background: '#EEEEEE',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${opinion.score * 10}%`,
              height: '100%',
              background: '#DC2626'
            }} />
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h4 style={{
          margin: '0 0 12px 0',
          fontSize: '16px',
          fontWeight: 600,
          color: '#222222'
        }}>
          ✓ Points forts
        </h4>
        {opinion.pros.map((pro, idx) => (
          <div key={idx} style={{
            padding: '8px 0',
            fontSize: '14px',
            color: '#222222'
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
          color: '#222222'
        }}>
          ✗ Points à considérer
        </h4>
        {opinion.cons.map((con, idx) => (
          <div key={idx} style={{
            padding: '8px 0',
            fontSize: '14px',
            color: '#666666'
          }}>
            • {con}
          </div>
        ))}
      </div>

      <div style={{
        padding: '16px',
        background: '#FAFAFA',
        borderRadius: '8px',
        border: '1px solid #EEEEEE',
        borderLeft: '4px solid #DC2626'
      }}>
        <strong style={{ display: 'block', marginBottom: '8px', color: '#222222' }}>
          Verdict de l'expert :
        </strong>
        <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.6, color: '#666666' }}>
          {opinion.verdict}
        </p>
      </div>
    </div>
  )
}

function SimilarVehicles({ vehicles }) {
  if (!vehicles || vehicles.length === 0) {
    return <p style={{ color: '#666666' }}>Véhicules similaires non disponibles</p>
  }

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
            background: '#FAFAFA',
            borderRadius: '8px',
            padding: '16px',
            textDecoration: 'none',
            color: 'inherit',
            border: '1px solid #EEEEEE',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#DC2626'
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#EEEEEE'
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <div style={{
            fontWeight: 600,
            fontSize: '14px',
            marginBottom: '8px',
            color: '#222222'
          }}>
            {v.title}
          </div>
          <div style={{
            fontSize: '16px',
            fontWeight: 700,
            color: '#222222',
            marginBottom: '4px'
          }}>
            {v.price.toLocaleString()} €
          </div>
          <div style={{
            fontSize: '12px',
            color: '#666666'
          }}>
            {v.year} • {v.mileage.toLocaleString()} km
          </div>
        </a>
      ))}
    </div>
  )
}

function ContactCard({ seller, onContact }) {
  if (!seller) {
    return null
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
      marginBottom: '24px',
      position: 'sticky',
      top: '20px'
    }}>
      <h3 style={{
        margin: '0 0 16px 0',
        fontSize: '18px',
        fontWeight: 600,
        color: '#222222'
      }}>
        {seller.is_pro ? '🏢 Vendeur professionnel' : '👤 Particulier'}
      </h3>

      <div style={{
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #EEEEEE'
      }}>
        <div style={{
          fontWeight: 600,
          marginBottom: '8px',
          fontSize: '16px',
          color: '#222222'
        }}>
          {seller.name || 'Vendeur'}
        </div>
        {seller.email && (
          <div style={{
            fontSize: '14px',
            color: '#666666',
            marginBottom: '4px'
          }}>
            📧 {seller.email}
          </div>
        )}
        {seller.phone && (
          <div style={{
            fontSize: '14px',
            color: '#666666'
          }}>
            📞 {seller.phone}
          </div>
        )}
      </div>

      <button
        onClick={onContact}
        style={{
          width: '100%',
          padding: '14px',
          background: '#DC2626',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '16px',
          fontWeight: 600,
          cursor: 'pointer',
          marginBottom: '12px',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          e.target.style.background = '#B91C1C'
          e.target.style.transform = 'translateY(-2px)'
        }}
        onMouseLeave={(e) => {
          e.target.style.background = '#DC2626'
          e.target.style.transform = 'translateY(0)'
        }}
      >
        💬 Contacter le vendeur
      </button>

      <button
        style={{
          width: '100%',
          padding: '14px',
          background: 'white',
          border: '1px solid #EEEEEE',
          color: '#222222',
          borderRadius: '8px',
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
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
      fontSize: '13px',
      color: '#666666',
      lineHeight: 1.6
    }}>
      <h4 style={{
        margin: '0 0 12px 0',
        fontSize: '14px',
        fontWeight: 600,
        color: '#222222'
      }}>
        ℹ️ Informations légales
      </h4>
      <p style={{ margin: '0 0 12px 0' }}>
        <strong style={{ color: '#222222' }}>VIN:</strong> {vehicle.vin}
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
          borderRadius: '12px',
          padding: '24px',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
          border: '1px solid #EEEEEE'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, fontSize: '24px', color: '#222222' }}>Contacter le vendeur</h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '28px',
              cursor: 'pointer',
              color: '#666666',
              padding: '0',
              width: '32px',
              height: '32px'
            }}
          >
            ✕
          </button>
        </div>

        <div style={{ marginBottom: '20px', padding: '16px', background: '#FAFAFA', borderRadius: '8px', border: '1px solid #EEEEEE' }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: '#222222' }}>{seller.name}</p>
          {seller.phone && (
            <p style={{ margin: '4px 0', fontSize: '14px', color: '#666666' }}>
              📞 {seller.phone}
            </p>
          )}
          {seller.email && (
            <p style={{ margin: '4px 0', fontSize: '14px', color: '#666666' }}>
              ✉️ {seller.email}
            </p>
          )}
        </div>

        <div style={{ marginBottom: '20px', padding: '12px', background: '#FAFAFA', borderRadius: '8px', border: '1px solid #EEEEEE' }}>
          <p style={{ margin: 0, fontSize: '14px', color: '#222222' }}>
            <strong>Véhicule concerné :</strong> {vehicle.title}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#222222' }}>
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
                borderRadius: '8px',
                border: '1px solid #EEEEEE',
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
                background: 'white',
                border: '1px solid #EEEEEE',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500,
                color: '#222222'
              }}
            >
              Annuler
            </button>
            <button
              type="submit"
              style={{
                padding: '10px 20px',
                background: '#DC2626',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
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