import React, { useState, useEffect } from 'react'

export default function AdvancedSearchForm({ onSearch, loading }) {
  const [makes, setMakes] = useState([])
  const [models, setModels] = useState([])
  const [years, setYears] = useState([])

  const [filters, setFilters] = useState({
    make: '',
    model: '',
    year_min: '',
    year_max: '',
    price_min: '',
    price_max: '',
    mileage_min: '',
    mileage_max: '',
    fuel_type: '',
    transmission: '',
    sources: ['leboncoin', 'autoscout24']
  })

  // Charger les marques au montage
  useEffect(() => {
    fetch('http://localhost:8000/api/search-advanced/filters/makes')
      .then(res => res.json())
      .then(data => setMakes(data.makes))
      .catch(err => console.error('Erreur chargement marques:', err))

    // Charger les années
    fetch('http://localhost:8000/api/search-advanced/filters/years')
      .then(res => res.json())
      .then(data => setYears(data.years))
      .catch(err => console.error('Erreur chargement années:', err))
  }, [])

  // Charger les modèles quand la marque change
  useEffect(() => {
    if (filters.make) {
      fetch(`http://localhost:8000/api/search-advanced/filters/models/${filters.make}`)
        .then(res => res.json())
        .then(data => setModels(data.models))
        .catch(err => console.error('Erreur chargement modèles:', err))
    } else {
      setModels([])
      setFilters(prev => ({ ...prev, model: '' }))
    }
  }, [filters.make])

  const handleChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Nettoyer les valeurs vides
    const cleanedFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
    )
    onSearch(cleanedFilters)
  }

  const handleReset = () => {
    setFilters({
      make: '',
      model: '',
      year_min: '',
      year_max: '',
      price_min: '',
      price_max: '',
      mileage_min: '',
      mileage_max: '',
      fuel_type: '',
      transmission: '',
      sources: ['leboncoin', 'autoscout24']
    })
  }

  const toggleSource = (source) => {
    setFilters(prev => ({
      ...prev,
      sources: prev.sources.includes(source)
        ? prev.sources.filter(s => s !== source)
        : [...prev.sources, source]
    }))
  }

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h2 style={styles.title}>🔍 Recherche Multi-Sources</h2>

      {/* Sources */}
      <div style={styles.section}>
        <label style={styles.label}>Sources</label>
        <div style={styles.checkboxGroup}>
          <label style={styles.checkbox}>
            <input
              type="checkbox"
              checked={filters.sources.includes('leboncoin')}
              onChange={() => toggleSource('leboncoin')}
            />
            LeBonCoin
          </label>
          <label style={styles.checkbox}>
            <input
              type="checkbox"
              checked={filters.sources.includes('autoscout24')}
              onChange={() => toggleSource('autoscout24')}
            />
            AutoScout24
          </label>
        </div>
      </div>

      {/* Marque et Modèle */}
      <div style={styles.row}>
        <div style={styles.field}>
          <label style={styles.label}>Marque</label>
          <select
            value={filters.make}
            onChange={(e) => handleChange('make', e.target.value)}
            style={styles.select}
          >
            <option value="">Toutes les marques</option>
            {makes.map(make => (
              <option key={make.value} value={make.value}>{make.label}</option>
            ))}
          </select>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Modèle</label>
          <select
            value={filters.model}
            onChange={(e) => handleChange('model', e.target.value)}
            style={styles.select}
            disabled={!filters.make}
          >
            <option value="">Tous les modèles</option>
            {models.map(model => (
              <option key={model.value} value={model.value}>{model.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Année */}
      <div style={styles.section}>
        <label style={styles.label}>Année</label>
        <div style={styles.row}>
          <div style={styles.field}>
            <select
              value={filters.year_min}
              onChange={(e) => handleChange('year_min', e.target.value)}
              style={styles.select}
            >
              <option value="">Min</option>
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          <span style={styles.separator}>→</span>
          <div style={styles.field}>
            <select
              value={filters.year_max}
              onChange={(e) => handleChange('year_max', e.target.value)}
              style={styles.select}
            >
              <option value="">Max</option>
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Prix */}
      <div style={styles.section}>
        <label style={styles.label}>Prix (€)</label>
        <div style={styles.row}>
          <div style={styles.field}>
            <input
              type="number"
              placeholder="Min"
              value={filters.price_min}
              onChange={(e) => handleChange('price_min', e.target.value)}
              style={styles.input}
              min="0"
            />
          </div>
          <span style={styles.separator}>→</span>
          <div style={styles.field}>
            <input
              type="number"
              placeholder="Max"
              value={filters.price_max}
              onChange={(e) => handleChange('price_max', e.target.value)}
              style={styles.input}
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Kilométrage */}
      <div style={styles.section}>
        <label style={styles.label}>Kilométrage (km)</label>
        <div style={styles.row}>
          <div style={styles.field}>
            <input
              type="number"
              placeholder="Min"
              value={filters.mileage_min}
              onChange={(e) => handleChange('mileage_min', e.target.value)}
              style={styles.input}
              min="0"
            />
          </div>
          <span style={styles.separator}>→</span>
          <div style={styles.field}>
            <input
              type="number"
              placeholder="Max"
              value={filters.mileage_max}
              onChange={(e) => handleChange('mileage_max', e.target.value)}
              style={styles.input}
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Carburant */}
      <div style={styles.field}>
        <label style={styles.label}>Carburant</label>
        <select
          value={filters.fuel_type}
          onChange={(e) => handleChange('fuel_type', e.target.value)}
          style={styles.select}
        >
          <option value="">Tous</option>
          <option value="essence">Essence</option>
          <option value="diesel">Diesel</option>
          <option value="electrique">Électrique</option>
          <option value="hybride">Hybride</option>
          <option value="gpl">GPL</option>
        </select>
      </div>

      {/* Transmission */}
      <div style={styles.field}>
        <label style={styles.label}>Boîte de vitesse</label>
        <select
          value={filters.transmission}
          onChange={(e) => handleChange('transmission', e.target.value)}
          style={styles.select}
        >
          <option value="">Toutes</option>
          <option value="manuelle">Manuelle</option>
          <option value="automatique">Automatique</option>
        </select>
      </div>

      {/* Boutons d'action */}
      <div style={styles.actions}>
        <button
          type="button"
          onClick={handleReset}
          style={styles.resetButton}
          disabled={loading}
        >
          Réinitialiser
        </button>
        <button
          type="submit"
          style={styles.submitButton}
          disabled={loading}
        >
          {loading ? '🔄 Recherche en cours...' : '🔍 Rechercher'}
        </button>
      </div>
    </form>
  )
}

