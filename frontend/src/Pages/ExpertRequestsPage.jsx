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
      PENDING: { label: 'En attente', color: 'var(--gray-700)' },
      IN_PROGRESS: { label: 'En cours', color: '#D97706' },
      COMPLETED: { label: 'Terminée', color: '#059669' },
      CANCELLED: { label: 'Annulée', color: 'var(--red-accent)' },
    };
    const { label, color } = statusMap[status] || { label: status, color: 'var(--gray-700)' };
    return (
      <span style={{
        background: color,
        color: 'var(--white)',
        padding: 'var(--space-1) var(--space-3)',
        fontSize: '11px',
        fontWeight: 'var(--font-weight-semibold)',
        letterSpacing: '0.05em',
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
    <div className="app-main">
      <div style={{ maxWidth: 'var(--container-2xl)', margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          background: 'var(--white)',
          padding: 'var(--space-8)',
          marginBottom: 'var(--space-8)',
          border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-gloss-md)',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Gloss overlay */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '100px',
            background: 'var(--gloss-overlay)',
            pointerEvents: 'none'
          }} />

          <h1 style={{
            fontSize: '32px',
            fontWeight: 'var(--font-weight-bold)',
            color: 'var(--text-primary)',
            margin: '0 0 var(--space-2) 0',
            letterSpacing: '-0.02em',
            position: 'relative',
            zIndex: 1
          }}>
            Demandes de recherche personnalisée
          </h1>
          <p style={{
            fontSize: '16px',
            color: 'var(--text-secondary)',
            margin: 0,
            fontWeight: 'var(--font-weight-medium)',
            position: 'relative',
            zIndex: 1
          }}>
            Gérez les demandes des clients et proposez-leur des véhicules
          </p>
        </div>

        {/* Filtres */}
        <div style={{
          display: 'flex',
          gap: 'var(--space-2)',
          marginBottom: 'var(--space-6)',
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
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p style={{ marginTop: 'var(--space-4)', color: 'var(--text-secondary)' }}>
              Chargement des demandes...
            </p>
          </div>
        ) : requests.length === 0 ? (
          <div className="card">
            <div className="empty-state">
              <p>Aucune demande trouvée</p>
            </div>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: 'var(--space-5)',
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
    </div>
  );
};

function FilterButton({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: 'var(--space-3) var(--space-5)',
        background: active ? 'var(--red-accent)' : 'var(--white)',
        color: active ? 'var(--white)' : 'var(--text-primary)',
        border: active ? 'none' : '1px solid var(--border-light)',
        fontSize: '14px',
        fontWeight: 'var(--font-weight-semibold)',
        cursor: 'pointer',
        transition: 'all var(--transition-base)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = 'var(--border-medium)';
          e.currentTarget.style.background = 'var(--gray-50)';
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = 'var(--border-light)';
          e.currentTarget.style.background = 'var(--white)';
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
        background: 'var(--white)',
        boxShadow: 'var(--shadow-gloss-sm)',
        border: '1px solid var(--border-light)',
        padding: 'var(--space-6)',
        cursor: 'pointer',
        transition: 'all var(--transition-base)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = 'var(--shadow-gloss-lg)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.borderColor = 'var(--border-medium)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'var(--shadow-gloss-sm)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.borderColor = 'var(--border-light)';
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 'var(--space-4)',
      }}>
        {getStatusBadge(request.status)}
        <span style={{
          fontSize: '12px',
          color: 'var(--text-muted)',
          fontWeight: 'var(--font-weight-medium)'
        }}>
          {formatDate(request.created_at)}
        </span>
      </div>

      {/* Title */}
      <h3 style={{
        fontSize: '18px',
        fontWeight: 'var(--font-weight-semibold)',
        color: 'var(--text-primary)',
        margin: '0 0 var(--space-3) 0',
        letterSpacing: '-0.01em'
      }}>
        Demande de recherche
      </h3>

      {/* Description */}
      <p style={{
        fontSize: '14px',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
        marginBottom: 'var(--space-4)',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        display: '-webkit-box',
        WebkitLineClamp: 3,
        WebkitBoxOrient: 'vertical',
        fontWeight: 'var(--font-weight-regular)'
      }}>
        {request.description}
      </p>

      {/* Criteria */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-2)',
        marginBottom: 'var(--space-4)',
        fontSize: '13px',
        fontWeight: 'var(--font-weight-medium)'
      }}>
        {request.budget_max && (
          <div style={{ color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 'var(--font-weight-semibold)', color: 'var(--text-primary)' }}>Budget max:</span> {request.budget_max.toLocaleString()} €
          </div>
        )}
        {request.preferred_fuel_type && (
          <div style={{ color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 'var(--font-weight-semibold)', color: 'var(--text-primary)' }}>Carburant:</span> {request.preferred_fuel_type}
          </div>
        )}
        {request.max_mileage && (
          <div style={{ color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 'var(--font-weight-semibold)', color: 'var(--text-primary)' }}>Kilométrage max:</span> {request.max_mileage.toLocaleString()} km
          </div>
        )}
        {request.min_year && (
          <div style={{ color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 'var(--font-weight-semibold)', color: 'var(--text-primary)' }}>Année min:</span> {request.min_year}
          </div>
        )}
      </div>

      {/* Action Button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onViewDetails();
        }}
        className="btn btn-primary"
        style={{
          width: '100%',
          padding: 'var(--space-3)',
          fontSize: '14px',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}
      >
        {request.status === 'PENDING' ? 'Accepter la demande' : 'Voir les détails'}
      </button>
    </div>
  );
}

export default ExpertRequestsPage;
