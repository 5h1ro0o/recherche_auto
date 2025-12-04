import React from 'react';
import { useNavigate } from 'react-router-dom';
import useSWR from 'swr';
import { getAvailableRequests, completeRequest } from '../services/assisted';

export default function ExpertMissionsPage() {
  const navigate = useNavigate();

  const { data: missions, mutate } = useSWR(
    ['/assisted/missions', 'IN_PROGRESS'],
    () => getAvailableRequests('IN_PROGRESS')
  );

  const { data: completed } = useSWR(
    ['/assisted/completed', 'COMPLETED'],
    () => getAvailableRequests('COMPLETED')
  );

  const handleComplete = async (requestId) => {
    if (!confirm('Marquer cette mission comme terminée ?')) return;

    try {
      await completeRequest(requestId);
      mutate();
      alert(' Mission terminée !');
    } catch (error) {
      console.error('Erreur:', error);
      alert('❌ Erreur lors de la finalisation');
    }
  };

  const totalMissions = (missions?.length || 0) + (completed?.length || 0);

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
          📋 Mes missions
        </h1>
        <p style={{
          fontSize: 'var(--space-4)',
          color: '#6a737d',
          margin: 0,
        }}>
          Gérez vos demandes en cours et consultez votre historique
        </p>
      </div>

      {/* Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-8)',
      }}>
        <StatCard
          icon=""
          label="En cours"
          value={missions?.length || 0}
          color="var(--red-accent)"
        />
        <StatCard
          icon=""
          label="Terminées"
          value={completed?.length || 0}
          color="var(--text-primary)"
        />
        <StatCard
          icon=""
          label="Total"
          value={totalMissions}
          color="var(--text-secondary)"
        />
        <StatCard
          icon=""
          label="Taux de complétion"
          value={
            totalMissions > 0
              ? `${Math.round(((completed?.length || 0) / totalMissions) * 100)}%`
              : '0%'
          }
          color="var(--text-primary)"
        />
      </div>

      {/* Active Missions */}
      <div style={{ marginBottom: 'var(--space-10)' }}>
        <h2 style={{
          fontSize: 'var(--space-5)',
          fontWeight: 600,
          color: '#24292e',
          marginBottom: 'var(--space-4)',
        }}>
           Missions en cours ({missions?.length || 0})
        </h2>

        {!missions ? (
          <div style={{
            textAlign: 'center',
            padding: '40px 20px',
            background: 'var(--white)',
                      }}>
            <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
            <p style={{ color: '#6a737d' }}>Chargement...</p>
          </div>
        ) : missions.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: 'var(--white)',
                      }}>
            <div style={{ fontSize: 'var(--space-16)', marginBottom: 'var(--space-4)' }}></div>
            <h3 style={{ margin: '0 0 8px 0' }}>Aucune mission en cours</h3>
            <p style={{ color: '#6a737d', marginBottom: 'var(--space-5)' }}>
              Acceptez des demandes depuis le marché pour commencer !
            </p>
            <button
              onClick={() => navigate('/expert/market')}
              style={{
                padding: '12px 24px',
                background: 'var(--red-accent)',
                color: 'var(--white)',
                border: 'none',
                                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'background 0.2s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
            >
              Voir le marché
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
            gap: 'var(--space-5)',
          }}>
            {missions.map((mission) => (
              <MissionCard
                key={mission.id}
                mission={mission}
                onViewDetails={() => navigate(`/expert/requests/${mission.id}`)}
                onComplete={() => handleComplete(mission.id)}
                onSearchVehicles={() => navigate(`/expert/requests/${mission.id}/search?budget_max=${mission.budget_max || ''}&fuel_type=${mission.preferred_fuel_type || ''}&transmission=${mission.preferred_transmission || ''}&max_mileage=${mission.max_mileage || ''}&min_year=${mission.min_year || ''}`)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Completed Missions */}
      {completed && completed.length > 0 && (
        <div>
          <h2 style={{
            fontSize: 'var(--space-5)',
            fontWeight: 600,
            color: '#24292e',
            marginBottom: 'var(--space-4)',
          }}>
             Missions terminées ({completed.length})
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
            gap: 'var(--space-5)',
          }}>
            {completed.slice(0, 6).map((mission) => (
              <CompletedMissionCard
                key={mission.id}
                mission={mission}
                onViewDetails={() => navigate(`/expert/requests/${mission.id}`)}
              />
            ))}
          </div>
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
      <div style={{ fontSize: 'var(--space-8)', lineHeight: 1 }}>{icon}</div>
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

function MissionCard({ mission, onViewDetails, onComplete, onSearchVehicles }) {
  const daysSince = Math.floor((Date.now() - new Date(mission.created_at).getTime()) / (1000 * 60 * 60 * 24));

  return (
    <div style={{
      background: 'var(--white)',
            padding: 'var(--space-6)',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 'var(--space-4)',
      }}>
        <div>
          <div style={{
            fontSize: 'var(--space-4)',
            fontWeight: 600,
            color: '#24292e',
            marginBottom: 'var(--space-1)',
          }}>
            {mission.client?.full_name || mission.client?.email}
          </div>
          <div style={{ fontSize: '13px', color: '#6a737d' }}>
            Acceptée il y a {daysSince} jour{daysSince > 1 ? 's' : ''}
          </div>
        </div>
        <span style={{
          background: 'var(--red-accent)',
          color: 'var(--white)',
          padding: '4px 10px',
                    fontSize: '11px',
          fontWeight: 600,
          letterSpacing: '0.5px',
          textTransform: 'uppercase',
        }}>
          En cours
        </span>
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
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
        }}>
          {mission.description}
        </p>
      </div>

      {/* Actions */}
      <div style={{
        display: 'flex',
        gap: 'var(--space-2)',
        flexDirection: 'column',
      }}>
        <button
          onClick={onSearchVehicles}
          style={{
            width: '100%',
            padding: 'var(--space-3)',
            background: 'var(--red-accent)',
            color: 'var(--white)',
            border: 'none',
                        fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'background 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
        >
           Rechercher véhicules
        </button>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <button
            onClick={onViewDetails}
            style={{
              flex: 1,
              padding: '10px',
              background: 'var(--white)',
              color: 'var(--text-primary)',
              border: '1px solid #EEEEEE',
                            fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
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
            Détails
          </button>
          <button
            onClick={onComplete}
            style={{
              flex: 1,
              padding: '10px',
              background: 'var(--text-primary)',
              color: 'var(--white)',
              border: 'none',
                            fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#000000'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'var(--text-primary)'}
          >
            Terminer
          </button>
        </div>
      </div>
    </div>
  );
}

function CompletedMissionCard({ mission, onViewDetails }) {
  const completedDate = new Date(mission.updated_at).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <div style={{
      background: 'var(--white)',
            padding: 'var(--space-5)',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      opacity: 0.8,
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 'var(--space-3)',
      }}>
        <div>
          <div style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#24292e',
            marginBottom: 'var(--space-1)',
          }}>
            {mission.client?.full_name || mission.client?.email}
          </div>
          <div style={{ fontSize: 'var(--space-3)', color: '#6a737d' }}>
            Terminée le {completedDate}
          </div>
        </div>
        <span style={{
          background: 'var(--text-primary)',
          color: 'var(--white)',
          padding: '4px 8px',
                    fontSize: '11px',
          fontWeight: 600,
          letterSpacing: '0.5px',
          textTransform: 'uppercase',
        }}>
          Terminée
        </span>
      </div>

      <button
        onClick={onViewDetails}
        style={{
          width: '100%',
          padding: '10px',
          background: 'var(--white)',
          color: 'var(--text-primary)',
          border: '1px solid #EEEEEE',
                    fontSize: '13px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s',
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
        Voir les détails
      </button>
    </div>
  );
}
