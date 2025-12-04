import { useState, useEffect } from 'react'

export default function AdminDashboard() {
  // Simuler l'utilisateur (remplacer par votre contexte d'auth)
  const user = { id: 'admin1', role: 'ADMIN', email: 'admin@example.com' }
  
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [scraperLogs, setScraperLogs] = useState([])
  const [workerHealth, setWorkerHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  // Vérifier accès admin
  if (!user || user.role !== 'ADMIN') {
    return (
      <div style={{
        maxWidth: '600px',
        margin: '100px auto',
        textAlign: 'center',
        padding: 'var(--space-10)',
        background: 'var(--white)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <div style={{ fontSize: 'var(--space-16)', marginBottom: 'var(--space-5)' }}>🔒</div>
        <h2 style={{ marginBottom: 'var(--space-4)' }}>Accès réservé aux administrateurs</h2>
        <p style={{ color: '#6a737d', marginBottom: 'var(--space-6)' }}>
          Cette page nécessite des privilèges administrateur
        </p>
        <button 
          onClick={() => window.location.href = '/'}
          style={{
            padding: '12px 24px',
            background: '#667eea',
            color: 'var(--white)',
            border: 'none',
                        fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          Retour à l'accueil
        </button>
      </div>
    )
  }

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  async function loadData() {
    try {
      const mockStats = {
        total_vehicles: 15234,
        sources: {
          leboncoin: 8945,
          lacentrale: 4532,
          autoscout24: 1757
        },
        deduplication: {
          total_processed: 18234,
          duplicates_found: 3000,
          rate: 16.5
        },
        last_24h: {
          new_vehicles: 243,
          updated_vehicles: 127,
          errors: 5
        },
        by_day: [
          { date: '2025-01-20', count: 243 },
          { date: '2025-01-21', count: 198 },
          { date: '2025-01-22', count: 267 },
          { date: '2025-01-23', count: 312 },
          { date: '2025-01-24', count: 289 },
          { date: '2025-01-25', count: 234 },
          { date: '2025-01-26', count: 201 }
        ]
      }

      const mockLogs = [
        {
          id: 1,
          timestamp: new Date(Date.now() - 2 * 60 * 1000),
          source: 'leboncoin',
          status: 'success',
          message: '124 véhicules scrapés',
          duration: '3.2s'
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 15 * 60 * 1000),
          source: 'lacentrale',
          status: 'warning',
          message: 'Pagination limitée à 5 pages',
          duration: '4.1s'
        },
        {
          id: 3,
          timestamp: new Date(Date.now() - 45 * 60 * 1000),
          source: 'autoscout24',
          status: 'error',
          message: 'Timeout après 30s',
          duration: '30.0s'
        }
      ]

      const mockWorkerHealth = {
        status: 'healthy',
        uptime_seconds: 86400,
        queue_size: 23,
        stats: {
          total_processed: 1523,
          total_errors: 3,
          total_duplicates: 245
        },
        connections: {
          redis: true,
          elasticsearch: true,
          database: true
        }
      }

      setStats(mockStats)
      setScraperLogs(mockLogs)
      setWorkerHealth(mockWorkerHealth)
      setLoading(false)
    } catch (error) {
      console.error('Erreur:', error)
      setLoading(false)
    }
  }

  async function triggerScraper(source) {
    if (!confirm(`Lancer le scraper ${source} manuellement ?`)) return
    alert(`🚀 Scraper ${source} lancé !`)
    setTimeout(loadData, 2000)
  }

  async function clearQueue() {
    if (!confirm('Vider la queue Redis ?')) return
    alert(' Queue vidée')
    loadData()
  }

  if (loading) {
    return (
      <div style={{ padding: 'var(--space-10)', textAlign: 'center' }}>
        <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
        <p>Chargement...</p>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: '1600px', margin: '0 auto', padding: 'var(--space-5)' }}>
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ 
          fontSize: 'var(--space-8)', 
          fontWeight: 700, 
          marginBottom: 'var(--space-2)',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
           Dashboard Administrateur
        </h1>
        <p style={{ color: '#6a737d', fontSize: '15px' }}>
          Monitoring des scrapers, worker et base de données
        </p>
      </div>

      {workerHealth && <HealthAlert workerHealth={workerHealth} onRefresh={loadData} />}

      <div style={{
        display: 'flex',
        gap: 'var(--space-2)',
        marginBottom: 'var(--space-6)',
        background: 'var(--white)',
        padding: 'var(--space-2)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
      }}>
        <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')} label=" Vue d'ensemble" />
        <TabButton active={activeTab === 'scrapers'} onClick={() => setActiveTab('scrapers')} label="🕷️ Scrapers" />
        <TabButton active={activeTab === 'worker'} onClick={() => setActiveTab('worker')} label=" Worker" />
        <TabButton active={activeTab === 'logs'} onClick={() => setActiveTab('logs')} label="📋 Logs" />
      </div>

      {activeTab === 'overview' && <OverviewTab stats={stats} />}
      {activeTab === 'scrapers' && <ScrapersTab stats={stats} onTrigger={triggerScraper} workerHealth={workerHealth} onClearQueue={clearQueue} />}
      {activeTab === 'worker' && <WorkerTab workerHealth={workerHealth} />}
      {activeTab === 'logs' && <LogsTab logs={scraperLogs} />}
    </div>
  )
}

function HealthAlert({ workerHealth, onRefresh }) {
  const hasIssues = !workerHealth.connections.redis || !workerHealth.connections.elasticsearch || !workerHealth.connections.database || workerHealth.queue_size > 100
  if (!hasIssues) return null

  return (
    <div style={{
      background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
      color: 'var(--white)',
      padding: '16px 20px',
            marginBottom: 'var(--space-6)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <span style={{ fontSize: 'var(--space-6)' }}></span>
        <div>
          <strong>Problèmes détectés</strong>
          <div style={{ fontSize: '13px', opacity: 0.9 }}>
            {!workerHealth.connections.redis && '❌ Redis • '}
            {!workerHealth.connections.elasticsearch && '❌ ES • '}
            {!workerHealth.connections.database && '❌ DB • '}
            {workerHealth.queue_size > 100 && ` Queue: ${workerHealth.queue_size}`}
          </div>
        </div>
      </div>
      <button onClick={onRefresh} style={{
        background: 'rgba(255,255,255,0.2)',
        border: '1px solid rgba(255,255,255,0.3)',
        color: 'var(--white)',
        padding: '8px 16px',
                cursor: 'pointer',
        fontSize: '13px',
        fontWeight: 600
      }}>
         Rafraîchir
      </button>
    </div>
  )
}

function TabButton({ active, onClick, label }) {
  return (
    <button onClick={onClick} style={{
      padding: '12px 20px',
      background: active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
      color: active ? 'var(--white)' : '#6a737d',
      border: 'none',
            fontSize: '14px',
      fontWeight: active ? 600 : 500,
      cursor: 'pointer',
      transition: 'all 0.2s',
      whiteSpace: 'nowrap'
    }}>
      {label}
    </button>
  )
}

function OverviewTab({ stats }) {
  return (
    <div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: '30px'
      }}>
        <KPICard icon="" label="Total véhicules" value={stats.total_vehicles.toLocaleString()} color="#667eea" />
        <KPICard icon="" label="Nouveaux (24h)" value={stats.last_24h.new_vehicles} trend={`+${stats.last_24h.new_vehicles}`} color="#28a745" />
        <KPICard icon="" label="Mis à jour (24h)" value={stats.last_24h.updated_vehicles} color="#17a2b8" />
        <KPICard icon="❌" label="Erreurs (24h)" value={stats.last_24h.errors} color={stats.last_24h.errors > 10 ? '#dc3545' : '#ffc107'} />
      </div>

      <div style={{
        background: 'var(--white)',
        padding: 'var(--space-6)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        marginBottom: 'var(--space-6)'
      }}>
        <h3 style={{ marginBottom: 'var(--space-5)', fontSize: '18px', fontWeight: 600 }}> Répartition par source</h3>
        <SourcesChart sources={stats.sources} total={stats.total_vehicles} />
      </div>

      <div style={{
        background: 'var(--white)',
        padding: 'var(--space-6)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        marginBottom: 'var(--space-6)'
      }}>
        <h3 style={{ marginBottom: 'var(--space-5)', fontSize: '18px', fontWeight: 600 }}> Déduplication</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-4)'
        }}>
          <StatItem label="Annonces traitées" value={stats.deduplication.total_processed.toLocaleString()} />
          <StatItem label="Doublons détectés" value={stats.deduplication.duplicates_found.toLocaleString()} />
          <StatItem label="Taux de déduplication" value={`${stats.deduplication.rate}%`} highlight />
        </div>
      </div>

      <div style={{
        background: 'var(--white)',
        padding: 'var(--space-6)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
      }}>
        <h3 style={{ marginBottom: 'var(--space-5)', fontSize: '18px', fontWeight: 600 }}> Annonces par jour (7 derniers jours)</h3>
        <TimelineChart data={stats.by_day} />
      </div>
    </div>
  )
}

