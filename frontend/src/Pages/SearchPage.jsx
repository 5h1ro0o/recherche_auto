// frontend/src/Pages/SearchPage.jsx
import React, { useState } from 'react'
import SearchBar from '../ui/SearchBar'
import Results from '../ui/Results'
import ChatBot from '../components/ChatBot'
import { useSearch } from '../services/useSearch'

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
    <div className="search-page">
      <div className="search-header">
        <h1>Recherche de véhicules</h1>
        <p className="search-subtitle">
          🎯 Utilisez la barre de recherche ou le chatbot pour trouver votre véhicule
        </p>
      </div>

      <SearchBar onSearch={onSearch} defaultValue={q} />

      {/* Affichage des filtres détectés */}
      {Object.keys(filters).length > 0 && (
        <div className="detected-filters">
          <h4>🔍 Filtres actifs :</h4>
          <div className="filters-list">
            {Object.entries(filters).map(([key, value]) => (
              <span key={key} className="filter-chip">
                <strong>{key}:</strong> {value}
              </span>
            ))}
          </div>
        </div>
      )}

      <Results
        loading={isLoading}
        results={results.length > 0 ? results : []}
        total={total}
        page={page}
        onPageChange={setPage}
      />

      {/* ChatBot flottant */}
      <ChatBot
        onFiltersDetected={handleFiltersDetected}
        onSearchResults={handleSearchResults}
      />
    </div>
  )
}