import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ExpertVehicleSearchPage() {
  const { requestId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [request, setRequest] = useState(null);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [proposing, setProposing] = useState({});

  const token = localStorage.getItem('token') || localStorage.getItem('access_token');

  useEffect(() => {
    fetchRequest();
    performSearch();
  }, [requestId]);

  const fetchRequest = async () => {
    try {
      const response = await fetch(`${API_URL}/api/assisted/requests/${requestId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Erreur chargement demande');
      const data = await response.json();
      setRequest(data);
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors du chargement de la demande');
    }
  };

  const performSearch = async (customQuery = null) => {
    setLoading(true);
    try {
      // Construire les filtres à partir des critères de la demande
      const filters = {};

      // Récupérer les critères depuis les searchParams (passés depuis la page précédente)
      const budgetMax = searchParams.get('budget_max');
      const fuelType = searchParams.get('fuel_type');
      const transmission = searchParams.get('transmission');
      const maxMileage = searchParams.get('max_mileage');
      const minYear = searchParams.get('min_year');

      if (budgetMax) filters.price_max = parseInt(budgetMax);
      if (fuelType && fuelType !== 'null') filters.fuel_type = fuelType;
      if (transmission && transmission !== 'null') filters.transmission = transmission;
      if (maxMileage) filters.mileage_max = parseInt(maxMileage);
      if (minYear) filters.year_min = parseInt(minYear);

      const response = await fetch(`${API_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          q: customQuery || searchQuery || null,
          filters: filters,
          page: 1,
          size: 50,
        }),
      });

      if (!response.ok) throw new Error('Erreur recherche');
      const data = await response.json();

      // Extraire les véhicules des résultats Elasticsearch
      const vehiclesList = data.hits ? data.hits.map(hit => ({
        id: hit.id,
        ...hit.source
      })) : [];

      setVehicles(vehiclesList);
    } catch (error) {
      console.error('Erreur recherche:', error);
      alert('Erreur lors de la recherche de véhicules');
    } finally {
      setLoading(false);
    }
  };

  const handleProposeVehicle = async (vehicleId) => {
    setProposing(prev => ({ ...prev, [vehicleId]: true }));

    try {
      const response = await fetch(`${API_URL}/api/assisted/requests/${requestId}/propose`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vehicle_id: vehicleId,
          message: 'Ce véhicule correspond à vos critères de recherche.',
        }),
      });

      if (!response.ok) throw new Error('Erreur proposition');

      alert('✅ Véhicule proposé au client avec succès !');

      // Marquer visuellement comme proposé
      setVehicles(prev => prev.map(v =>
        v.id === vehicleId ? { ...v, proposed: true } : v
      ));
    } catch (error) {
      console.error('Erreur:', error);
      alert('❌ Erreur lors de la proposition du véhicule');
    } finally {
      setProposing(prev => ({ ...prev, [vehicleId]: false }));
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    performSearch(searchQuery);
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{ marginBottom: '30px' }}>
        <button
          onClick={() => navigate(`/expert/requests/${requestId}`)}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '8px 16px',
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: '16px',
          }}
        >
          ← Retour à la demande
        </button>

        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
          🔍 Recherche de véhicules
        </h1>
        <p style={{ color: '#6a737d', fontSize: '14px' }}>
          Proposez des véhicules correspondant aux critères du client
        </p>
      </div>

      {/* Critères de recherche appliqués */}
      {request && (
        <div style={{
          background: '#e7f3ff',
          padding: '16px',
          borderRadius: '12px',
          marginBottom: '24px',
        }}>
          <div style={{ fontWeight: 600, marginBottom: '12px', color: '#0366d6' }}>
            📋 Critères du client appliqués :
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {searchParams.get('budget_max') && (
              <span style={{
                background: 'white',
                padding: '6px 12px',
                borderRadius: '16px',
                fontSize: '13px',
                fontWeight: 500,
              }}>
                💰 Budget max : {parseInt(searchParams.get('budget_max')).toLocaleString()} €
              </span>
            )}
            {searchParams.get('fuel_type') && searchParams.get('fuel_type') !== 'null' && (
              <span style={{
                background: 'white',
                padding: '6px 12px',
                borderRadius: '16px',
                fontSize: '13px',
                fontWeight: 500,
              }}>
                ⛽ Carburant : {searchParams.get('fuel_type')}
              </span>
            )}
            {searchParams.get('transmission') && searchParams.get('transmission') !== 'null' && (
              <span style={{
                background: 'white',
                padding: '6px 12px',
                borderRadius: '16px',
                fontSize: '13px',
                fontWeight: 500,
              }}>
                ⚙️ Transmission : {searchParams.get('transmission')}
              </span>
            )}
            {searchParams.get('max_mileage') && (
              <span style={{
                background: 'white',
                padding: '6px 12px',
                borderRadius: '16px',
                fontSize: '13px',
                fontWeight: 500,
              }}>
                🛣️ Km max : {parseInt(searchParams.get('max_mileage')).toLocaleString()} km
              </span>
            )}
            {searchParams.get('min_year') && (
              <span style={{
                background: 'white',
                padding: '6px 12px',
                borderRadius: '16px',
                fontSize: '13px',
                fontWeight: 500,
              }}>
                📅 Année min : {searchParams.get('min_year')}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Barre de recherche */}
      <form onSubmit={handleSearchSubmit} style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            placeholder="Rechercher par marque, modèle..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '2px solid #e1e4e8',
              borderRadius: '8px',
              fontSize: '15px',
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '12px 24px',
              background: loading ? '#CCCCCC' : '#DC2626',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.background = '#B91C1C';
            }}
            onMouseLeave={(e) => {
              if (!loading) e.currentTarget.style.background = '#DC2626';
            }}
          >
            {loading ? 'Recherche...' : 'Rechercher'}
          </button>
        </div>
      </form>

      {/* Résultats */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#6a737d' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <p>Recherche en cours...</p>
        </div>
      ) : vehicles.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#6a737d' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
          <p>Aucun véhicule trouvé avec ces critères</p>
          <p style={{ fontSize: '13px' }}>Essayez de modifier votre recherche</p>
        </div>
      ) : (
        <div>
          <div style={{
            marginBottom: '16px',
            fontSize: '14px',
            color: '#6a737d',
            fontWeight: 600,
          }}>
            {vehicles.length} véhicule{vehicles.length > 1 ? 's' : ''} trouvé{vehicles.length > 1 ? 's' : ''}
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '20px',
          }}>
            {vehicles.map((vehicle) => (
              <VehicleCard
                key={vehicle.id}
                vehicle={vehicle}
                onPropose={() => handleProposeVehicle(vehicle.id)}
                proposing={proposing[vehicle.id]}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function VehicleCard({ vehicle, onPropose, proposing }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      overflow: 'hidden',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      border: vehicle.proposed ? '2px solid #28a745' : '2px solid transparent',
      transition: 'all 0.2s',
    }}>
      {/* Image */}
      {vehicle.images && vehicle.images.length > 0 ? (
        <div style={{
          height: '200px',
          background: `url(${vehicle.images[0]})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }} />
      ) : (
        <div style={{
          height: '200px',
          background: '#FAFAFA',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '48px',
          color: '#CCCCCC',
        }}>
          🚗
        </div>
      )}

      {/* Content */}
      <div style={{ padding: '16px' }}>
        <h3 style={{
          margin: '0 0 12px 0',
          fontSize: '16px',
          fontWeight: 600,
          color: '#24292e',
        }}>
          {vehicle.title}
        </h3>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '8px',
          marginBottom: '16px',
          fontSize: '13px',
          color: '#6a737d',
        }}>
          {vehicle.price && (
            <div>💰 {vehicle.price.toLocaleString()} €</div>
          )}
          {vehicle.year && (
            <div>📅 {vehicle.year}</div>
          )}
          {vehicle.mileage && (
            <div>🛣️ {vehicle.mileage.toLocaleString()} km</div>
          )}
          {vehicle.fuel_type && (
            <div>⛽ {vehicle.fuel_type}</div>
          )}
        </div>

        {vehicle.description && (
          <p style={{
            margin: '0 0 16px 0',
            fontSize: '13px',
            color: '#6a737d',
            lineHeight: 1.5,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}>
            {vehicle.description}
          </p>
        )}

        <button
          onClick={onPropose}
          disabled={proposing || vehicle.proposed}
          style={{
            width: '100%',
            padding: '12px',
            background: vehicle.proposed
              ? '#222222'
              : proposing
                ? '#CCCCCC'
                : '#DC2626',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: (proposing || vehicle.proposed) ? 'not-allowed' : 'pointer',
            transition: 'background 0.2s',
          }}
          onMouseEnter={(e) => {
            if (!proposing && !vehicle.proposed) {
              e.currentTarget.style.background = '#B91C1C';
            }
          }}
          onMouseLeave={(e) => {
            if (!proposing && !vehicle.proposed) {
              e.currentTarget.style.background = '#DC2626';
            }
          }}
        >
          {vehicle.proposed
            ? 'Déjà proposé'
            : proposing
              ? 'Envoi...'
              : 'Envoyer au client'}
        </button>
      </div>
    </div>
  );
}
