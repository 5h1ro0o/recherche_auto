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
  const inProgressRequests = stats?.in_progress_requests || 0;
  const completedRequests = stats?.completed_requests || 0;
  const acceptedProposals = stats?.accepted_proposals || 0;
  const totalProposals = stats?.total_proposals || 1;
  const rejectedProposals = stats?.rejected_proposals || 0;
  const pendingProposals = totalProposals - acceptedProposals - rejectedProposals;

  // Calculs de pourcentages
  const completionRate = totalRequests > 0 ? Math.round((completedRequests / totalRequests) * 100) : 0;
  const acceptanceRate = totalProposals > 0 ? Math.round((acceptedProposals / totalProposals) * 100) : 0;
  const inProgressRate = totalRequests > 0 ? Math.round((inProgressRequests / totalRequests) * 100) : 0;

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
          ⭐ Dashboard Expert
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#666666',
          margin: 0,
        }}>
          Bienvenue {user?.full_name || user?.email} - Vue d'ensemble de votre activité
        </p>
      </div>

      {/* Statistiques principales avec graphiques */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '32px',
      }}>
        <KPICard
          icon="📋"
          label="Total demandes"
          value={totalRequests}
          color="#4F46E5"
          trend="+12%"
        />
        <KPICard
          icon="🔄"
          label="En cours"
          value={inProgressRequests}
          percentage={inProgressRate}
          color="#F59E0B"
        />
        <KPICard
          icon="✅"
          label="Terminées"
          value={completedRequests}
          percentage={completionRate}
          color="#10B981"
        />
        <KPICard
          icon="💚"
          label="Taux succès"
          value={`${acceptanceRate}%`}
          color="#8B5CF6"
        />
      </div>

      {/* Section graphiques */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '24px',
        marginBottom: '32px',
      }}>
        {/* Graphique des demandes */}
        <div style={{
          background: 'white',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #EEEEEE',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#222222',
            marginBottom: '20px',
          }}>📊 Répartition des demandes</h3>

          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
            <PieChart
              data={[
                { value: completedRequests, color: '#10B981', label: 'Terminées' },
                { value: inProgressRequests, color: '#F59E0B', label: 'En cours' },
                { value: pendingRequests, color: '#EF4444', label: 'En attente' },
              ]}
              size={180}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <LegendItem color="#10B981" label="Terminées" value={completedRequests} total={totalRequests} />
            <LegendItem color="#F59E0B" label="En cours" value={inProgressRequests} total={totalRequests} />
            <LegendItem color="#EF4444" label="En attente" value={pendingRequests} total={totalRequests} />
          </div>
        </div>

        {/* Graphique des propositions */}
        <div style={{
          background: 'white',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #EEEEEE',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#222222',
            marginBottom: '20px',
          }}>🚗 Statut des propositions</h3>

          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
            <PieChart
              data={[
                { value: acceptedProposals, color: '#10B981', label: 'Acceptées' },
                { value: pendingProposals, color: '#6B7280', label: 'En attente' },
                { value: rejectedProposals, color: '#EF4444', label: 'Refusées' },
              ]}
              size={180}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <LegendItem color="#10B981" label="Acceptées" value={acceptedProposals} total={totalProposals} />
            <LegendItem color="#6B7280" label="En attente" value={pendingProposals} total={totalProposals} />
            <LegendItem color="#EF4444" label="Refusées" value={rejectedProposals} total={totalProposals} />
          </div>
        </div>

        {/* Métriques de performance */}
        <div style={{
          background: 'white',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #EEEEEE',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#222222',
            marginBottom: '20px',
          }}>📈 Métriques de performance</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <ProgressBar
              label="Taux de complétion"
              percentage={completionRate}
              color="#10B981"
            />
            <ProgressBar
              label="Taux d'acceptation"
              percentage={acceptanceRate}
              color="#8B5CF6"
            />
            <ProgressBar
              label="Demandes actives"
              percentage={inProgressRate}
              color="#F59E0B"
            />
          </div>

          <div style={{
            marginTop: '20px',
            padding: '12px',
            background: '#F9FAFB',
            borderRadius: '8px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>
              Performance globale
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: '#4F46E5' }}>
              {Math.round((completionRate + acceptanceRate) / 2)}%
            </div>
          </div>
        </div>
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
          count={pendingRequests}
          onClick={() => navigate('/expert/market')}
        />
        <ActionCard
          icon="📋"
          title="Mes missions"
          description="Gérez vos demandes en cours"
          count={inProgressRequests}
          onClick={() => navigate('/expert/missions')}
        />
        <ActionCard
          icon="💬"
          title="Messagerie"
          description="Communiquez avec vos clients"
          onClick={() => navigate('/messages')}
        />
      </div>
    </div>
  );
}

// Composants de graphiques