function ScrapersTab({ stats, onTrigger, workerHealth, onClearQueue }) {
  const scrapers = [
    { id: 'leboncoin', name: 'LeBonCoin', icon: '', count: stats.sources.leboncoin, status: 'active', schedule: 'Toutes les 6h' },
    { id: 'lacentrale', name: 'La Centrale', icon: '🟢', count: stats.sources.lacentrale, status: 'active', schedule: 'Toutes les 6h (offset 30min)' },
    { id: 'autoscout24', name: 'AutoScout24', icon: '🔴', count: stats.sources.autoscout24, status: 'warning', schedule: 'Toutes les 12h' }
  ]

  return (
    <div>
      <div style={{
        background: workerHealth.queue_size > 50 ? 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)' : 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
        color: 'var(--white)',
        padding: 'var(--space-5)',
                marginBottom: 'var(--space-6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: 'var(--space-1)' }}>Queue Redis</div>
          <div style={{ fontSize: 'var(--space-8)', fontWeight: 700 }}>{workerHealth.queue_size} annonces</div>
        </div>
        <button onClick={onClearQueue} style={{
          background: 'rgba(255,255,255,0.2)',
          border: '1px solid rgba(255,255,255,0.3)',
          color: 'var(--white)',
          padding: '10px 20px',
                    cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 600
        }}>
           Vider la queue
        </button>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: 'var(--space-5)'
      }}>
        {scrapers.map(scraper => (
          <ScraperCard key={scraper.id} scraper={scraper} onTrigger={() => onTrigger(scraper.id)} />
        ))}
      </div>
    </div>
  )
}

