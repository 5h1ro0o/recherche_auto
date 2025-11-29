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
      background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
      paddingBottom: '60px',
    }}>
      {/* Header Section */}
      <div style={{
        background: 'linear-gradient(135deg, #DC2626 0%, #DC2626 100%)',
        color: 'white',
        padding: '60px 20px',
        textAlign: 'center',
        marginBottom: '40px',
      }}>
        <h1 style={{
          fontSize: '42px',
          fontWeight: 700,
          margin: '0 0 16px 0',
          lineHeight: 1.2,
        }}>
          Recherche de véhicules
        </h1>
        <p style={{
          fontSize: '18px',
          margin: 0,
          opacity: 0.95,
        }}>
          🎯 Utilisez la barre de recherche ou le chatbot pour trouver votre véhicule
        </p>
      </div>

      <SearchBar onSearch={onSearch} defaultValue={q} />

      {/* Affichage des filtres détectés */}
      {Object.keys(filters).length > 0 && (
        <div style={{
          maxWidth: '800px',
          margin: '0 auto 32px auto',
          padding: '0 20px',
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
          }}>
            <h4 style={{
              fontSize: '16px',
              fontWeight: 600,
              color: '#222222',
              margin: '0 0 16px 0',
            }}>
              🔍 Filtres actifs
            </h4>
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
            }}>
              {Object.entries(filters).map(([key, value]) => (
                <span
                  key={key}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    background: '#FEE2E2',
                    color: '#DC2626',
                    padding: '6px 14px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: 500,
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
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '0 20px',
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