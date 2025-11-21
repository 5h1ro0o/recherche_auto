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

    console.log('🔍 Recherche avec filtres:', filters)

    try {
      const response = await fetch('http://localhost:8000/api/search-advanced/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...filters,
          max_pages: 3
        })
      })

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
      }

      const data = await response.json()

      console.log('✅ Résultats reçus:', data)

      setResults(data.results || [])
      setSearchStats({
        total: data.total_results,
        duration: data.duration,
        sources: data.sources_stats,
        filters: data.filters_applied
      })

    } catch (err) {
      console.error('❌ Erreur recherche:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        {/* Formulaire de recherche */}
        <div style={styles.searchSection}>
          <AdvancedSearchForm onSearch={handleSearch} loading={loading} />
        </div>

        {/* Statistiques de recherche */}
        {searchStats && (
          <div style={styles.stats}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>
                📊 {searchStats.total} résultat{searchStats.total > 1 ? 's' : ''} trouvé{searchStats.total > 1 ? 's' : ''}
              </h3>
              <span style={styles.duration}>
                ⏱️ {searchStats.duration.toFixed(2)}s
              </span>
            </div>

            <div style={styles.sourcesStats}>
              {Object.entries(searchStats.sources).map(([source, stats]) => (
                <div key={source} style={styles.sourceStats}>
                  <span style={styles.sourceName}>
                    {source === 'leboncoin' ? '🟠 LeBonCoin' : '🔵 AutoScout24'}
                  </span>
                  <span style={{
                    ...styles.sourceCount,
                    color: stats.success ? '#28a745' : '#dc3545'
                  }}>
                    {stats.success ? `${stats.count} annonces` : `❌ ${stats.error}`}
                  </span>
                </div>
              ))}
            </div>

            {/* Filtres appliqués */}
            <div style={styles.appliedFilters}>
              <strong>Filtres appliqués:</strong>
              <div style={styles.filterTags}>
                {searchStats.filters.make && (
                  <span style={styles.filterTag}>Marque: {searchStats.filters.make}</span>
                )}
                {searchStats.filters.model && (
                  <span style={styles.filterTag}>Modèle: {searchStats.filters.model}</span>
                )}
                {searchStats.filters.price_min && (
                  <span style={styles.filterTag}>Prix min: {searchStats.filters.price_min}€</span>
                )}
                {searchStats.filters.price_max && (
                  <span style={styles.filterTag}>Prix max: {searchStats.filters.price_max}€</span>
                )}
                {searchStats.filters.year_min && (
                  <span style={styles.filterTag}>Année min: {searchStats.filters.year_min}</span>
                )}
                {searchStats.filters.year_max && (
                  <span style={styles.filterTag}>Année max: {searchStats.filters.year_max}</span>
                )}
                {searchStats.filters.fuel_type && (
                  <span style={styles.filterTag}>Carburant: {searchStats.filters.fuel_type}</span>
                )}
                {searchStats.filters.transmission && (
                  <span style={styles.filterTag}>Transmission: {searchStats.filters.transmission}</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Erreur */}
        {error && (
          <div style={styles.error}>
            <h3>❌ Erreur</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Résultats */}
        {!loading && !error && (
          <div style={styles.resultsSection}>
            <EnrichedResults
              loading={loading}
              results={results}
              total={results.length}
            />
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f6f8fa',
    paddingTop: '80px',
    paddingBottom: '40px'
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 20px'
  },
  searchSection: {
    marginBottom: '32px'
  },
  stats: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  statsHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px'
  },
  statsTitle: {
    margin: 0,
    fontSize: '20px',
    fontWeight: 600,
    color: '#24292e'
  },
  duration: {
    fontSize: '14px',
    color: '#6a737d'
  },
  sourcesStats: {
    display: 'flex',
    gap: '24px',
    marginBottom: '16px',
    paddingBottom: '16px',
    borderBottom: '1px solid #e1e4e8'
  },
  sourceStats: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  sourceName: {
    fontSize: '14px',
    fontWeight: 500,
    color: '#24292e'
  },
  sourceCount: {
    fontSize: '13px'
  },
  appliedFilters: {
    fontSize: '14px',
    color: '#586069'
  },
  filterTags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginTop: '8px'
  },
  filterTag: {
    padding: '4px 12px',
    backgroundColor: '#f1f8ff',
    color: '#0366d6',
    borderRadius: '16px',
    fontSize: '13px'
  },
  error: {
    backgroundColor: '#fff5f5',
    border: '1px solid #feb2b2',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '24px'
  },
  resultsSection: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  }
}
