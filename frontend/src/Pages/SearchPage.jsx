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
  const [enableScraping, setEnableScraping] = useState(true) // ACTIVÉ pour scraper les plateformes
  const [scrapingMode, setScrapingMode] = useState('always') // 'always' = toujours scraper

  // Utiliser le hook useSearch pour récupérer les résultats
  const { data, loading, error, refetch } = useSearch(q, page, filters, enableScraping, scrapingMode)

  // Extraire les résultats et le total des données
  const results = data?.results || []
  const total = data?.total || 0

  function onSearch(term) {
    setQ(term)
    setPage(1)
    refetch()
  }

  // Callback quand le chatbot détecte des filtres
  function handleFiltersDetected(detectedFilters) {
    console.log('Filtres détectés par IA:', detectedFilters)
    setFilters(detectedFilters)
    setPage(1)
  }

  // Callback quand le chatbot retourne des résultats
  function handleSearchResults(hits, totalResults) {
    // Le chatbot peut aussi retourner des résultats directement
    // Dans ce cas, on pourrait les afficher
    console.log('Résultats du chatbot:', hits, totalResults)
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

      {/* Affichage d'erreur si nécessaire */}
      {error && (
        <div className="search-error" style={{ padding: '20px', margin: '20px', backgroundColor: '#fee', borderRadius: '8px' }}>
          <p style={{ color: '#c00' }}>❌ Erreur: {error}</p>
        </div>
      )}

      {/* Statistiques de scraping */}
      {data && data.sources && (
        <div className="scraping-stats" style={{ padding: '10px', margin: '10px 0', backgroundColor: '#e8f5e9', borderRadius: '8px' }}>
          <p>
            📊 Résultats: {data.from_db || 0} de la base de données + {data.from_scraping || 0} du scraping
            {data.sources && Object.keys(data.sources).length > 0 && (
              <span> (Sources: {Object.keys(data.sources).filter(k => data.sources[k].success).join(', ')})</span>
            )}
          </p>
        </div>
      )}

      <Results
        loading={loading}
        results={results}
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