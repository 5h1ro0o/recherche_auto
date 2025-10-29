// frontend/src/ui/SearchFiltersForm.jsx
import React, { useState } from 'react';
import './SearchFiltersForm.css';

const MAKES = [
  'Peugeot', 'Renault', 'Citroën', 'Volkswagen', 'BMW', 'Mercedes', 'Audi',
  'Ford', 'Toyota', 'Nissan', 'Opel', 'Fiat', 'Seat', 'Hyundai', 'Kia'
];

const FUEL_TYPES = ['essence', 'diesel', 'electrique', 'hybride', 'gpl'];
const TRANSMISSIONS = ['manuelle', 'automatique'];

export default function SearchFiltersForm({ onSearch, loading }) {
  const [filters, setFilters] = useState({
    make: '',
    model: '',
    price_min: '',
    price_max: '',
    year_min: '',
    year_max: '',
    mileage_max: '',
    fuel_type: '',
    transmission: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Construire l'objet de filtres sans les valeurs vides
    const activeFilters = {};
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== '') {
        activeFilters[key] = value;
      }
    });

    onSearch(activeFilters);
  };

  const handleReset = () => {
    setFilters({
      make: '',
      model: '',
      price_min: '',
      price_max: '',
      year_min: '',
      year_max: '',
      mileage_max: '',
      fuel_type: '',
      transmission: ''
    });
  };

  return (
    <form className="search-filters-form" onSubmit={handleSubmit}>
      <h3>Rechercher un véhicule</h3>
      <p className="form-subtitle">
        Renseignez vos critères de recherche ci-dessous
      </p>

      <div className="filters-grid">
        {/* Marque */}
        <div className="form-group">
          <label htmlFor="make">Marque</label>
          <select
            id="make"
            name="make"
            value={filters.make}
            onChange={handleChange}
          >
            <option value="">Toutes les marques</option>
            {MAKES.map(make => (
              <option key={make} value={make}>{make}</option>
            ))}
          </select>
        </div>

        {/* Modèle */}
        <div className="form-group">
          <label htmlFor="model">Modèle</label>
          <input
            type="text"
            id="model"
            name="model"
            placeholder="Ex: 308, Clio..."
            value={filters.model}
            onChange={handleChange}
          />
        </div>

        {/* Prix minimum */}
        <div className="form-group">
          <label htmlFor="price_min">Prix minimum (€)</label>
          <input
            type="number"
            id="price_min"
            name="price_min"
            placeholder="Ex: 5000"
            min="0"
            step="1000"
            value={filters.price_min}
            onChange={handleChange}
          />
        </div>

        {/* Prix maximum */}
        <div className="form-group">
          <label htmlFor="price_max">Prix maximum (€)</label>
          <input
            type="number"
            id="price_max"
            name="price_max"
            placeholder="Ex: 20000"
            min="0"
            step="1000"
            value={filters.price_max}
            onChange={handleChange}
          />
        </div>

        {/* Année minimum */}
        <div className="form-group">
          <label htmlFor="year_min">Année minimum</label>
          <input
            type="number"
            id="year_min"
            name="year_min"
            placeholder="Ex: 2015"
            min="1990"
            max={new Date().getFullYear()}
            value={filters.year_min}
            onChange={handleChange}
          />
        </div>

        {/* Année maximum */}
        <div className="form-group">
          <label htmlFor="year_max">Année maximum</label>
          <input
            type="number"
            id="year_max"
            name="year_max"
            placeholder="Ex: 2023"
            min="1990"
            max={new Date().getFullYear()}
            value={filters.year_max}
            onChange={handleChange}
          />
        </div>

        {/* Kilométrage maximum */}
        <div className="form-group">
          <label htmlFor="mileage_max">Kilométrage max (km)</label>
          <input
            type="number"
            id="mileage_max"
            name="mileage_max"
            placeholder="Ex: 100000"
            min="0"
            step="10000"
            value={filters.mileage_max}
            onChange={handleChange}
          />
        </div>

        {/* Carburant */}
        <div className="form-group">
          <label htmlFor="fuel_type">Carburant</label>
          <select
            id="fuel_type"
            name="fuel_type"
            value={filters.fuel_type}
            onChange={handleChange}
          >
            <option value="">Tous</option>
            {FUEL_TYPES.map(fuel => (
              <option key={fuel} value={fuel}>
                {fuel.charAt(0).toUpperCase() + fuel.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Transmission */}
        <div className="form-group">
          <label htmlFor="transmission">Transmission</label>
          <select
            id="transmission"
            name="transmission"
            value={filters.transmission}
            onChange={handleChange}
          >
            <option value="">Toutes</option>
            {TRANSMISSIONS.map(trans => (
              <option key={trans} value={trans}>
                {trans.charAt(0).toUpperCase() + trans.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-actions">
        <button
          type="submit"
          className="btn-search"
          disabled={loading}
        >
          {loading ? 'Recherche en cours...' : 'Rechercher'}
        </button>
        <button
          type="button"
          className="btn-reset"
          onClick={handleReset}
          disabled={loading}
        >
          Réinitialiser
        </button>
      </div>

      {loading && (
        <div className="search-info">
          Scraping de LeBonCoin, La Centrale et AutoScout24 en cours...
        </div>
      )}
    </form>
  );
}
