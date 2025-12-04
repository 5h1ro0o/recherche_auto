// frontend/src/Pages/ProDashboard.jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import useSWR from 'swr'
import { 
  getMyStock, 
  addVehicle, 
  updateVehicle, 
  deleteVehicle,
  toggleVisibility,
  getMyStats,
  getVehiclesByMonth,
  getPriceDistribution
} from '../services/pro'

export default function ProDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('stock')
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  // Charger données
  const { data: stock, mutate: mutateStock } = useSWR('/pro/stock', () => getMyStock(1, 50, statusFilter === 'all' ? null : statusFilter, searchTerm))
  const { data: stats } = useSWR('/pro/stats', getMyStats)
  const { data: monthlyData } = useSWR('/pro/stats/monthly', getVehiclesByMonth)
  const { data: priceData } = useSWR('/pro/stats/prices', getPriceDistribution)

  if (!user || user.role !== 'PRO') {
    return (
      <div className="access-denied">
        <h2>🔒 Accès réservé aux professionnels</h2>
        <p>Cette page est uniquement accessible aux comptes professionnels.</p>
        <button onClick={() => navigate('/')}>Retour à l'accueil</button>
      </div>
    )
  }

  return (
    <div className="pro-dashboard">
      <div className="dashboard-header">
        <div>
          <h1> Espace Professionnel</h1>
          <p className="subtitle">Gérez votre stock et suivez vos performances</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn-add-vehicle">
          ➕ Ajouter un véhicule
        </button>
      </div>

      {/* KPIs */}
      {stats && (
        <div className="kpi-grid">
          <KPICard
            icon=""
            label="Véhicules actifs"
            value={stats.active_vehicles}
            subtext={`${stats.inactive_vehicles} inactifs`}
            color="blue"
          />
          <KPICard
            icon=""
            label="Ajouts ce mois"
            value={stats.recent_additions}
            trend={stats.recent_additions > 0 ? '+' + stats.recent_additions : '0'}
            color="green"
          />
          <KPICard
            icon=""
            label="Favoris total"
            value={stats.total_favorites}
            color="red"
          />
          <KPICard
            icon=""
            label="Messages (30j)"
            value={stats.messages_received_30d}
            color="purple"
          />
        </div>
      )}

      {/* Véhicule le plus populaire */}
      {stats?.most_popular_vehicle && (
        <div className="popular-vehicle-banner">
          <div className="banner-content">
            <span className="banner-icon"></span>
            <div>
              <strong>Véhicule le plus populaire :</strong>{' '}
              {stats.most_popular_vehicle.title} ({stats.most_popular_vehicle.favorites} favoris)
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'stock' ? 'active' : ''}`}
          onClick={() => setActiveTab('stock')}
        >
          📦 Mon Stock {stock && `(${stock.length})`}
        </button>
        <button
          className={`tab ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
           Statistiques
        </button>
        <button
          className={`tab ${activeTab === 'messages' ? 'active' : ''}`}
          onClick={() => setActiveTab('messages')}
        >
           Messages
        </button>
      </div>

      {/* Contenu */}
      <div className="tab-content">
        {activeTab === 'stock' && (
          <StockTab
            stock={stock}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onEdit={(vehicle) => {
              setEditingVehicle(vehicle)
              setShowEditModal(true)
            }}
            onToggle={async (id) => {
              await toggleVisibility(id)
              mutateStock()
            }}
            onDelete={async (id) => {
              if (confirm('Supprimer ce véhicule définitivement ?')) {
                await deleteVehicle(id)
                mutateStock()
              }
            }}
            onRefresh={mutateStock}
          />
        )}

        {activeTab === 'stats' && (
          <StatsTab 
            stats={stats} 
            monthlyData={monthlyData}
            priceData={priceData}
          />
        )}

        {activeTab === 'messages' && (
          <MessagesTab />
        )}
      </div>

      {/* Modals */}
      {showAddModal && (
        <VehicleFormModal
          title="Ajouter un véhicule"
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false)
            mutateStock()
          }}
        />
      )}

      {showEditModal && editingVehicle && (
        <VehicleFormModal
          title="Modifier le véhicule"
          vehicle={editingVehicle}
          onClose={() => {
            setShowEditModal(false)
            setEditingVehicle(null)
          }}
          onSuccess={() => {
            setShowEditModal(false)
            setEditingVehicle(null)
            mutateStock()
          }}
        />
      )}
    </div>
  )
}

