import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import useSWR from 'swr';
import {
  getAvailableRequests,
  acceptRequest,
  completeRequest,
  getExpertStats
} from '../services/assisted';

export default function ExpertDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Charger les données
  const { data: stats } = useSWR('/assisted/expert/stats', getExpertStats);

  // Vérifier accès expert
  if (!user || user.role !== 'EXPERT') {
    return (
      <div style={{
        padding: '60px 20px',
        textAlign: 'center',
        maxWidth: '600px',
        margin: '0 auto',
      }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: 600,
          color: '#222222',
          marginBottom: '12px',
        }}>Accès réservé aux experts</h2>
        <p style={{
          color: '#666666',
          marginBottom: '24px',
        }}>Cette page est uniquement accessible aux comptes experts.</p>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '12px 24px',
            background: '#DC2626',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Retour à l'accueil
        </button>
      </div>
    );
  }

  const totalRequests = stats?.total_requests || 0;
  const pendingRequests = stats?.pending_requests || 0;
  const completedRequests = stats?.completed_requests || 0;
  const acceptedProposals = stats?.accepted_proposals || 0;
  const totalProposals = stats?.total_proposals || 1;

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          color: '#222222',
          margin: '0 0 8px 0',
        }}>
          Dashboard Expert
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#666666',
          margin: 0,
        }}>
          Aidez les clients à trouver leur véhicule idéal
        </p>
      </div>

      {/* Statistiques */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '16px',
        marginBottom: '32px',
      }}>
        <StatCard
          icon="📋"
          label="Demandes traitées"
          value={totalRequests}
          color="#222222"
        />
        <StatCard
          icon="⏳"
          label="En cours"
          value={pendingRequests}
          subtext={`${totalRequests > 0 ? Math.round((pendingRequests / totalRequests) * 100) : 0}% du total`}
          color="#DC2626"
        />
        <StatCard
          icon="✅"
          label="Terminées"
          value={completedRequests}
          subtext={`Taux: ${totalRequests > 0 ? Math.round((completedRequests / totalRequests) * 100) : 0}%`}
          color="#222222"
        />
        <StatCard
          icon="💚"
          label="Taux d'acceptation"
          value={`${Math.round((acceptedProposals / totalProposals) * 100)}%`}
          subtext={`${acceptedProposals}/${totalProposals} véhicules`}
          color="#666666"
        />
      </div>

      {/* Quick Actions */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '16px',
      }}>
        <ActionCard
          icon="🏪"
          title="Marché des demandes"
          description="Acceptez de nouvelles demandes de clients"
          onClick={() => navigate('/expert/market')}
        />
        <ActionCard
          icon="📋"
          title="Mes missions"
          description="Gérez vos demandes en cours"
          onClick={() => navigate('/expert/missions')}
        />
        <ActionCard
          icon="🔍"
          title="Rechercher véhicules"
          description="Trouvez des véhicules pour vos clients"
          onClick={() => navigate('/expert/search')}
        />
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, subtext, color }) {
  return (
    <div style={{
      background: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
    }}>
      <div style={{ fontSize: '32px', lineHeight: 1 }}>{icon}</div>
      <div>
        <div style={{
          fontSize: '12px',
          color: '#666666',
          marginBottom: '4px',
          textTransform: 'uppercase',
          fontWeight: 600,
          letterSpacing: '0.5px',
        }}>
          {label}
        </div>
        <div style={{
          fontSize: '24px',
          fontWeight: 700,
          color: color,
        }}>{value}</div>
        {subtext && (
          <div style={{
            fontSize: '12px',
            color: '#999999',
            marginTop: '4px',
          }}>{subtext}</div>
        )}
      </div>
    </div>
  );
}

function ActionCard({ icon, title, description, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'white',
        padding: '24px',
        borderRadius: '12px',
        border: '1px solid #EEEEEE',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
        cursor: 'pointer',
        transition: 'all 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)';
        e.currentTarget.style.borderColor = '#222222';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)';
        e.currentTarget.style.borderColor = '#EEEEEE';
      }}
    >
      <div style={{
        fontSize: '32px',
        marginBottom: '12px',
      }}>{icon}</div>
      <h3 style={{
        fontSize: '18px',
        fontWeight: 600,
        color: '#222222',
        margin: '0 0 8px 0',
      }}>{title}</h3>
      <p style={{
        fontSize: '14px',
        color: '#666666',
        margin: 0,
        lineHeight: 1.5,
      }}>{description}</p>
    </div>
  );
}