function ScraperCard({ scraper, onTrigger }) {
  const statusColors = {
    active: { bg: '#d4edda', color: '#155724', text: ' Actif' },
    warning: { bg: '#fff3cd', color: '#856404', text: ' Avertissement' },
    error: { bg: '#f8d7da', color: '#721c24', text: '❌ Erreur' }
  }
  const status = statusColors[scraper.status]

  return (
    <div style={{
      background: 'var(--white)',
            padding: 'var(--space-6)',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      border: '2px solid #e1e4e8'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-3)',
        marginBottom: 'var(--space-4)'
      }}>
        <span style={{ fontSize: 'var(--space-8)' }}>{scraper.icon}</span>
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>{scraper.name}</h3>
          <div style={{ fontSize: '13px', color: '#6a737d', marginTop: '2px' }}>{scraper.schedule}</div>
        </div>
        <div style={{
          background: status.bg,
          color: status.color,
          padding: '4px 12px',
                    fontSize: 'var(--space-3)',
          fontWeight: 600
        }}>
          {status.text}
        </div>
      </div>

      <div style={{
        background: '#f8f9fa',
        padding: 'var(--space-4)',
                marginBottom: 'var(--space-4)'
      }}>
        <div style={{ fontSize: '13px', color: '#6a737d', marginBottom: 'var(--space-1)' }}>Annonces dans la base</div>
        <div style={{ fontSize: 'var(--space-7)', fontWeight: 700, color: '#24292e' }}>{scraper.count.toLocaleString()}</div>
      </div>

      <button onClick={onTrigger} style={{
        width: '100%',
        padding: 'var(--space-3)',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'var(--white)',
        border: 'none',
                fontSize: '14px',
        fontWeight: 600,
        cursor: 'pointer'
      }}>
        🚀 Lancer manuellement
      </button>
    </div>
  )
}