const styles = {
  form: {
    backgroundColor: '#fff',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    maxWidth: '800px',
    margin: '0 auto'
  },
  title: {
    fontSize: '24px',
    fontWeight: 600,
    marginBottom: '24px',
    color: '#24292e'
  },
  section: {
    marginBottom: '20px'
  },
  row: {
    display: 'flex',
    gap: '16px',
    alignItems: 'center'
  },
  field: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  label: {
    fontSize: '14px',
    fontWeight: 500,
    color: '#24292e'
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontFamily: 'inherit',
    width: '100%'
  },
  select: {
    padding: '10px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontFamily: 'inherit',
    backgroundColor: '#fff',
    cursor: 'pointer',
    width: '100%'
  },
  separator: {
    fontSize: '18px',
    color: '#6a737d',
    marginTop: '28px'
  },
  checkboxGroup: {
    display: 'flex',
    gap: '16px',
    flexWrap: 'wrap'
  },
  checkbox: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    cursor: 'pointer'
  },
  actions: {
    display: 'flex',
    gap: '12px',
    marginTop: '32px',
    justifyContent: 'flex-end'
  },
  resetButton: {
    padding: '12px 24px',
    backgroundColor: '#f6f8fa',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  submitButton: {
    padding: '12px 32px',
    backgroundColor: '#0366d6',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  }
}
