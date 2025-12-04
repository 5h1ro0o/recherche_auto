// frontend/src/Pages/SearchPage.jsx
import React, { useState } from 'react'
import SearchBar from '../ui/SearchBar'
import Results from '../ui/Results'
import ChatBot from '../components/ChatBot'
import { useSearch } from '../services/UseSearch'

export default function SearchPage() {
  const [q, setQ] = useState('')
  const [filters, setFilters] = useState({})
  const [page, setPage] = useState(1)
  const [results, setResults] = useState([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)

  const { refetch } = useSearch(q, page)

  function onSearch(term) {
    setQ(term)
    setPage(1)
    setIsLoading(true)
    refetch().finally(() => setIsLoading(false))
  }

  // Callback quand le chatbot détecte des filtres
  function handleFiltersDetected(detectedFilters) {
    console.log('Filtres détectés par IA:', detectedFilters)
    setFilters(detectedFilters)
  }

  // Callback quand le chatbot retourne des résultats
  function handleSearchResults(hits, totalResults) {
    setResults(hits)
    setTotal(totalResults)
    setIsLoading(false)
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--gray-50)',
      paddingBottom: 'var(--space-16)'
    }}>
      {/* Header Section */}
      <div style={{
        background: 'var(--white)',
        color: 'var(--text-primary)',
        padding: 'var(--space-16) var(--space-6)',
        textAlign: 'center',
        marginBottom: 'var(--space-10)',
        borderBottom: '1px solid var(--border-light)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Gloss overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '200px',
          background: 'var(--gloss-overlay)',
          pointerEvents: 'none'
        }} />

        <h1 style={{
          fontSize: '48px',
          fontWeight: 'var(--font-weight-bold)',
          margin: '0 0 var(--space-4) 0',
          lineHeight: 1.1,
          letterSpacing: '-0.02em',
          position: 'relative',
          zIndex: 1
        }}>
          Recherche de véhicules
        </h1>
        <p style={{
          fontSize: '18px',
          margin: 0,
          color: 'var(--text-secondary)',
          fontWeight: 'var(--font-weight-medium)',
          position: 'relative',
          zIndex: 1
        }}>
          Utilisez la barre de recherche ou le chatbot pour trouver votre véhicule
        </p>
      </div>

      <SearchBar onSearch={onSearch} defaultValue={q} />

      {/* Affichage des filtres détectés */}
      {Object.keys(filters).length > 0 && (
        <div style={{
          maxWidth: 'var(--container-lg)',
          margin: '0 auto var(--space-8) auto',
          padding: '0 var(--space-5)'
        }}>
          <div style={{
            background: 'var(--white)',
            border: '1px solid var(--border-light)',
            padding: 'var(--space-5)',
            boxShadow: 'var(--shadow-gloss-sm)'
          }}>
            <h4 style={{
              fontSize: '14px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              margin: '0 0 var(--space-4) 0',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Filtres actifs
            </h4>
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 'var(--space-2)'
            }}>
              {Object.entries(filters).map(([key, value]) => (
                <span
                  key={key}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 'var(--space-2)',
                    background: 'var(--red-accent-light)',
                    color: 'var(--red-accent)',
                    padding: 'var(--space-1) var(--space-3)',
                    fontSize: '13px',
                    fontWeight: 'var(--font-weight-medium)'
                  }}
                >
                  <strong>{key}:</strong> {value}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      <div style={{
        maxWidth: 'var(--container-xl)',
        margin: '0 auto',
        padding: '0 var(--space-5)'
      }}>
        <Results
          loading={isLoading}
          results={results.length > 0 ? results : []}
          total={total}
          page={page}
          onPageChange={setPage}
        />
      </div>

      {/* ChatBot flottant */}
      <ChatBot
        onFiltersDetected={handleFiltersDetected}
        onSearchResults={handleSearchResults}
      />
    </div>
  )
}
