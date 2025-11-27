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

  const handleSearch = async (filters) => {
    setLoading(true);
    setError(null);
    setResults([]);
    setSearchStats(null);

    console.log('🔍 Recherche avec filtres:', filters);

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

      console.log('✅ Résultats reçus:', data);

      setResults(data.results || []);
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
            price: vehicle.price,
            year: vehicle.year,
            mileage: vehicle.mileage,
            fuel_type: vehicle.fuel_type,
            transmission: vehicle.transmission,
            url: vehicle.url,
            image_url: vehicle.images?.[0] || null,
            source: vehicle.source
          },
          message: `Ce véhicule correspond parfaitement à vos critères de recherche. ${vehicle.title} - ${vehicle.price}€`
        }),
      });

      if (!response.ok) throw new Error('Erreur proposition');

      alert('✅ Véhicule proposé au client avec succès !');

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
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <p style={{ color: '#666666' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#FAFAFA', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '32px' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <button
            onClick={() => navigate(`/expert/requests/${requestId}`)}
            style={{
              background: 'white',
              border: '1px solid #EEEEEE',
              padding: '8px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              marginBottom: '16px',
              color: '#222222',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#222222';
              e.currentTarget.style.background = '#FAFAFA';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#EEEEEE';
              e.currentTarget.style.background = 'white';
            }}
          >
            ← Retour à la demande
          </button>

          <h1 style={{
            fontSize: '32px',
            fontWeight: 700,
            color: '#222222',
            margin: '0 0 8px 0'
          }}>
            Recherche de véhicules
          </h1>
          <p style={{
            fontSize: '16px',
            color: '#666666',
            margin: 0
          }}>
            Recherchez et proposez des véhicules pour <strong>{request.client?.full_name || request.client?.email}</strong>
          </p>
        </div>

        {/* Critères du client */}
        <div style={{
          background: 'white',
          padding: '20px',
          borderRadius: '12px',
          marginBottom: '24px',
          border: '1px solid #EEEEEE',
          boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 600,
            marginBottom: '12px',
            color: '#222222',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Critères du client
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {request.budget_max && (
              <span style={{
                background: '#FAFAFA',
                padding: '6px 12px',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                💰 Budget max : {request.budget_max.toLocaleString()} €
              </span>
            )}
            {request.preferred_fuel_type && request.preferred_fuel_type !== 'null' && (
              <span style={{
                background: '#FAFAFA',
                padding: '6px 12px',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                ⛽ Carburant : {request.preferred_fuel_type}
              </span>
            )}
            {request.preferred_transmission && request.preferred_transmission !== 'null' && (
              <span style={{
                background: '#FAFAFA',
                padding: '6px 12px',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                ⚙️ Transmission : {request.preferred_transmission}
              </span>
            )}
            {request.max_mileage && (
              <span style={{
                background: '#FAFAFA',
                padding: '6px 12px',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                🛣️ Km max : {request.max_mileage.toLocaleString()} km
              </span>
            )}
            {request.min_year && (
              <span style={{
                background: '#FAFAFA',
                padding: '6px 12px',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 500,
                border: '1px solid #EEEEEE'
              }}>
                📅 Année min : {request.min_year}
              </span>
            )}
          </div>
          {request.description && (
            <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #EEEEEE' }}>
              <div style={{
                fontSize: '12px',
                fontWeight: 600,
                marginBottom: '6px',
                color: '#222222',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Description du besoin
              </div>
              <p style={{
                margin: 0,
                fontSize: '14px',
                color: '#666666',
                lineHeight: 1.6
              }}>
                {request.description}
              </p>
            </div>
          )}
        </div>

        {/* Formulaire de recherche */}
        <div style={{
          background: 'white',
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '24px',
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
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            marginBottom: '24px',
            border: '1px solid #EEEEEE',
            boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: 600,
                color: '#222222',
                margin: 0
              }}>
                {searchStats.total} résultat{searchStats.total > 1 ? 's' : ''} trouvé{searchStats.total > 1 ? 's' : ''}
              </h3>
              <span style={{
                fontSize: '13px',
                color: '#666666'
              }}>
                ⏱️ {searchStats.duration.toFixed(2)}s
              </span>
            </div>

            <div style={{
              display: 'flex',
              gap: '16px',
              marginBottom: '12px'
            }}>
              {Object.entries(searchStats.sources).map(([source, stats]) => (
                <div key={source} style={{
                  flex: 1,
                  padding: '12px',
                  background: '#FAFAFA',
                  borderRadius: '8px',
                  border: '1px solid #EEEEEE'
                }}>
                  <div style={{
                    fontSize: '12px',
                    color: '#666666',
                    marginBottom: '4px',
                    textTransform: 'uppercase',
                    fontWeight: 600,
                    letterSpacing: '0.5px'
                  }}>
                    {source === 'leboncoin' ? 'LeBonCoin' : 'AutoScout24'}
                  </div>
                  <div style={{
                    fontSize: '16px',
                    fontWeight: 600,
                    color: stats.success ? '#222222' : '#DC2626'
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
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            marginBottom: '24px',
            border: '2px solid #DC2626'
          }}>
            <h3 style={{ color: '#DC2626', margin: '0 0 8px 0' }}>❌ Erreur</h3>
            <p style={{ color: '#666666', margin: 0 }}>{error}</p>
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
            background: 'white',
            padding: '60px 20px',
            borderRadius: '12px',
            textAlign: 'center',
            border: '1px solid #EEEEEE'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <h3 style={{ color: '#222222', margin: '0 0 8px 0' }}>Aucun véhicule trouvé</h3>
            <p style={{ color: '#666666', margin: 0 }}>Essayez de modifier les critères de recherche</p>
          </div>
        )}
      </div>
    </div>
  );
}
