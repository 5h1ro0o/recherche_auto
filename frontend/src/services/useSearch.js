// frontend/src/services/useSearch.js
import { useState, useEffect } from 'react';
import client from './api';

/**
 * Hook personnalisé pour la recherche de véhicules avec scraping
 * @param {string} query - Terme de recherche
 * @param {number} page - Numéro de page
 * @param {object} filters - Filtres additionnels
 * @param {boolean} enableScraping - Activer le scraping (défaut: true)
 * @param {string} scrapingMode - Mode de scraping: 'auto', 'always', 'never', 'db_first'
 */
export function useSearch(
  query = '',
  page = 1,
  filters = {},
  enableScraping = true,
  scrapingMode = 'always' // Par défaut, toujours scraper
) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSearch = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await client.post('/search', {
        q: query || '',
        filters: filters,
        page: page,
        enable_scraping: enableScraping,
        scraping_mode: scrapingMode
      });

      setData(response.data);
      return response.data;
    } catch (err) {
      console.error('Erreur lors de la recherche:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la recherche');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Déclencher la recherche automatiquement quand les paramètres changent
  useEffect(() => {
    // Ne déclencher que si on a une query OU des filtres
    if (query || Object.keys(filters).length > 0) {
      fetchSearch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, page, enableScraping, scrapingMode]);

  return {
    data,
    loading,
    error,
    refetch: fetchSearch
  };
}
