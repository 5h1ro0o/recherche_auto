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
      alert('✅ Mission terminée !');
    } catch (error) {
      console.error('Erreur:', error);
      alert('❌ Erreur lors de la finalisation');
    }
  };

  const totalMissions = (missions?.length || 0) + (completed?.length || 0);

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          color: '#24292e',
          margin: '0 0 8px 0',
        }}>
          📋 Mes missions
        </h1>
        <p style={{
          fontSize: '16px',
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
        gap: '16px',
        marginBottom: '32px',
      }}>
        <StatCard
          icon="🔄"
          label="En cours"
          value={missions?.length || 0}
          color="#0366d6"
        />
        <StatCard
          icon="✅"
          label="Terminées"
          value={completed?.length || 0}
          color="#28a745"
        />
        <StatCard
          icon="📊"
          label="Total"
          value={totalMissions}
          color="#6a737d"
        />
        <StatCard
          icon="📈"
          label="Taux de complétion"
          value={
            totalMissions > 0
              ? `${Math.round(((completed?.length || 0) / totalMissions) * 100)}%`
              : '0%'
          }
          color="#764ba2"
        />
      </div>

      {/* Active Missions */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{
          fontSize: '20px',
          fontWeight: 600,
          color: '#24292e',
          marginBottom: '16px',
        }}>
          🔄 Missions en cours ({missions?.length || 0})
        </h2>

        {!missions ? (
          <div style={{
            textAlign: 'center',
            padding: '40px 20px',
            background: 'white',
            borderRadius: '12px',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
            <p style={{ color: '#6a737d' }}>Chargement...</p>
          </div>
        ) : missions.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: 'white',
            borderRadius: '12px',
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>🎉</div>
            <h3 style={{ margin: '0 0 8px 0' }}>Aucune mission en cours</h3>
            <p style={{ color: '#6a737d', marginBottom: '20px' }}>
              Acceptez des demandes depuis le marché pour commencer !
            </p>
            <button
              onClick={() => navigate('/expert/market')}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              🏪 Voir le marché
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
            gap: '20px',
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
            fontSize: '20px',
            fontWeight: 600,
            color: '#24292e',
            marginBottom: '16px',
          }}>
            ✅ Missions terminées ({completed.length})
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
            gap: '20px',
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
      background: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
    }}>
      <div style={{ fontSize: '32px', lineHeight: 1 }}>{icon}</div>
      <div>
        <div style={{
          fontSize: '12px',
          color: '#6a737d',
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
      </div>
    </div>
  );
}

function MissionCard({ mission, onViewDetails, onComplete, onSearchVehicles }) {
  const daysSince = Math.floor((Date.now() - new Date(mission.created_at).getTime()) / (1000 * 60 * 60 * 24));

  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      border: '2px solid #667eea',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '16px',
      }}>
        <div>
          <div style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#24292e',
            marginBottom: '4px',
          }}>
            {mission.client?.full_name || mission.client?.email}
          </div>
          <div style={{ fontSize: '13px', color: '#6a737d' }}>
            Acceptée il y a {daysSince} jour{daysSince > 1 ? 's' : ''}
          </div>
        </div>
        <span style={{
          background: '#0366d6',
          color: 'white',
          padding: '4px 10px',
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: 600,
        }}>
          En cours
        </span>
      </div>

      {/* Description */}
      <div style={{
        background: '#f6f8fa',
        padding: '12px',
        borderRadius: '8px',
        marginBottom: '16px',
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
        gap: '8px',
        flexDirection: 'column',
      }}>
        <button
          onClick={onSearchVehicles}
          style={{
            width: '100%',
            padding: '12px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          🔍 Rechercher véhicules
        </button>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={onViewDetails}
            style={{
              flex: 1,
              padding: '10px',
              background: 'white',
              color: '#0366d6',
              border: '2px solid #0366d6',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            👁️ Détails
          </button>
          <button
            onClick={onComplete}
            style={{
              flex: 1,
              padding: '10px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            ✅ Terminer
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
      background: 'white',
      borderRadius: '16px',
      padding: '20px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      opacity: 0.8,
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '12px',
      }}>
        <div>
          <div style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#24292e',
            marginBottom: '4px',
          }}>
            {mission.client?.full_name || mission.client?.email}
          </div>
          <div style={{ fontSize: '12px', color: '#6a737d' }}>
            Terminée le {completedDate}
          </div>
        </div>
        <span style={{
          background: '#28a745',
          color: 'white',
          padding: '4px 8px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 600,
        }}>
          ✅ Terminée
        </span>
      </div>

      <button
        onClick={onViewDetails}
        style={{
          width: '100%',
          padding: '10px',
          background: '#f6f8fa',
          color: '#24292e',
          border: '1px solid #e1e4e8',
          borderRadius: '8px',
          fontSize: '13px',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        👁️ Voir les détails
      </button>
    </div>
  );
}