function PieChart({ data, size = 150 }) {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  if (total === 0) {
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: '#E5E7EB',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '14px',
        color: '#6B7280',
      }}>
        Aucune donnée
      </div>
    );
  }

  let currentAngle = 0;
  const segments = data.map((item, index) => {
    const percentage = (item.value / total) * 100;
    const angle = (item.value / total) * 360;
    const startAngle = currentAngle;
    currentAngle += angle;

    return { ...item, percentage, startAngle, angle };
  });

  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 200 200">
        {segments.map((segment, index) => {
          if (segment.value === 0) return null;

          const radius = 80;
          const centerX = 100;
          const centerY = 100;

          const startAngle = segment.startAngle - 90; // Start from top
          const endAngle = startAngle + segment.angle;

          const startRad = (startAngle * Math.PI) / 180;
          const endRad = (endAngle * Math.PI) / 180;

          const x1 = centerX + radius * Math.cos(startRad);
          const y1 = centerY + radius * Math.sin(startRad);
          const x2 = centerX + radius * Math.cos(endRad);
          const y2 = centerY + radius * Math.sin(endRad);

          const largeArc = segment.angle > 180 ? 1 : 0;

          const pathData = [
            `M ${centerX} ${centerY}`,
            `L ${x1} ${y1}`,
            `A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`,
            'Z'
          ].join(' ');

          return (
            <path
              key={index}
              d={pathData}
              fill={segment.color}
              stroke="white"
              strokeWidth="2"
            />
          );
        })}

        {/* Center circle for donut effect */}
        <circle cx="100" cy="100" r="45" fill="white" />

        {/* Center text */}
        <text
          x="100"
          y="95"
          textAnchor="middle"
          style={{
            fontSize: '24px',
            fontWeight: 700,
            fill: '#222222',
          }}
        >
          {total}
        </text>
        <text
          x="100"
          y="112"
          textAnchor="middle"
          style={{
            fontSize: '12px',
            fill: '#6B7280',
          }}
        >
          Total
        </text>
      </svg>
    </div>
  );
}

function LegendItem({ color, label, value, total }) {
  const percentage = total > 0 ? Math.round((value / total) * 100) : 0;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '8px',
      borderRadius: '6px',
      background: '#F9FAFB',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          width: '12px',
          height: '12px',
          borderRadius: '3px',
          background: color,
        }} />
        <span style={{ fontSize: '14px', color: '#374151' }}>{label}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '14px', fontWeight: 600, color: '#222222' }}>
          {value}
        </span>
        <span style={{ fontSize: '12px', color: '#6B7280' }}>
          ({percentage}%)
        </span>
      </div>
    </div>
  );
}

function ProgressBar({ label, percentage, color }) {
  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: '8px',
      }}>
        <span style={{ fontSize: '14px', color: '#374151' }}>{label}</span>
        <span style={{ fontSize: '14px', fontWeight: 600, color: '#222222' }}>
          {percentage}%
        </span>
      </div>
      <div style={{
        height: '8px',
        background: '#E5E7EB',
        borderRadius: '4px',
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${percentage}%`,
          height: '100%',
          background: color,
          borderRadius: '4px',
          transition: 'width 0.3s ease',
        }} />
      </div>
    </div>
  );
}

function KPICard({ icon, label, value, percentage, color, trend }) {
  return (
    <div style={{
      background: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      border: '1px solid #EEEEEE',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '4px',
        height: '100%',
        background: color,
      }} />

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '12px',
            color: '#6B7280',
            marginBottom: '8px',
            textTransform: 'uppercase',
            fontWeight: 600,
            letterSpacing: '0.5px',
          }}>
            {label}
          </div>
          <div style={{
            fontSize: '28px',
            fontWeight: 700,
            color: color,
            marginBottom: '4px',
          }}>{value}</div>
          {percentage !== undefined && (
            <div style={{ fontSize: '13px', color: '#6B7280' }}>
              {percentage}% du total
            </div>
          )}
          {trend && (
            <div style={{
              fontSize: '13px',
              color: '#10B981',
              fontWeight: 600,
              marginTop: '4px',
            }}>
              {trend} ce mois
            </div>
          )}
        </div>
        <div style={{
          fontSize: '32px',
          opacity: 0.3,
        }}>{icon}</div>
      </div>
    </div>
  );
}

function ActionCard({ icon, title, description, count, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'white',
        padding: '24px',
        borderRadius: '12px',
        border: '2px solid #EEEEEE',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        cursor: 'pointer',
        transition: 'all 0.2s',
        position: 'relative',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
        e.currentTarget.style.borderColor = '#4F46E5';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        e.currentTarget.style.borderColor = '#EEEEEE';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      {count !== undefined && count > 0 && (
        <div style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          background: '#EF4444',
          color: 'white',
          borderRadius: '12px',
          padding: '4px 10px',
          fontSize: '13px',
          fontWeight: 600,
        }}>
          {count}
        </div>
      )}

      <div style={{
        fontSize: '40px',
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
        color: '#6B7280',
        margin: 0,
        lineHeight: 1.5,
      }}>{description}</p>
    </div>
  );
}
