// frontend/src/Pages/SearchPage.jsx
import React, { useState } from 'react'
import SearchFiltersForm from '../ui/SearchFiltersForm'
import Results from '../ui/Results'
import ChatBot from '../components/ChatBot'
import URLImport from '../components/URLImport'
import client from '../services/api'

export default function SearchPage() {
  const [results, setResults] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [scrapingStats, setScrapingStats] = useState(null)

  async function handleSearch(criteriaFilters) {
    setLoading(true)
    setError(null)

    try {
      // Construire la query à partir des filtres
      // Si une marque et modèle sont fournis, créer une query
      let query = '';
      if (criteriaFilters.make) {
        query = criteriaFilters.make;
        if (criteriaFilters.model) {
          query += ' ' + criteriaFilters.model;
        }
      }

      // Appeler l'API de recherche SANS scraping (DB uniquement)
      const response = await client.post('/search', {
        q: query || '',
        filters: criteriaFilters,
        page: page,
        enable_scraping: false,  // DÉSACTIVÉ - recherche DB uniquement
        scraping_mode: 'never'
      });

      setResults(response.data.results || []);
      setTotal(response.data.total || 0);
      setScrapingStats({
        from_db: response.data.from_db || 0,
        from_scraping: response.data.from_scraping || 0,
        sources: response.data.sources || {}
      });

    } catch (err) {
      console.error('Erreur lors de la recherche:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la recherche');
    } finally {
      setLoading(false);
    }
  }

  // Callback quand le chatbot détecte des filtres
  function handleFiltersDetected(detectedFilters) {
    console.log('Filtres détectés par IA:', detectedFilters)
    handleSearch(detectedFilters)
  }

  // Callback quand le chatbot retourne des résultats
  function handleSearchResults(hits, totalResults) {
    console.log('Résultats du chatbot:', hits, totalResults)
  }

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>Recherche de véhicules</h1>
        <p className="search-subtitle">
          🔍 Recherchez dans notre base de données ou importez une annonce depuis une URL
        </p>
      </div>

      {/* Import d'URL */}
      <URLImport onImportSuccess={(data) => {
        // Après import, recharger la recherche
        handleSearch({});
      }} />

      {/* Formulaire de recherche par critères */}
      <SearchFiltersForm onSearch={handleSearch} loading={loading} />

      {/* Affichage d'erreur si nécessaire */}
      {error && (
        <div className="search-error" style={{ padding: '20px', margin: '20px', backgroundColor: '#fee', borderRadius: '8px' }}>
          <p style={{ color: '#c00' }}>❌ Erreur: {error}</p>
        </div>
      )}

      {/* Statistiques de scraping */}
      {scrapingStats && (
        <div className="scraping-stats" style={{ padding: '15px', margin: '20px 0', backgroundColor: '#e8f5e9', borderRadius: '8px' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#2e7d32' }}>📊 Statistiques de recherche</h4>
          <p style={{ margin: '5px 0' }}>
            <strong>Résultats trouvés:</strong> {total} annonces
          </p>
          <p style={{ margin: '5px 0' }}>
            <strong>Base de données:</strong> {scrapingStats.from_db} annonces
          </p>
          <p style={{ margin: '5px 0' }}>
            <strong>Scraping en temps réel:</strong> {scrapingStats.from_scraping} annonces
          </p>
          {scrapingStats.sources && Object.keys(scrapingStats.sources).length > 0 && (
            <p style={{ margin: '10px 0 0 0' }}>
              <strong>Sources:</strong>
              {Object.entries(scrapingStats.sources).map(([source, info]) => (
                <span key={source} style={{ marginLeft: '8px', padding: '4px 8px', background: info.success ? '#c8e6c9' : '#ffcdd2', borderRadius: '4px', fontSize: '12px' }}>
                  {source}: {info.count || 0}
                  {!info.success && ' (échec)'}
                </span>
              ))}
            </p>
          )}
        </div>
      )}

      {/* Résultats */}
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