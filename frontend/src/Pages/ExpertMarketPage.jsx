import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import useSWR from 'swr';
import { getAvailableRequests, acceptRequest } from '../services/assisted';

export default function ExpertMarketPage() {
  const navigate = useNavigate();
  const [budgetFilter, setBudgetFilter] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [searchTerm, setSearchTerm] = useState('');

  const { data: requests, mutate } = useSWR(
    ['/assisted/market', 'PENDING'],
    () => getAvailableRequests('PENDING')
  );

  const filteredAndSortedRequests = useMemo(() => {
    if (!requests) return [];

    let filtered = [...requests];

    // Filtre par budget
    if (budgetFilter) {
      const maxBudget = parseInt(budgetFilter);
      filtered = filtered.filter(r => !r.budget_max || r.budget_max <= maxBudget);
    }

    // Filtre par recherche texte
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(r =>
        r.description?.toLowerCase().includes(term) ||
        r.preferred_fuel_type?.toLowerCase().includes(term)
      );
    }

    // Tri
    switch (sortBy) {
      case 'urgent':
        filtered.sort((a, b) => {
          const ageA = Date.now() - new Date(a.created_at).getTime();
          const ageB = Date.now() - new Date(b.created_at).getTime();
          return ageB - ageA;
        });
        break;

      case 'budget':
        filtered.sort((a, b) => (b.budget_max || 0) - (a.budget_max || 0));
        break;

      default: // 'recent'
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    return filtered;
  }, [requests, budgetFilter, sortBy, searchTerm]);

  const handleAccept = async (requestId) => {
    try {
      await acceptRequest(requestId);
      mutate();
      alert(' Demande acceptée avec succès !');
      navigate(`/expert/requests/${requestId}`);
    } catch (error) {
      console.error('Erreur:', error);
      alert('❌ Erreur lors de l\'acceptation de la demande');
    }
  };

  const isUrgent = (createdAt) => {
    const age = Date.now() - new Date(createdAt).getTime();
    return age > 48 * 60 * 60 * 1000; // 48 heures
  };

  return (
    <div style={{ padding: 'var(--space-8)' }}>
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-8)' }}>
        <h1 style={{
          fontSize: 'var(--space-8)',
          fontWeight: 700,
          color: '#24292e',
          margin: '0 0 8px 0',
        }}>
          🏪 Marché des demandes
        </h1>
        <p style={{
          fontSize: 'var(--space-4)',
          color: '#6a737d',
          margin: 0,
        }}>
          Acceptez des demandes de clients et proposez-leur des véhicules adaptés
        </p>
      </div>

      {/* Filters */}
      <div style={{
        background: 'var(--white)',
        padding: 'var(--space-5)',
                marginBottom: 'var(--space-6)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        display: 'flex',
        gap: 'var(--space-3)',
        flexWrap: 'wrap',
      }}>
        <input
          type="text"
          placeholder=" Rechercher dans les descriptions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: '1 1 300px',
            padding: '12px 16px',
            border: '2px solid #e1e4e8',
                        fontSize: '14px',
          }}
        />

        <select
          value={budgetFilter}
          onChange={(e) => setBudgetFilter(e.target.value)}
          style={{
            padding: '12px 16px',
            border: '2px solid #e1e4e8',
                        fontSize: '14px',
            cursor: 'pointer',
          }}
        >
          <option value=""> Tous les budgets</option>
          <option value="10000">≤ 10 000 €</option>
          <option value="15000">≤ 15 000 €</option>
          <option value="20000">≤ 20 000 €</option>
          <option value="30000">≤ 30 000 €</option>
          <option value="50000">≤ 50 000 €</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{
            padding: '12px 16px',
            border: '2px solid #e1e4e8',
                        fontSize: '14px',
            cursor: 'pointer',
          }}
        >
          <option value="recent"> Plus récentes</option>
          <option value="urgent">🚨 Plus urgentes (48h)</option>
          <option value="budget">💵 Budget décroissant</option>
        </select>

        {(searchTerm || budgetFilter || sortBy !== 'recent') && (
          <button
            onClick={() => {
              setSearchTerm('');
              setBudgetFilter('');
              setSortBy('recent');
            }}
            style={{
              padding: '12px 16px',
              background: '#f6f8fa',
              border: '2px solid #e1e4e8',
                            fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              color: '#586069',
            }}
          >
             Réinitialiser
          </button>
        )}
      </div>

      {/* Stats Bar */}
      {requests && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-6)',
        }}>
          <StatCard
            icon="📋"
            label="Demandes disponibles"
            value={filteredAndSortedRequests.length}
            color="var(--text-primary)"
          />
          <StatCard
            icon="🚨"
            label="Demandes urgentes"
            value={filteredAndSortedRequests.filter(r => isUrgent(r.created_at)).length}
            color="var(--red-accent)"
          />
          <StatCard
            icon=""
            label="Budget moyen"
            value={
              filteredAndSortedRequests.length > 0
                ? Math.round(
                    filteredAndSortedRequests.reduce((sum, r) => sum + (r.budget_max || 0), 0) /
                    filteredAndSortedRequests.filter(r => r.budget_max).length
                  ).toLocaleString() + ' €'
                : 'N/A'
            }
            color="var(--text-secondary)"
          />
        </div>
      )}

      {/* Requests Grid */}
      {!requests ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: 'var(--white)',
                  }}>
          <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
          <p style={{ color: '#6a737d' }}>Chargement des demandes...</p>
        </div>
      ) : filteredAndSortedRequests.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: 'var(--white)',
                  }}>
          <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
          <h3 style={{ margin: '0 0 8px 0' }}>Aucune demande disponible</h3>
          <p style={{ color: '#6a737d', margin: 0 }}>
            {searchTerm || budgetFilter
              ? 'Essayez de modifier vos filtres'
              : 'Revenez plus tard pour voir les nouvelles demandes'}
          </p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
          gap: 'var(--space-5)',
        }}>
          {filteredAndSortedRequests.map((request) => (
            <RequestCard
              key={request.id}
              request={request}
              onAccept={() => handleAccept(request.id)}
              isUrgent={isUrgent(request.created_at)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div style={{
      background: 'var(--white)',
      padding: 'var(--space-5)',
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-4)',
    }}>
      <div style={{
        fontSize: 'var(--space-8)',
        lineHeight: 1,
      }}>{icon}</div>
      <div>
        <div style={{
          fontSize: 'var(--space-3)',
          color: '#6a737d',
          marginBottom: 'var(--space-1)',
          textTransform: 'uppercase',
          fontWeight: 600,
          letterSpacing: '0.5px',
        }}>
          {label}
        </div>
        <div style={{
          fontSize: 'var(--space-6)',
          fontWeight: 700,
          color: color,
        }}>{value}</div>
      </div>
    </div>
  );
}

function RequestCard({ request, onAccept, isUrgent }) {
  const age = Math.floor((Date.now() - new Date(request.created_at).getTime()) / (1000 * 60 * 60));

  return (
    <div style={{
      background: 'var(--white)',
            padding: 'var(--space-6)',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: isUrgent ? '2px solid #DC2626' : '1px solid #EEEEEE',
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
        marginBottom: 'var(--space-4)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'var(--red-accent)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--white)',
            fontSize: 'var(--space-4)',
            fontWeight: 600,
          }}>
            {request.client?.full_name?.[0] || request.client?.email?.[0] || '?'}
          </div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#24292e' }}>
              {request.client?.full_name || request.client?.email}
            </div>
            <div style={{ fontSize: 'var(--space-3)', color: '#6a737d' }}>
              Il y a {age}h
            </div>
          </div>
        </div>

        {isUrgent && (
          <span style={{
            background: 'var(--red-accent)',
            color: 'var(--white)',
            padding: '4px 8px',
                        fontSize: '11px',
            fontWeight: 600,
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
          }}>
            Urgent
          </span>
        )}
      </div>

      {/* Description */}
      <div style={{
        background: '#f6f8fa',
        padding: 'var(--space-3)',
                marginBottom: 'var(--space-4)',
      }}>
        <p style={{
          margin: 0,
          fontSize: '14px',
          lineHeight: 1.6,
          color: '#24292e',
        }}>
          {request.description}
        </p>
      </div>

      {/* Criteria Tags */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 'var(--space-2)',
        marginBottom: 'var(--space-4)',
      }}>
        {request.budget_max && (
          <Tag icon="" label={`${request.budget_max.toLocaleString()} €`} />
        )}
        {request.preferred_fuel_type && (
          <Tag icon="" label={request.preferred_fuel_type} />
        )}
        {request.preferred_transmission && (
          <Tag icon="" label={request.preferred_transmission} />
        )}
        {request.max_mileage && (
          <Tag icon="" label={`${request.max_mileage.toLocaleString()} km`} />
        )}
        {request.min_year && (
          <Tag icon="" label={`${request.min_year}`} />
        )}
      </div>

      {/* Action Button */}
      <button
        onClick={onAccept}
        style={{
          width: '100%',
          padding: '14px',
          background: 'var(--red-accent)',
          color: 'var(--white)',
          border: 'none',
                    fontSize: '15px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'background 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'var(--red-accent)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'var(--red-accent)';
        }}
      >
        Accepter cette demande
      </button>
    </div>
  );
}

function Tag({ icon, label }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--space-1)',
      background: 'var(--white)',
      border: '1px solid #e1e4e8',
      padding: '4px 10px',
            fontSize: '13px',
      fontWeight: 500,
      color: '#24292e',
    }}>
      <span>{icon}</span>
      <span>{label}</span>
    </span>
  );
}