function KPICard({ icon, label, value, subtext, trend, color }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-content">
        <div className="kpi-label">{label}</div>
        <div className="kpi-value">
          {value}
          {trend && <span className="kpi-trend">{trend}</span>}
        </div>
        {subtext && <div className="kpi-subtext">{subtext}</div>}
      </div>
    </div>
  )
}

function StockTab({ stock, searchTerm, setSearchTerm, statusFilter, setStatusFilter, onEdit, onToggle, onDelete, onRefresh }) {
  if (!stock) return <div className="loading">Chargement du stock...</div>

  const filteredStock = stock.filter(v => {
    const matchSearch = !searchTerm || 
      v.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.make?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.model?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && v.is_active) ||
      (statusFilter === 'inactive' && !v.is_active)
    
    return matchSearch && matchStatus
  })

  return (
    <div className="stock-tab">
      {/* Filtres */}
      <div className="stock-filters">
        <input
          type="text"
          placeholder=" Rechercher un véhicule..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        
        <select 
          value={statusFilter} 
          onChange={(e) => setStatusFilter(e.target.value)}
          className="status-filter"
        >
          <option value="all">Tous les statuts</option>
          <option value="active"> Actifs uniquement</option>
          <option value="inactive">⏸️ Inactifs uniquement</option>
        </select>

        <button onClick={onRefresh} className="btn-refresh">
           Actualiser
        </button>
      </div>

      {/* Tableau */}
      {filteredStock.length === 0 ? (
        <div className="empty-state">
          <p>Aucun véhicule trouvé</p>
        </div>
      ) : (
        <div className="vehicles-table-wrapper">
          <table className="vehicles-table">
            <thead>
              <tr>
                <th>Véhicule</th>
                <th>Prix</th>
                <th>Année</th>
                <th>Kilométrage</th>
                <th>Carburant</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredStock.map(v => (
                <tr key={v.id} className={!v.is_active ? 'inactive-row' : ''}>
                  <td>
                    <div className="vehicle-cell">
                      <strong>{v.title || `${v.make || ''} ${v.model || ''}`}</strong>
                      {v.vin && <div className="vehicle-vin">VIN: {v.vin}</div>}
                    </div>
                  </td>
                  <td className="price-cell">{v.price ? `${v.price.toLocaleString()} €` : '—'}</td>
                  <td>{v.year || '—'}</td>
                  <td>{v.mileage ? `${v.mileage.toLocaleString()} km` : '—'}</td>
                  <td>{v.fuel_type || '—'}</td>
                  <td>
                    <span className={`status-badge ${v.is_active ? 'active' : 'inactive'}`}>
                      {v.is_active ? ' Actif' : '⏸️ Inactif'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        onClick={() => onToggle(v.id)} 
                        title={v.is_active ? 'Désactiver' : 'Activer'}
                        className="btn-icon"
                      >
                        {v.is_active ? '⏸️' : '▶️'}
                      </button>
                      <button 
                        onClick={() => onEdit(v)} 
                        title="Modifier"
                        className="btn-icon"
                      >
                        
                      </button>
                      <button 
                        onClick={() => onDelete(v.id)} 
                        title="Supprimer"
                        className="btn-icon danger"
                      >
                        
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function StatsTab({ stats, monthlyData, priceData }) {
  return (
    <div className="stats-tab">
      <h2> Statistiques détaillées</h2>
      
      <div className="charts-grid">
        {/* Graphique mensuel */}
        {monthlyData && monthlyData.labels.length > 0 && (
          <div className="chart-card">
            <h3>Véhicules ajoutés par mois</h3>
            <SimpleBarChart 
              labels={monthlyData.labels}
              data={monthlyData.data}
              color="#667eea"
            />
          </div>
        )}

        {/* Distribution prix */}
        {priceData && priceData.labels.length > 0 && (
          <div className="chart-card">
            <h3>Distribution des prix</h3>
            <SimpleBarChart 
              labels={priceData.labels}
              data={priceData.data}
              color="#28a745"
            />
          </div>
        )}
      </div>

      {/* Stats textuelles */}
      {stats && (
        <div className="stats-summary">
          <h3>Résumé</h3>
          <ul>
            <li>Total de véhicules : <strong>{stats.total_vehicles}</strong></li>
            <li>Véhicules actifs : <strong>{stats.active_vehicles}</strong> ({((stats.active_vehicles / stats.total_vehicles) * 100).toFixed(0)}%)</li>
            <li>Total favoris reçus : <strong>{stats.total_favorites}</strong></li>
            <li>Messages reçus (30j) : <strong>{stats.messages_received_30d}</strong></li>
          </ul>
        </div>
      )}
    </div>
  )
}

function SimpleBarChart({ labels, data, color }) {
  const maxValue = Math.max(...data)
  
  return (
    <div className="simple-bar-chart">
      {labels.map((label, idx) => (
        <div key={idx} className="bar-item">
          <div className="bar-label">{label}</div>
          <div className="bar-wrapper">
            <div 
              className="bar-fill" 
              style={{ 
                width: `${(data[idx] / maxValue) * 100}%`,
                backgroundColor: color
              }}
            >
              <span className="bar-value">{data[idx]}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function MessagesTab() {
  const navigate = useNavigate()
  
  return (
    <div className="messages-tab">
      <h2> Vos conversations</h2>
      <p>Gérez vos échanges avec les clients intéressés par vos véhicules.</p>
      <button onClick={() => navigate('/messages')} className="btn-primary">
        Accéder à la messagerie
      </button>
    </div>
  )
}

function VehicleFormModal({ title, vehicle = null, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    title: vehicle?.title || '',
    make: vehicle?.make || '',
    model: vehicle?.model || '',
    price: vehicle?.price || '',
    year: vehicle?.year || '',
    mileage: vehicle?.mileage || '',
    vin: vehicle?.vin || '',
    fuel_type: vehicle?.fuel_type || '',
    transmission: vehicle?.transmission || '',
    description: vehicle?.description || ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Nettoyer les données
      const cleanData = {}
      Object.entries(formData).forEach(([key, value]) => {
        if (value !== '' && value !== null) {
          cleanData[key] = ['price', 'year', 'mileage'].includes(key) ? parseInt(value) : value
        }
      })

      if (vehicle) {
        await updateVehicle(vehicle.id, cleanData)
      } else {
        await addVehicle(cleanData)
      }
      
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button onClick={onClose} className="close-modal">✕</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="vehicle-form">
          <div className="form-row">
            <div className="form-group">
              <label>Titre de l'annonce *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Ex: Belle Peugeot 208 5 portes"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Marque *</label>
              <input
                type="text"
                name="make"
                value={formData.make}
                onChange={handleChange}
                placeholder="Ex: Peugeot"
                required
              />
            </div>

            <div className="form-group">
              <label>Modèle *</label>
              <input
                type="text"
                name="model"
                value={formData.model}
                onChange={handleChange}
                placeholder="Ex: 208"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Prix (€) *</label>
              <input
                type="number"
                name="price"
                value={formData.price}
                onChange={handleChange}
                placeholder="Ex: 15000"
                min="0"
                required
              />
            </div>

            <div className="form-group">
              <label>Année *</label>
              <input
                type="number"
                name="year"
                value={formData.year}
                onChange={handleChange}
                placeholder="Ex: 2020"
                min="1980"
                max={new Date().getFullYear() + 1}
                required
              />
            </div>

            <div className="form-group">
              <label>Kilométrage *</label>
              <input
                type="number"
                name="mileage"
                value={formData.mileage}
                onChange={handleChange}
                placeholder="Ex: 50000"
                min="0"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Carburant</label>
              <select name="fuel_type" value={formData.fuel_type} onChange={handleChange}>
                <option value="">-- Sélectionner --</option>
                <option value="essence">Essence</option>
                <option value="diesel">Diesel</option>
                <option value="electrique">Électrique</option>
                <option value="hybride">Hybride</option>
              </select>
            </div>

            <div className="form-group">
              <label>Transmission</label>
              <select name="transmission" value={formData.transmission} onChange={handleChange}>
                <option value="">-- Sélectionner --</option>
                <option value="manuelle">Manuelle</option>
                <option value="automatique">Automatique</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>VIN (optionnel)</label>
            <input
              type="text"
              name="vin"
              value={formData.vin}
              onChange={handleChange}
              placeholder="Ex: VF3XXXXXXXXXXXXXXX"
              maxLength={17}
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Décrivez le véhicule, son état, son historique..."
              rows={4}
            />
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Annuler
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Enregistrement...' : vehicle ? 'Modifier' : 'Ajouter'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}