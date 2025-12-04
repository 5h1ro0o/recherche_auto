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
          fontSize: 'var(--space-6)',
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginBottom: 'var(--space-3)',
        }}>Accès réservé aux experts</h2>
        <p style={{
          color: 'var(--text-secondary)',
          marginBottom: 'var(--space-6)',
        }}>Cette page est uniquement accessible aux comptes experts.</p>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '12px 24px',
            background: 'var(--red-accent)',
            color: 'var(--white)',
            border: 'none',
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
    <div style={{ padding: 'var(--space-8)', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-8)' }}>
        <h1 style={{
          fontSize: 'var(--space-8)',
          fontWeight: 700,
          color: 'var(--text-primary)',
          margin: '0 0 8px 0',
        }}>
           Dashboard Expert
        </h1>
        <p style={{
          fontSize: 'var(--space-4)',
          color: 'var(--text-secondary)',
          margin: 0,
        }}>
          Bienvenue {user?.full_name || user?.email} - Vue d'ensemble de votre activité
        </p>
      </div>

      {/* Statistiques principales avec graphiques */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-8)',
      }}>
        <KPICard
          icon="📋"
          label="Total demandes"
          value={totalRequests}
          color="var(--red-accent)"
          trend="+12%"
        />
        <KPICard
          icon=""
          label="En cours"
          value={inProgressRequests}
          percentage={inProgressRate}
          color="#F59E0B"
        />
        <KPICard
          icon=""
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
        gap: 'var(--space-6)',
        marginBottom: 'var(--space-8)',
      }}>
        {/* Graphique des demandes */}
        <div style={{
          background: 'var(--white)',
          padding: 'var(--space-6)',
                    border: '1px solid #EEEEEE',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <h3 style={{
            fontSize: 'var(--space-4)',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: 'var(--space-5)',
          }}> Répartition des demandes</h3>

          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 'var(--space-6)' }}>
            <PieChart
              data={[
                { value: completedRequests, color: '#10B981', label: 'Terminées' },
                { value: inProgressRequests, color: '#F59E0B', label: 'En cours' },
                { value: pendingRequests, color: 'var(--red-accent)', label: 'En attente' },
              ]}
              size={180}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            <LegendItem color="#10B981" label="Terminées" value={completedRequests} total={totalRequests} />
            <LegendItem color="#F59E0B" label="En cours" value={inProgressRequests} total={totalRequests} />
            <LegendItem color="var(--red-accent)" label="En attente" value={pendingRequests} total={totalRequests} />
          </div>
        </div>

        {/* Graphique des propositions */}
        <div style={{
          background: 'var(--white)',
          padding: 'var(--space-6)',
                    border: '1px solid #EEEEEE',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <h3 style={{
            fontSize: 'var(--space-4)',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: 'var(--space-5)',
          }}> Statut des propositions</h3>

          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 'var(--space-6)' }}>
            <PieChart
              data={[
                { value: acceptedProposals, color: '#10B981', label: 'Acceptées' },
                { value: pendingProposals, color: '#6B7280', label: 'En attente' },
                { value: rejectedProposals, color: 'var(--red-accent)', label: 'Refusées' },
              ]}
              size={180}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            <LegendItem color="#10B981" label="Acceptées" value={acceptedProposals} total={totalProposals} />
            <LegendItem color="#6B7280" label="En attente" value={pendingProposals} total={totalProposals} />
            <LegendItem color="var(--red-accent)" label="Refusées" value={rejectedProposals} total={totalProposals} />
          </div>
        </div>

        {/* Métriques de performance */}
        <div style={{
          background: 'var(--white)',
          padding: 'var(--space-6)',
                    border: '1px solid #EEEEEE',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <h3 style={{
            fontSize: 'var(--space-4)',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: 'var(--space-5)',
          }}> Métriques de performance</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
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
            marginTop: 'var(--space-5)',
            padding: 'var(--space-3)',
            background: 'var(--gray-50)',
                        textAlign: 'center',
          }}>
            <div style={{ fontSize: 'var(--space-3)', color: '#6B7280', marginBottom: 'var(--space-1)' }}>
              Performance globale
            </div>
            <div style={{ fontSize: 'var(--space-6)', fontWeight: 700, color: 'var(--red-accent)' }}>
              {Math.round((completionRate + acceptanceRate) / 2)}%
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: 'var(--space-4)',
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
          icon=""
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
        background: 'var(--border-light)',
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
              stroke="var(--white)"
              strokeWidth="2"
            />
          );
        })}

        {/* Center circle for donut effect */}
        <circle cx="100" cy="100" r="45" fill="var(--white)" />

        {/* Center text */}
        <text
          x="100"
          y="95"
          textAnchor="middle"
          style={{
            fontSize: 'var(--space-6)',
            fontWeight: 700,
            fill: 'var(--text-primary)',
          }}
        >
          {total}
        </text>
        <text
          x="100"
          y="112"
          textAnchor="middle"
          style={{
            fontSize: 'var(--space-3)',
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
      padding: 'var(--space-2)',
            background: 'var(--gray-50)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <div style={{
          width: 'var(--space-3)',
          height: 'var(--space-3)',
                    background: color,
        }} />
        <span style={{ fontSize: '14px', color: '#374151' }}>{label}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
          {value}
        </span>
        <span style={{ fontSize: 'var(--space-3)', color: '#6B7280' }}>
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
        marginBottom: 'var(--space-2)',
      }}>
        <span style={{ fontSize: '14px', color: '#374151' }}>{label}</span>
        <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
          {percentage}%
        </span>
      </div>
      <div style={{
        height: 'var(--space-2)',
        background: 'var(--border-light)',
                overflow: 'hidden',
      }}>
        <div style={{
          width: `${percentage}%`,
          height: '100%',
          background: color,
                    transition: 'width 0.3s ease',
        }} />
      </div>
    </div>
  );
}

function KPICard({ icon, label, value, percentage, color, trend }) {
  return (
    <div style={{
      background: 'var(--white)',
      padding: 'var(--space-5)',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      border: '1px solid #EEEEEE',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 'var(--space-1)',
        height: '100%',
        background: color,
      }} />

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: 'var(--space-3)',
            color: '#6B7280',
            marginBottom: 'var(--space-2)',
            textTransform: 'uppercase',
            fontWeight: 600,
            letterSpacing: '0.5px',
          }}>
            {label}
          </div>
          <div style={{
            fontSize: 'var(--space-7)',
            fontWeight: 700,
            color: color,
            marginBottom: 'var(--space-1)',
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
              marginTop: 'var(--space-1)',
            }}>
              {trend} ce mois
            </div>
          )}
        </div>
        <div style={{
          fontSize: 'var(--space-8)',
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
        background: 'var(--white)',
        padding: 'var(--space-6)',
                border: '2px solid #EEEEEE',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        cursor: 'pointer',
        transition: 'all 0.2s',
        position: 'relative',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
        e.currentTarget.style.borderColor = 'var(--red-accent)';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        e.currentTarget.style.borderColor = 'var(--border-light)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      {count !== undefined && count > 0 && (
        <div style={{
          position: 'absolute',
          top: 'var(--space-4)',
          right: 'var(--space-4)',
          background: 'var(--red-accent)',
          color: 'var(--white)',
                    padding: '4px 10px',
          fontSize: '13px',
          fontWeight: 600,
        }}>
          {count}
        </div>
      )}

      <div style={{
        fontSize: 'var(--space-10)',
        marginBottom: 'var(--space-3)',
      }}>{icon}</div>
      <h3 style={{
        fontSize: '18px',
        fontWeight: 600,
        color: 'var(--text-primary)',
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