function WorkerTab({ workerHealth }) {
  const hours = Math.floor(workerHealth.uptime_seconds / 3600)
  const minutes = Math.floor((workerHealth.uptime_seconds % 3600) / 60)
  const uptime = `${hours}h ${minutes}m`

  return (
    <div>
      <div style={{
        background: workerHealth.status === 'healthy' ? 'linear-gradient(135deg, #28a745 0%, #20c997 100%)' : 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)',
        color: 'var(--white)',
        padding: 'var(--space-6)',
                marginBottom: 'var(--space-6)',
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-4)'
      }}>
        <span style={{ fontSize: 'var(--space-12)' }}>{workerHealth.status === 'healthy' ? '' : '❌'}</span>
        <div>
          <h2 style={{ margin: 0, fontSize: 'var(--space-6)', fontWeight: 700 }}>Worker {workerHealth.status === 'healthy' ? 'opérationnel' : 'en erreur'}</h2>
          <div style={{ fontSize: '14px', opacity: 0.9, marginTop: 'var(--space-1)' }}>Uptime: {uptime}</div>
        </div>
      </div>

      <div style={{
        background: 'var(--white)',
        padding: 'var(--space-6)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        marginBottom: 'var(--space-6)'
      }}>
        <h3 style={{ marginBottom: 'var(--space-5)', fontSize: '18px', fontWeight: 600 }}>🔌 État des connexions</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-4)'
        }}>
          <ConnectionStatus name="Redis" connected={workerHealth.connections.redis} />
          <ConnectionStatus name="Elasticsearch" connected={workerHealth.connections.elasticsearch} />
          <ConnectionStatus name="PostgreSQL" connected={workerHealth.connections.database} />
        </div>
      </div>

      <div style={{
        background: 'var(--white)',
        padding: 'var(--space-6)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
      }}>
        <h3 style={{ marginBottom: 'var(--space-5)', fontSize: '18px', fontWeight: 600 }}> Statistiques du worker</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-4)'
        }}>
          <StatItem label="Véhicules traités" value={workerHealth.stats.total_processed.toLocaleString()} />
          <StatItem label="Doublons détectés" value={workerHealth.stats.total_duplicates.toLocaleString()} />
          <StatItem label="Erreurs" value={workerHealth.stats.total_errors} highlight={workerHealth.stats.total_errors > 10} />
        </div>
      </div>
    </div>
  )
}

