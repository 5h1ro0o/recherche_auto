import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const ExpertRequestsPage = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('PENDING');
  const navigate = useNavigate();

  const token = localStorage.getItem('token') || localStorage.getItem('access_token');
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const url = `${API_URL}/api/assisted/requests${filter ? `?status_filter=${filter}` : ''}`;
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des demandes');
      }

      const data = await response.json();
      setRequests(data);
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors du chargement des demandes');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      PENDING: { label: 'En attente', color: '#666666' },
      IN_PROGRESS: { label: 'En cours', color: '#DC2626' },
      COMPLETED: { label: 'Terminée', color: '#222222' },
      CANCELLED: { label: 'Annulée', color: '#999999' },
    };
    const { label, color } = statusMap[status] || { label: status, color: '#666666' };
    return (
      <span style={{
        background: color,
        color: 'white',
        padding: '4px 10px',
        borderRadius: '4px',
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.5px',
        textTransform: 'uppercase'
      }}>
        {label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div style={{ padding: '32px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          color: '#222222',
          margin: '0 0 8px 0',
        }}>
          Demandes de recherche personnalisée
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#666666',
          margin: 0,
        }}>
          Gérez les demandes des clients et proposez-leur des véhicules
        </p>
      </div>

      {/* Filtres */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '24px',
        flexWrap: 'wrap'
      }}>
        <FilterButton
          label="En attente"
          active={filter === 'PENDING'}
          onClick={() => setFilter('PENDING')}
        />
        <FilterButton
          label="En cours"
          active={filter === 'IN_PROGRESS'}
          onClick={() => setFilter('IN_PROGRESS')}
        />
        <FilterButton
          label="Terminées"
          active={filter === 'COMPLETED'}
          onClick={() => setFilter('COMPLETED')}
        />
        <FilterButton
          label="Toutes"
          active={filter === ''}
          onClick={() => setFilter('')}
        />
      </div>

      {/* Liste des demandes */}
      {loading ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <p style={{ color: '#666666' }}>Chargement des demandes...</p>
        </div>
      ) : requests.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: '#FAFAFA',
          borderRadius: '12px',
          border: '1px solid #EEEEEE'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
          <p style={{ color: '#666666', fontSize: '16px' }}>Aucune demande trouvée</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '20px',
        }}>
          {requests.map((request) => (
            <RequestCard
              key={request.id}
              request={request}
              onViewDetails={() => navigate(`/expert/requests/${request.id}`)}
              getStatusBadge={getStatusBadge}
              formatDate={formatDate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

function FilterButton({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '12px 20px',
        background: active ? '#DC2626' : 'white',
        color: active ? 'white' : '#222222',
        border: active ? 'none' : '1px solid #EEEEEE',
        borderRadius: '8px',
        fontSize: '14px',
        fontWeight: 600,
        cursor: 'pointer',
        transition: 'all 0.2s',
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = '#222222';
          e.currentTarget.style.background = '#FAFAFA';
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = '#EEEEEE';
          e.currentTarget.style.background = 'white';
        }
      }}
    >
      {label}
    </button>
  );
}

function RequestCard({ request, onViewDetails, getStatusBadge, formatDate }) {
  return (
    <div
      onClick={onViewDetails}
      style={{
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
        border: '1px solid #EEEEEE',
        padding: '24px',
        cursor: 'pointer',
        transition: 'all 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)';
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '16px',
      }}>
        {getStatusBadge(request.status)}
        <span style={{
          fontSize: '12px',
          color: '#999999',
        }}>
          {formatDate(request.created_at)}
        </span>
      </div>

      {/* Title */}
      <h3 style={{
        fontSize: '18px',
        fontWeight: 600,
        color: '#222222',
        margin: '0 0 12px 0',
      }}>
        Demande de recherche
      </h3>

      {/* Description */}
      <p style={{
        fontSize: '14px',
        color: '#666666',
        lineHeight: 1.6,
        marginBottom: '16px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        display: '-webkit-box',
        WebkitLineClamp: 3,
        WebkitBoxOrient: 'vertical',
      }}>
        {request.description}
      </p>

      {/* Criteria */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        marginBottom: '16px',
        fontSize: '13px',
      }}>
        {request.budget_max && (
          <div style={{ color: '#666666' }}>
            <span style={{ fontWeight: 600, color: '#222222' }}>Budget max:</span> {request.budget_max.toLocaleString()} €
          </div>
        )}
        {request.preferred_fuel_type && (
          <div style={{ color: '#666666' }}>
            <span style={{ fontWeight: 600, color: '#222222' }}>Carburant:</span> {request.preferred_fuel_type}
          </div>
        )}
        {request.max_mileage && (
          <div style={{ color: '#666666' }}>
            <span style={{ fontWeight: 600, color: '#222222' }}>Kilométrage max:</span> {request.max_mileage.toLocaleString()} km
          </div>
        )}
        {request.min_year && (
          <div style={{ color: '#666666' }}>
            <span style={{ fontWeight: 600, color: '#222222' }}>Année min:</span> {request.min_year}
          </div>
        )}
      </div>

      {/* Action Button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onViewDetails();
        }}
        style={{
          width: '100%',
          padding: '12px',
          background: '#DC2626',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'background 0.2s',
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = '#B91C1C'}
        onMouseLeave={(e) => e.currentTarget.style.background = '#DC2626'}
      >
        {request.status === 'PENDING' ? 'Accepter la demande' : 'Voir les détails'}
      </button>
    </div>
  );
}

export default ExpertRequestsPage;
