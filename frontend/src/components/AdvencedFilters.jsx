import React, { useState } from 'react';
import { MapPin, Sliders, X } from 'lucide-react';

export default function AdvancedFilters({ onApply, onClose }) {
  const [filters, setFilters] = useState({
    price: [0, 100000],
    mileage: [0, 300000],
    year: [2000, new Date().getFullYear()],
    makes: [],
    fuelTypes: [],
    transmissions: [],
    location: {
      lat: 48.8566,
      lng: 2.3522,
      radius: 50
    }
  });

  const [showMap, setShowMap] = useState(false);

  const makes = ['Peugeot', 'Renault', 'Citroën', 'Volkswagen', 'BMW', 'Mercedes', 'Audi', 'Toyota', 'Ford'];
  const fuelTypes = ['Essence', 'Diesel', 'Électrique', 'Hybride', 'GPL'];
  const transmissions = ['Manuelle', 'Automatique', 'Semi-automatique'];

  function handleRangeChange(key, index, value) {
    const newRange = [...filters[key]];
    newRange[index] = parseInt(value);
    setFilters({ ...filters, [key]: newRange });
  }

  function toggleArrayFilter(key, value) {
    const current = filters[key];
    const newValue = current.includes(value)
      ? current.filter(v => v !== value)
      : [...current, value];
    setFilters({ ...filters, [key]: newValue });
  }

  function handleApply() {
    onApply(filters);
    onClose();
  }

  function handleReset() {
    setFilters({
      price: [0, 100000],
      mileage: [0, 300000],
      year: [2000, new Date().getFullYear()],
      makes: [],
      fuelTypes: [],
      transmissions: [],
      location: { lat: 48.8566, lng: 2.3522, radius: 50 }
    });
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '100%',
      maxWidth: '480px',
      background: 'white',
      boxShadow: '-4px 0 24px rgba(0,0,0,0.15)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      animation: 'slideInRight 0.3s ease'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '20px 24px',
        borderBottom: '2px solid #f0f0f0',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Sliders size={24} />
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 700 }}>
            Filtres Avancés
          </h2>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'rgba(255,255,255,0.2)',
            border: 'none',
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.3)'}
          onMouseLeave={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
        >
          <X size={20} color="white" />
        </button>
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px'
      }}>
        {/* Prix */}
        <FilterSection title="💰 Prix" icon="💰">
          <RangeSlider
            min={0}
            max={100000}
            step={1000}
            value={filters.price}
            onChange={(idx, val) => handleRangeChange('price', idx, val)}
            formatValue={(v) => `${(v / 1000).toFixed(0)}k €`}
          />
        </FilterSection>

        {/* Kilométrage */}
        <FilterSection title="🛣️ Kilométrage">
          <RangeSlider
            min={0}
            max={300000}
            step={5000}
            value={filters.mileage}
            onChange={(idx, val) => handleRangeChange('mileage', idx, val)}
            formatValue={(v) => `${(v / 1000).toFixed(0)}k km`}
          />
        </FilterSection>

        {/* Année */}
        <FilterSection title="📅 Année">
          <RangeSlider
            min={2000}
            max={new Date().getFullYear()}
            step={1}
            value={filters.year}
            onChange={(idx, val) => handleRangeChange('year', idx, val)}
            formatValue={(v) => v.toString()}
          />
        </FilterSection>

        {/* Marques */}
        <FilterSection title="🏭 Marques">
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {makes.map(make => (
              <FilterChip
                key={make}
                label={make}
                active={filters.makes.includes(make)}
                onClick={() => toggleArrayFilter('makes', make)}
              />
            ))}
          </div>
        </FilterSection>

        {/* Carburant */}
        <FilterSection title="⛽ Carburant">
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {fuelTypes.map(fuel => (
              <FilterChip
                key={fuel}
                label={fuel}
                active={filters.fuelTypes.includes(fuel)}
                onClick={() => toggleArrayFilter('fuelTypes', fuel)}
              />
            ))}
          </div>
        </FilterSection>

        {/* Transmission */}
        <FilterSection title="⚙️ Transmission">
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {transmissions.map(trans => (
              <FilterChip
                key={trans}
                label={trans}
                active={filters.transmissions.includes(trans)}
                onClick={() => toggleArrayFilter('transmissions', trans)}
              />
            ))}
          </div>
        </FilterSection>

        {/* Localisation */}
        <FilterSection title="📍 Rayon de recherche">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '12px'
          }}>
            <MapPin size={20} color="#667eea" />
            <div style={{ flex: 1 }}>
              <input
                type="range"
                min="10"
                max="500"
                step="10"
                value={filters.location.radius}
                onChange={(e) => setFilters({
                  ...filters,
                  location: { ...filters.location, radius: parseInt(e.target.value) }
                })}
                style={{
                  width: '100%',
                  accentColor: '#667eea'
                }}
              />
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '13px',
                color: '#6a737d',
                marginTop: '4px'
              }}>
                <span>10 km</span>
                <span style={{ fontWeight: 600, color: '#667eea' }}>
                  {filters.location.radius} km
                </span>
                <span>500 km</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => setShowMap(!showMap)}
            style={{
              width: '100%',
              padding: '10px',
              background: '#f8f9fa',
              border: '1px solid #e1e4e8',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#e1e4e8'
              e.target.style.borderColor = '#667eea'
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#f8f9fa'
              e.target.style.borderColor = '#e1e4e8'
            }}
          >
            {showMap ? '🗺️ Masquer la carte' : '🗺️ Choisir sur la carte'}
          </button>
          {showMap && (
            <div style={{
              marginTop: '12px',
              height: '200px',
              background: '#e0e7ff',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#667eea',
              fontSize: '14px',
              fontWeight: 500
            }}>
              Carte interactive (à intégrer)
            </div>
          )}
        </FilterSection>
      </div>

      {/* Footer Actions */}
      <div style={{
        padding: '20px 24px',
        borderTop: '2px solid #f0f0f0',
        display: 'flex',
        gap: '12px',
        background: '#f8f9fa'
      }}>
        <button
          onClick={handleReset}
          style={{
            flex: 1,
            padding: '12px',
            background: 'white',
            border: '2px solid #e1e4e8',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = '#f0f0f0'
            e.target.style.borderColor = '#d1d5da'
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'white'
            e.target.style.borderColor = '#e1e4e8'
          }}
        >
          🔄 Réinitialiser
        </button>
        <button
          onClick={handleApply}
          style={{
            flex: 2,
            padding: '12px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            color: 'white',
            cursor: 'pointer',
            transition: 'all 0.3s',
            boxShadow: '0 4px 12px rgba(102,126,234,0.3)'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)'
            e.target.style.boxShadow = '0 6px 20px rgba(102,126,234,0.4)'
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)'
            e.target.style.boxShadow = '0 4px 12px rgba(102,126,234,0.3)'
          }}
        >
          ✅ Appliquer les filtres
        </button>
      </div>

      <style>{`
        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}

function FilterSection({ title, children }) {
  return (
    <div style={{
      marginBottom: '28px',
      paddingBottom: '28px',
      borderBottom: '1px solid #e1e4e8'
    }}>
      <h3 style={{
        margin: '0 0 16px 0',
        fontSize: '15px',
        fontWeight: 600,
        color: '#24292e',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        {title}
      </h3>
      {children}
    </div>
  );
}

function RangeSlider({ min, max, step, value, onChange, formatValue }) {
  return (
    <div>
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '12px'
      }}>
        <input
          type="number"
          value={value[0]}
          onChange={(e) => onChange(0, e.target.value)}
          min={min}
          max={value[1]}
          step={step}
          style={{
            flex: 1,
            padding: '8px 12px',
            border: '2px solid #e1e4e8',
            borderRadius: '8px',
            fontSize: '14px'
          }}
        />
        <span style={{
          alignSelf: 'center',
          color: '#6a737d',
          fontSize: '14px',
          fontWeight: 500
        }}>
          à
        </span>
        <input
          type="number"
          value={value[1]}
          onChange={(e) => onChange(1, e.target.value)}
          min={value[0]}
          max={max}
          step={step}
          style={{
            flex: 1,
            padding: '8px 12px',
            border: '2px solid #e1e4e8',
            borderRadius: '8px',
            fontSize: '14px'
          }}
        />
      </div>
      <div style={{ position: 'relative', padding: '0 8px' }}>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value[0]}
          onChange={(e) => onChange(0, e.target.value)}
          style={{
            position: 'absolute',
            width: '100%',
            pointerEvents: 'none',
            appearance: 'none',
            background: 'transparent',
            zIndex: 2
          }}
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value[1]}
          onChange={(e) => onChange(1, e.target.value)}
          style={{
            position: 'relative',
            width: '100%',
            appearance: 'none',
            background: 'linear-gradient(to right, #e0e0e0 0%, #667eea 0%, #667eea 100%, #e0e0e0 100%)',
            height: '6px',
            borderRadius: '3px',
            outline: 'none'
          }}
        />
      </div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '13px',
        color: '#6a737d',
        marginTop: '8px'
      }}>
        <span>{formatValue(value[0])}</span>
        <span>{formatValue(value[1])}</span>
      </div>
    </div>
  );
}

function FilterChip({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '8px 16px',
        background: active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white',
        color: active ? 'white' : '#24292e',
        border: active ? 'none' : '2px solid #e1e4e8',
        borderRadius: '20px',
        fontSize: '13px',
        fontWeight: active ? 600 : 500,
        cursor: 'pointer',
        transition: 'all 0.2s',
        whiteSpace: 'nowrap'
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.target.style.background = '#f8f9fa'
          e.target.style.borderColor = '#667eea'
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.target.style.background = 'white'
          e.target.style.borderColor = '#e1e4e8'
        }
      }}
    >
      {label}
    </button>
  );
}