function LogsTab({ logs }) {
  return (
    <div style={{
      background: 'var(--white)',
      padding: 'var(--space-6)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <h3 style={{ marginBottom: 'var(--space-5)', fontSize: '18px', fontWeight: 600 }}>📋 Logs des scrapers</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {logs.map(log => <LogEntry key={log.id} log={log} />)}
      </div>
    </div>
  )
}

function LogEntry({ log }) {
  const statusConfig = {
    success: { icon: '', color: '#28a745', bg: '#d4edda' },
    warning: { icon: '', color: '#ffc107', bg: '#fff3cd' },
    error: { icon: '❌', color: '#dc3545', bg: '#f8d7da' }
  }
  const config = statusConfig[log.status]
  const elapsed = Math.floor((Date.now() - log.timestamp) / 60000)
  const timeAgo = elapsed < 60 ? `Il y a ${elapsed} min` : `Il y a ${Math.floor(elapsed / 60)} h`

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-4)',
      padding: 'var(--space-4)',
      background: config.bg,
            borderLeft: `4px solid ${config.color}`
    }}>
      <span style={{ fontSize: 'var(--space-6)' }}>{config.icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-1)' }}>
          <strong>{log.source}</strong>
          <span style={{ fontSize: 'var(--space-3)', color: '#6a737d', background: 'rgba(0,0,0,0.1)', padding: '2px 8px',  }}>
            {log.duration}
          </span>
        </div>
        <div style={{ fontSize: '14px', color: '#586069' }}>{log.message}</div>
      </div>
      <div style={{ fontSize: 'var(--space-3)', color: '#6a737d', textAlign: 'right' }}>{timeAgo}</div>
    </div>
  )
}

function KPICard({ icon, label, value, trend, color }) {
  return (
    <div style={{
      background: 'var(--white)',
      padding: 'var(--space-6)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-4)'
    }}>
      <div style={{ fontSize: 'var(--space-10)' }}>{icon}</div>
      <div>
        <div style={{ fontSize: 'var(--space-3)', color: '#6a737d', marginBottom: 'var(--space-1)', textTransform: 'uppercase', fontWeight: 600 }}>{label}</div>
        <div style={{ fontSize: 'var(--space-7)', fontWeight: 700, color }}>
          {value}
          {trend && <span style={{ fontSize: '14px', color: '#28a745', marginLeft: 'var(--space-2)' }}>{trend}</span>}
        </div>
      </div>
    </div>
  )
}

function SourcesChart({ sources, total }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      {Object.entries(sources).map(([name, count]) => {
        const percentage = (count / total * 100).toFixed(1)
        return (
          <div key={name}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '14px' }}>
              <strong>{name}</strong>
              <span style={{ color: '#6a737d' }}>{count.toLocaleString()} ({percentage}%)</span>
            </div>
            <div style={{ height: 'var(--space-2)', background: '#e1e4e8',  overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${percentage}%`,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}

function TimelineChart({ data }) {
  const maxCount = Math.max(...data.map(d => d.count))
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 'var(--space-2)', height: '200px' }}>
      {data.map((item, idx) => (
        <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-2)' }}>
          <div style={{ fontSize: 'var(--space-3)', fontWeight: 600 }}>{item.count}</div>
          <div style={{
            width: '100%',
            height: `${(item.count / maxCount) * 180}px`,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '8px 8px 0 0'
          }} />
          <div style={{ fontSize: '11px', color: '#6a737d' }}>
            {item.date.split('-')[2]}/{item.date.split('-')[1]}
          </div>
        </div>
      ))}
    </div>
  )
}

function StatItem({ label, value, highlight }) {
  return (
    <div style={{
      background: highlight ? '#fff3cd' : '#f8f9fa',
      padding: 'var(--space-4)',
          }}>
      <div style={{ fontSize: '13px', color: '#6a737d', marginBottom: '6px' }}>{label}</div>
      <div style={{ fontSize: 'var(--space-6)', fontWeight: 700, color: highlight ? '#856404' : '#24292e' }}>{value}</div>
    </div>
  )
}

function ConnectionStatus({ name, connected }) {
  return (
    <div style={{
      padding: 'var(--space-4)',
      background: connected ? '#d4edda' : '#f8d7da',
            display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-3)'
    }}>
      <span style={{ fontSize: 'var(--space-6)' }}>{connected ? '' : '❌'}</span>
      <div>
        <div style={{ fontWeight: 600, color: connected ? '#155724' : '#721c24' }}>{name}</div>
        <div style={{ fontSize: 'var(--space-3)', color: connected ? '#155724' : '#721c24', opacity: 0.8 }}>
          {connected ? 'Connecté' : 'Déconnecté'}
        </div>
      </div>
    </div>
  )
}