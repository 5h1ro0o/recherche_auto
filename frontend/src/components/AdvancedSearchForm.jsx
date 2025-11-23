import React, { useState, useEffect } from 'react'

export default function AdvancedSearchForm({ onSearch, loading }) {
  const [makes, setMakes] = useState([])
  const [models, setModels] = useState([])
  const [years, setYears] = useState([])

  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [showEquipmentFilters, setShowEquipmentFilters] = useState(false)

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
    body_type: '',
    horsepower_min: '',
    horsepower_max: '',
    horsepower_fiscal_min: '',
    horsepower_fiscal_max: '',
    seller_type: '',
    first_registration: false,
    nb_doors: '',
    nb_seats: '',
    color: '',
    color_interior: '',
    metallic_color: false,
    emission_class: '',
    critair: '',
    co2_max: '',
    technical_control_ok: false,
    non_smoker: false,
    no_accident: false,
    service_history: false,
    warranty: false,
    manufacturer_warranty: false,
    // Équipements confort
    climate_control: '',
    leather_interior: false,
    sunroof: false,
    panoramic_roof: false,
    heated_seats: false,
    electric_seats: false,
    parking_sensors: false,
    parking_camera: false,
    // Équipements technologie
    gps: false,
    bluetooth: false,
    apple_carplay: false,
    android_auto: false,
    cruise_control: false,
    adaptive_cruise_control: false,
    keyless_entry: false,
    head_up_display: false,
    // Équipements sécurité
    abs: false,
    esp: false,
    airbags: '',
    lane_assist: false,
    blind_spot: false,
    automatic_emergency_braking: false,
    // Autres équipements
    alloy_wheels: false,
    led_headlights: false,
    xenon_headlights: false,
    tow_bar: false,
    ski_rack: false,
    roof_rack: false,
    // Motorisation
    cylinders: '',
    engine_size: '',
    drive_type: '',
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
      body_type: '',
      horsepower_min: '',
      horsepower_max: '',
      horsepower_fiscal_min: '',
      horsepower_fiscal_max: '',
      seller_type: '',
      first_registration: false,
      nb_doors: '',
      nb_seats: '',
      color: '',
      color_interior: '',
      metallic_color: false,
      emission_class: '',
      critair: '',
      co2_max: '',
      technical_control_ok: false,
      non_smoker: false,
      no_accident: false,
      service_history: false,
      warranty: false,
      manufacturer_warranty: false,
      climate_control: '',
      leather_interior: false,
      sunroof: false,
      panoramic_roof: false,
      heated_seats: false,
      electric_seats: false,
      parking_sensors: false,
      parking_camera: false,
      gps: false,
      bluetooth: false,
      apple_carplay: false,
      android_auto: false,
      cruise_control: false,
      adaptive_cruise_control: false,
      keyless_entry: false,
      head_up_display: false,
      abs: false,
      esp: false,
      airbags: '',
      lane_assist: false,
      blind_spot: false,
      automatic_emergency_braking: false,
      alloy_wheels: false,
      led_headlights: false,
      xenon_headlights: false,
      tow_bar: false,
      ski_rack: false,
      roof_rack: false,
      cylinders: '',
      engine_size: '',
      drive_type: '',
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

      {/* Bouton pour afficher plus de filtres */}
      <div style={styles.section}>
        <button
          type="button"
          onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          style={styles.toggleButton}
        >
          {showAdvancedFilters ? '− Masquer les filtres avancés' : '+ Afficher les filtres avancés'}
        </button>
      </div>

      {/* Filtres avancés (repliables) */}
      {showAdvancedFilters && (
        <div style={styles.advancedSection}>
          {/* Carrosserie */}
          <div style={styles.field}>
            <label style={styles.label}>Type de carrosserie</label>
            <select
              value={filters.body_type}
              onChange={(e) => handleChange('body_type', e.target.value)}
              style={styles.select}
            >
              <option value="">Tous</option>
              <option value="berline">Berline</option>
              <option value="break">Break</option>
              <option value="suv">SUV</option>
              <option value="coupe">Coupé</option>
              <option value="cabriolet">Cabriolet</option>
              <option value="monospace">Monospace</option>
              <option value="utilitaire">Utilitaire</option>
            </select>
          </div>

          {/* Puissance */}
          <div style={styles.section}>
            <label style={styles.label}>Puissance (chevaux)</label>
            <div style={styles.row}>
              <div style={styles.field}>
                <input
                  type="number"
                  placeholder="Min"
                  value={filters.horsepower_min}
                  onChange={(e) => handleChange('horsepower_min', e.target.value)}
                  style={styles.input}
                  min="0"
                />
              </div>
              <span style={styles.separator}>→</span>
              <div style={styles.field}>
                <input
                  type="number"
                  placeholder="Max"
                  value={filters.horsepower_max}
                  onChange={(e) => handleChange('horsepower_max', e.target.value)}
                  style={styles.input}
                  min="0"
                />
              </div>
            </div>
          </div>

          {/* Puissance fiscale */}
          <div style={styles.section}>
            <label style={styles.label}>Puissance fiscale (CV)</label>
            <div style={styles.row}>
              <div style={styles.field}>
                <input
                  type="number"
                  placeholder="Min"
                  value={filters.horsepower_fiscal_min}
                  onChange={(e) => handleChange('horsepower_fiscal_min', e.target.value)}
                  style={styles.input}
                  min="0"
                />
              </div>
              <span style={styles.separator}>→</span>
              <div style={styles.field}>
                <input
                  type="number"
                  placeholder="Max"
                  value={filters.horsepower_fiscal_max}
                  onChange={(e) => handleChange('horsepower_fiscal_max', e.target.value)}
                  style={styles.input}
                  min="0"
                />
              </div>
            </div>
          </div>

          {/* Type de vendeur */}
          <div style={styles.field}>
            <label style={styles.label}>Type de vendeur</label>
            <select
              value={filters.seller_type}
              onChange={(e) => handleChange('seller_type', e.target.value)}
              style={styles.select}
            >
              <option value="">Tous</option>
              <option value="particulier">Particulier</option>
              <option value="professionnel">Professionnel</option>
            </select>
          </div>

          {/* Caractéristiques */}
          <div style={styles.row}>
            <div style={styles.field}>
              <label style={styles.label}>Nombre de portes</label>
              <select
                value={filters.nb_doors}
                onChange={(e) => handleChange('nb_doors', e.target.value)}
                style={styles.select}
              >
                <option value="">Toutes</option>
                <option value="2">2 portes</option>
                <option value="3">3 portes</option>
                <option value="4">4 portes</option>
                <option value="5">5 portes</option>
              </select>
            </div>

            <div style={styles.field}>
              <label style={styles.label}>Nombre de places</label>
              <select
                value={filters.nb_seats}
                onChange={(e) => handleChange('nb_seats', e.target.value)}
                style={styles.select}
              >
                <option value="">Toutes</option>
                <option value="2">2 places</option>
                <option value="4">4 places</option>
                <option value="5">5 places</option>
                <option value="7">7 places</option>
                <option value="9">9 places</option>
              </select>
            </div>
          </div>

          {/* Couleur */}
          <div style={styles.field}>
            <label style={styles.label}>Couleur</label>
            <input
              type="text"
              placeholder="Ex: noir, blanc, rouge..."
              value={filters.color}
              onChange={(e) => handleChange('color', e.target.value)}
              style={styles.input}
            />
          </div>

          {/* Options historique */}
          <div style={styles.section}>
            <label style={styles.label}>Historique et garanties</label>
            <div style={styles.checkboxGroup}>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.first_registration}
                  onChange={(e) => handleChange('first_registration', e.target.checked)}
                />
                Première main
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.no_accident}
                  onChange={(e) => handleChange('no_accident', e.target.checked)}
                />
                Jamais accidenté
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.service_history}
                  onChange={(e) => handleChange('service_history', e.target.checked)}
                />
                Carnet d'entretien
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.warranty}
                  onChange={(e) => handleChange('warranty', e.target.checked)}
                />
                Sous garantie
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.technical_control_ok}
                  onChange={(e) => handleChange('technical_control_ok', e.target.checked)}
                />
                Contrôle technique OK
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Bouton pour afficher les équipements */}
      <div style={styles.section}>
        <button
          type="button"
          onClick={() => setShowEquipmentFilters(!showEquipmentFilters)}
          style={styles.toggleButton}
        >
          {showEquipmentFilters ? '− Masquer les équipements' : '+ Afficher les équipements'}
        </button>
      </div>

      {/* Filtres équipements (repliables) */}
      {showEquipmentFilters && (
        <div style={styles.advancedSection}>
          {/* Équipements confort */}
          <div style={styles.section}>
            <label style={styles.label}>Confort</label>
            <div style={styles.checkboxGroup}>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.leather_interior}
                  onChange={(e) => handleChange('leather_interior', e.target.checked)}
                />
                Intérieur cuir
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.sunroof}
                  onChange={(e) => handleChange('sunroof', e.target.checked)}
                />
                Toit ouvrant
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.panoramic_roof}
                  onChange={(e) => handleChange('panoramic_roof', e.target.checked)}
                />
                Toit panoramique
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.heated_seats}
                  onChange={(e) => handleChange('heated_seats', e.target.checked)}
                />
                Sièges chauffants
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.parking_camera}
                  onChange={(e) => handleChange('parking_camera', e.target.checked)}
                />
                Caméra de recul
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.parking_sensors}
                  onChange={(e) => handleChange('parking_sensors', e.target.checked)}
                />
                Capteurs de stationnement
              </label>
            </div>
          </div>

          {/* Équipements technologie */}
          <div style={styles.section}>
            <label style={styles.label}>Technologie</label>
            <div style={styles.checkboxGroup}>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.gps}
                  onChange={(e) => handleChange('gps', e.target.checked)}
                />
                GPS / Navigation
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.bluetooth}
                  onChange={(e) => handleChange('bluetooth', e.target.checked)}
                />
                Bluetooth
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.apple_carplay}
                  onChange={(e) => handleChange('apple_carplay', e.target.checked)}
                />
                Apple CarPlay
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.android_auto}
                  onChange={(e) => handleChange('android_auto', e.target.checked)}
                />
                Android Auto
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.cruise_control}
                  onChange={(e) => handleChange('cruise_control', e.target.checked)}
                />
                Régulateur de vitesse
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.keyless_entry}
                  onChange={(e) => handleChange('keyless_entry', e.target.checked)}
                />
                Démarrage sans clé
              </label>
            </div>
          </div>

          {/* Équipements sécurité */}
          <div style={styles.section}>
            <label style={styles.label}>Sécurité</label>
            <div style={styles.checkboxGroup}>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.abs}
                  onChange={(e) => handleChange('abs', e.target.checked)}
                />
                ABS
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.esp}
                  onChange={(e) => handleChange('esp', e.target.checked)}
                />
                ESP
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.lane_assist}
                  onChange={(e) => handleChange('lane_assist', e.target.checked)}
                />
                Aide au maintien de voie
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.blind_spot}
                  onChange={(e) => handleChange('blind_spot', e.target.checked)}
                />
                Détection angle mort
              </label>
            </div>
          </div>

          {/* Autres équipements */}
          <div style={styles.section}>
            <label style={styles.label}>Autres</label>
            <div style={styles.checkboxGroup}>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.alloy_wheels}
                  onChange={(e) => handleChange('alloy_wheels', e.target.checked)}
                />
                Jantes alliage
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.led_headlights}
                  onChange={(e) => handleChange('led_headlights', e.target.checked)}
                />
                Phares LED
              </label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.tow_bar}
                  onChange={(e) => handleChange('tow_bar', e.target.checked)}
                />
                Attelage
              </label>
            </div>
          </div>
        </div>
      )}

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
  },
  toggleButton: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#f6f8fa',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    textAlign: 'left',
    color: '#0366d6'
  },
  advancedSection: {
    padding: '20px',
    backgroundColor: '#f6f8fa',
    borderRadius: '6px',
    marginBottom: '20px'
  }
}
