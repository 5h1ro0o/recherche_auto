// frontend/src/components/URLImport.jsx
import React, { useState } from 'react';
import client from '../services/api';
import './URLImport.css';

export default function URLImport({ onImportSuccess }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [importedVehicle, setImportedVehicle] = useState(null);

  async function handleImport(e) {
    e.preventDefault();

    if (!url.trim()) {
      setError('Veuillez entrer une URL');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await client.post('/import/url', {
        url: url.trim(),
        save_to_favorites: false
      });

      if (response.data.success) {
        setSuccess(true);
        setImportedVehicle(response.data.vehicle);
        setUrl(''); // Reset le champ

        // Appeler le callback si fourni
        if (onImportSuccess) {
          onImportSuccess(response.data);
        }

        // Auto-hide success message après 5s
        setTimeout(() => {
          setSuccess(false);
          setImportedVehicle(null);
        }, 5000);
      }
    } catch (err) {
      console.error('Erreur import URL:', err);
      setError(err.response?.data?.detail || 'Erreur lors de l\'import de l\'URL');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="url-import-container">
      <div className="url-import-card">
        <h3>📎 Importer une annonce</h3>
        <p className="import-subtitle">
          Collez l'URL d'une annonce LeBonCoin, La Centrale ou AutoScout24
        </p>

        <form onSubmit={handleImport} className="import-form">
          <div className="input-group">
            <input
              type="url"
              placeholder="https://www.leboncoin.fr/voitures/..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
              className="url-input"
            />
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="import-button"
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Import en cours...
                </>
              ) : (
                'Importer'
              )}
            </button>
          </div>

          <div className="supported-sites">
            <span className="sites-label">Sites supportés:</span>
            <span className="site-badge leboncoin">LeBonCoin</span>
            <span className="site-badge lacentrale">La Centrale</span>
            <span className="site-badge autoscout">AutoScout24</span>
          </div>
        </form>

        {/* Message d'erreur */}
        {error && (
          <div className="alert alert-error">
            ❌ {error}
          </div>
        )}

        {/* Message de succès */}
        {success && importedVehicle && (
          <div className="alert alert-success">
            <div className="success-header">
              ✅ Véhicule importé avec succès !
            </div>
            <div className="imported-vehicle-preview">
              {importedVehicle.images && importedVehicle.images[0] && (
                <img src={importedVehicle.images[0]} alt={importedVehicle.title} />
              )}
              <div className="vehicle-info">
                <h4>{importedVehicle.title}</h4>
                <p className="vehicle-price">
                  {importedVehicle.price.toLocaleString('fr-FR')} €
                </p>
                <p className="vehicle-details">
                  {importedVehicle.make} {importedVehicle.model}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Exemples d'URLs */}
        <details className="url-examples">
          <summary>💡 Exemples d'URLs valides</summary>
          <ul>
            <li>
              <strong>LeBonCoin:</strong><br/>
              <code>https://www.leboncoin.fr/voitures/123456.htm</code>
            </li>
            <li>
              <strong>La Centrale:</strong><br/>
              <code>https://www.lacentrale.fr/auto-occasion-annonce-123456.html</code>
            </li>
            <li>
              <strong>AutoScout24:</strong><br/>
              <code>https://www.autoscout24.fr/offres/123456</code>
            </li>
          </ul>
        </details>
      </div>
    </div>
  );
}
