import React, { useState } from 'react'
import { Link } from 'react-router-dom'

// Composant principal Results enrichi
export default function EnrichedResults({ loading, results = [], total = 0, page = 1, onPageChange }) {
  const [quickViewVehicle, setQuickViewVehicle] = useState(null)

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
        <p style={{ color: '#6a737d' }}>Chargement des résultats...</p>
      </div>
    )
  }

  if (!results || results.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>🔍</div>
        <h3 style={{ fontSize: '24px', color: '#24292e', marginBottom: '12px' }}>
          Aucun résultat trouvé
        </h3>
        <p style={{ color: '#6a737d', fontSize: '16px' }}>
          Essayez d'élargir vos critères de recherche
        </p>
      </div>
    )
  }
  return (
    <div>
      <div style={{ marginBottom: '16px', color: '#586069' }}>
        {total} résultat{total > 1 ? 's' : ''} trouvé{total > 1 ? 's' : ''}.
      </div>
      <div>
        {results.map((vehicle) => (
          <div
          