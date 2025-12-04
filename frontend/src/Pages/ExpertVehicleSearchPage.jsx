import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AdvancedSearchForm from '../components/AdvancedSearchForm';
import EnrichedResults from '../ui/Results';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ExpertVehicleSearchPage() {
  const { requestId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [searchStats, setSearchStats] = useState(null);
  const [error, setError] = useState(null);
  const [proposing, setProposing] = useState({});
  const [initialFilters, setInitialFilters] = useState(null);

  const token = localStorage.getItem('token') || localStorage.getItem('access_token');

  useEffect(() => {
    fetchRequest();
  }, [requestId]);

  const fetchRequest = async () => {
    try {
      const response = await fetch(`${API_URL}/api/assisted/requests/${requestId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Erreur chargement demande');
      const data = await response.json();
      setRequest(data);

      // Pré-remplir les filtres avec les critères de la demande
      const filters = {
        sources: ['leboncoin', 'autoscout24']
      };

      // Budget
      if (data.budget_max) {
        filters.price_max = data.budget_max.toString();
      }

      // Carburant
      if (data.preferred_fuel_type && data.preferred_fuel_type !== 'null') {
        filters.fuel_type = data.preferred_fuel_type;
      }

      // Transmission
      if (data.preferred_transmission && data.preferred_transmission !== 'null') {
        filters.transmission = data.preferred_transmission;
      }

      // Kilométrage
      if (data.max_mileage) {
        filters.mileage_max = data.max_mileage.toString();
      }

      // Année
      if (data.min_year) {
        filters.year_min = data.min_year.toString();
      }

      setInitialFilters(filters);
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors du chargement de la demande');
    }
  };

  // Fonction pour générer un ID stable basé sur l'URL du véhicule
  const generateVehicleId = (url, source) => {
    // Assurer que source a une valeur par défaut
    const safeSource = source || 'scraping';

    if (!url) {
      // Fallback: générer un UUID aléatoire
      return `${safeSource}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Créer un hash simple de l'URL pour un ID stable
    let hash = 0;
    for (let i = 0; i < url.length; i++) {
      const char = url.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }

    // Combiner source et hash pour un ID unique
    return `${safeSource}_${Math.abs(hash).toString(36)}`;
  };

  const handleSearch = async (filters) => {
    setLoading(true);
    setError(null);
    setResults([]);
    setSearchStats(null);

    console.log(' Recherche avec filtres:', filters);

    try {
      const response = await fetch(`${API_URL}/api/search-advanced/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...filters,
          max_pages: 20
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();

      console.log(' Résultats reçus:', data);

      // Générer des IDs stables pour les véhicules qui n'en ont pas
      const vehiclesWithIds = (data.results || []).map(vehicle => ({
        ...vehicle,
        id: vehicle.id || generateVehicleId(vehicle.url, vehicle.source)
      }));

      setResults(vehiclesWithIds);
      setSearchStats({
        total: data.total_results,
        duration: data.duration,
        sources: data.sources_stats,
        filters: data.filters_applied
      });

    } catch (err) {
      console.error('❌ Erreur recherche:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProposeVehicle = async (vehicle) => {
    setProposing(prev => ({ ...prev, [vehicle.id]: true }));

    try {
      const response = await fetch(`${API_URL}/api/assisted/requests/${requestId}/propose`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vehicle_id: vehicle.id,
          vehicle_data: {
            title: vehicle.title,
            make: vehicle.make,
            model: vehicle.model,
            price: vehicle.price,
            year: vehicle.year,
            mileage: vehicle.mileage,
            fuel_type: vehicle.fuel_type,
            transmission: vehicle.transmission,
            description: vehicle.description,
            url: vehicle.url,
            image_url: vehicle.images,
            location_city: vehicle.location_city,
            location_lat: vehicle.location_lat,
            location_lon: vehicle.location_lon,
            original_id: vehicle.original_id,
            source: vehicle.source
          },
          message: `Ce véhicule correspond parfaitement à vos critères de recherche. ${vehicle.title} - ${vehicle.price}€`
        }),
      });

      if (!response.ok) throw new Error('Erreur proposition');

      alert(' Véhicule proposé au client avec succès !');

      // Marquer visuellement comme proposé
      setResults(prev => prev.map(v =>
        v.id === vehicle.id ? { ...v, proposed: true } : v
      ));
    } catch (error) {
      console.error('Erreur:', error);
      alert('❌ Erreur lors de la proposition du véhicule');
    } finally {
      setProposing(prev => ({ ...prev, [vehicle.id]: false }));
    }
  };

  if (!request || !initialFilters) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '80vh'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
          <p style={{ color: 'var(--text-secondary)' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: 'var(--gray-50)', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: 'var(--space-8)' }}>
        {/* Header */}
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <button
            onClick={() => navigate(`/expert/requests/${requestId}`)}
            style={{
              background: 'var(--white)',
              border: '1px solid #EEEEEE',
              padding: '8px 16px',
                            cursor: 'pointer',
              marginBottom: 'var(--space-4)',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--text-primary)';
              e.currentTarget.style.background = 'var(--gray-50)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-light)';
              e.currentTarget.style.background = 'var(--white)';
            }}
          >
            ← Retour à la demande
          </button>

          <h1 style={{
            fontSize: 'var(--space-8)',
            fontWeight: 700,
            color: 'var(--text-primary)',
            margin: '0 0 8px 0'
          }}>
            Recherche de véhicules
          </h1>
          <p style={{
            fontSize: 'var(--space-4)',
            color: 'var(--text-secondary)',
            margin: 0
          }}>
            Recherchez et proposez des véhicules pour <strong>{request.client?.full_name || request.client?.email}</strong>
          </p>
        </div>

        {/* Critères du client */}
        <div style={{
          background: 'var(--white)',
          padding: 'var(--space-5)',
                    marginBottom: 'var(--space-6)',
          border: '1px solid #EEEEEE',
          boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
        }}>
          <div style={{
            fontSize: 'var(--space-3)',
            fontWeight: 600,
            marginBottom: 'var(--space-3)',
            color: 'var(--text-primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Critères du client
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            {request.budget_max && (
              <span style={{
                background: 'var(--gray-50)',
                padding: '6px 12px',
                                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                 Budget max : {request.budget_max.toLocaleString()} €
              </span>
            )}
            {request.preferred_fuel_type && request.preferred_fuel_type !== 'null' && (
              <span style={{
                background: 'var(--gray-50)',
                padding: '6px 12px',
                                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                 Carburant : {request.preferred_fuel_type}
              </span>
            )}
            {request.preferred_transmission && request.preferred_transmission !== 'null' && (
              <span style={{
                background: 'var(--gray-50)',
                padding: '6px 12px',
                                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                 Transmission : {request.preferred_transmission}
              </span>
            )}
            {request.max_mileage && (
              <span style={{
                background: 'var(--gray-50)',
                padding: '6px 12px',
                                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                 Km max : {request.max_mileage.toLocaleString()} km
              </span>
            )}
            {request.min_year && (
              <span style={{
                background: 'var(--gray-50)',
                padding: '6px 12px',
                                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                 Année min : {request.min_year}
              </span>
            )}
          </div>
          {request.description && (
            <div style={{ marginTop: 'var(--space-3)', paddingTop: 'var(--space-3)', borderTop: '1px solid #EEEEEE' }}>
              <div style={{
                fontSize: 'var(--space-3)',
                fontWeight: 600,
                marginBottom: '6px',
                color: 'var(--text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Description du besoin
              </div>
              <p style={{
                margin: 0,
                fontSize: '14px',
                color: 'var(--text-secondary)',
                lineHeight: 1.6
              }}>
                {request.description}
              </p>
            </div>
          )}
        </div>

        {/* Formulaire de recherche */}
        <div style={{
          background: 'var(--white)',
          padding: 'var(--space-6)',
                    marginBottom: 'var(--space-6)',
          border: '1px solid #EEEEEE',
          boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
        }}>
          <AdvancedSearchForm
            onSearch={handleSearch}
            loading={loading}
            initialFilters={initialFilters}
          />
        </div>

        {/* Statistiques de recherche */}
        {searchStats && (
          <div style={{
            background: 'var(--white)',
            padding: 'var(--space-5)',
                        marginBottom: 'var(--space-6)',
            border: '1px solid #EEEEEE',
            boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 'var(--space-4)'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: 600,
                color: 'var(--text-primary)',
                margin: 0
              }}>
                {searchStats.total} résultat{searchStats.total > 1 ? 's' : ''} trouvé{searchStats.total > 1 ? 's' : ''}
              </h3>
              <span style={{
                fontSize: '13px',
                color: 'var(--text-secondary)'
              }}>
                 {searchStats.duration.toFixed(2)}s
              </span>
            </div>

            <div style={{
              display: 'flex',
              gap: 'var(--space-4)',
              marginBottom: 'var(--space-3)'
            }}>
              {Object.entries(searchStats.sources).map(([source, stats]) => (
                <div key={source} style={{
                  flex: 1,
                  padding: 'var(--space-3)',
                  background: 'var(--gray-50)',
                                    border: '1px solid #EEEEEE'
                }}>
                  <div style={{
                    fontSize: 'var(--space-3)',
                    color: 'var(--text-secondary)',
                    marginBottom: 'var(--space-1)',
                    textTransform: 'uppercase',
                    fontWeight: 600,
                    letterSpacing: '0.5px'
                  }}>
                    {source === 'leboncoin' ? 'LeBonCoin' : 'AutoScout24'}
                  </div>
                  <div style={{
                    fontSize: 'var(--space-4)',
                    fontWeight: 600,
                    color: stats.success ? 'var(--text-primary)' : 'var(--red-accent)'
                  }}>
                    {stats.success ? `${stats.count} annonces` : `Erreur`}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Erreur */}
        {error && (
          <div style={{
            background: 'var(--white)',
            padding: 'var(--space-5)',
                        marginBottom: 'var(--space-6)',
            border: '2px solid #DC2626'
          }}>
            <h3 style={{ color: 'var(--red-accent)', margin: '0 0 8px 0' }}>❌ Erreur</h3>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{error}</p>
          </div>
        )}

        {/* Résultats avec bouton de proposition */}
        {!loading && !error && results.length > 0 && (
          <div>
            <EnrichedResults
              loading={loading}
              results={results}
              total={results.length}
              showProposeButton={true}
              onPropose={handleProposeVehicle}
              proposing={proposing}
              requestId={requestId}
            />
          </div>
        )}

        {/* État vide */}
        {!loading && !error && results.length === 0 && searchStats && (
          <div style={{
            background: 'var(--white)',
            padding: '60px 20px',
                        textAlign: 'center',
            border: '1px solid #EEEEEE'
          }}>
            <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
            <h3 style={{ color: 'var(--text-primary)', margin: '0 0 8px 0' }}>Aucun véhicule trouvé</h3>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Essayez de modifier les critères de recherche</p>
          </div>
        )}
      </div>
    </div>
  );
}
