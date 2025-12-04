import React, { useState } from 'react'
import AdvancedSearchForm from '../components/AdvancedSearchForm'
import EnrichedResults from '../ui/Results'

export default function AdvancedSearchPage() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [searchStats, setSearchStats] = useState(null)
  const [error, setError] = useState(null)

  const handleSearch = async (filters) => {
    setLoading(true)
    setError(null)
    setResults([])
    setSearchStats(null)

    console.log('Recherche avec filtres:', filters)

    try {
      const response = await fetch('http://localhost:8000/api/search-advanced/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...filters,
          max_pages: 20
        })
      })

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
      }

      const data = await response.json()

      console.log('Résultats reçus:', data)

      setResults(data.results || [])
      setSearchStats({
        total: data.total_results,
        duration: data.duration,
        sources: data.sources_stats,
        filters: data.filters_applied
      })

    } catch (err) {
      console.error('Erreur recherche:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-main">
      <div style={{
        maxWidth: 'var(--container-2xl)',
        margin: '0 auto'
      }}>
        {/* Formulaire de recherche */}
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <AdvancedSearchForm onSearch={handleSearch} loading={loading} />
        </div>

        {/* Statistiques de recherche */}
        {searchStats && (
          <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 'var(--space-4)',
              padding: 'var(--space-5)'
            }}>
              <h3 style={{
                margin: 0,
                fontSize: '20px',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--text-primary)',
                letterSpacing: '-0.01em'
              }}>
                {searchStats.total} résultat{searchStats.total > 1 ? 's' : ''} trouvé{searchStats.total > 1 ? 's' : ''}
              </h3>
              <span style={{
                fontSize: '14px',
                color: 'var(--text-secondary)',
                fontWeight: 'var(--font-weight-medium)'
              }}>
                {searchStats.duration.toFixed(2)}s
              </span>
            </div>

            <div style={{
              display: 'flex',
              gap: 'var(--space-6)',
              marginBottom: 'var(--space-4)',
              paddingBottom: 'var(--space-4)',
              borderBottom: '1px solid var(--border-light)',
              padding: '0 var(--space-5)'
            }}>
              {Object.entries(searchStats.sources).map(([source, stats]) => (
                <div key={source} style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 'var(--space-1)'
                }}>
                  <span style={{
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-semibold)',
                    color: 'var(--text-primary)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {source === 'leboncoin' ? 'LeBonCoin' : 'AutoScout24'}
                  </span>
                  <span style={{
                    fontSize: '13px',
                    color: stats.success ? '#059669' : 'var(--red-accent)',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    {stats.success ? `${stats.count} annonces` : stats.error}
                  </span>
                </div>
              ))}
            </div>

            {/* Filtres appliqués */}
            <div style={{
              fontSize: '14px',
              color: 'var(--text-secondary)',
              padding: '0 var(--space-5) var(--space-5) var(--space-5)'
            }}>
              <strong style={{
                color: 'var(--text-primary)',
                fontWeight: 'var(--font-weight-semibold)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontSize: '12px'
              }}>
                Filtres appliqués
              </strong>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 'var(--space-2)',
                marginTop: 'var(--space-3)'
              }}>
                {searchStats.filters.make && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Marque: {searchStats.filters.make}
                  </span>
                )}
                {searchStats.filters.model && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Modèle: {searchStats.filters.model}
                  </span>
                )}
                {searchStats.filters.price_min && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Prix min: {searchStats.filters.price_min}€
                  </span>
                )}
                {searchStats.filters.price_max && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Prix max: {searchStats.filters.price_max}€
                  </span>
                )}
                {searchStats.filters.year_min && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Année min: {searchStats.filters.year_min}
                  </span>
                )}
                {searchStats.filters.year_max && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Année max: {searchStats.filters.year_max}
                  </span>
                )}
                {searchStats.filters.fuel_type && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Carburant: {searchStats.filters.fuel_type}
                  </span>
                )}
                {searchStats.filters.transmission && (
                  <span style={{
                    padding: 'var(--space-1) var(--space-3)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}>
                    Transmission: {searchStats.filters.transmission}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Erreur */}
        {error && (
          <div style={{
            background: 'var(--red-accent-light)',
            border: '1px solid var(--red-accent)',
            padding: 'var(--space-5)',
            marginBottom: 'var(--space-6)'
          }}>
            <h3 style={{
              margin: '0 0 var(--space-2) 0',
              fontSize: '18px',
              color: 'var(--red-accent)',
              fontWeight: 'var(--font-weight-semibold)'
            }}>
              Erreur
            </h3>
            <p style={{ margin: 0, color: 'var(--red-accent)' }}>{error}</p>
          </div>
        )}

        {/* Résultats */}
        {!loading && !error && (
          <div className="card">
            <div className="card-body">
              <EnrichedResults
                loading={loading}
                results={results}
                total={results.length}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
