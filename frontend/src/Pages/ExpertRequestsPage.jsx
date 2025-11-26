import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const ExpertRequestsPage = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('PENDING');
  const navigate = useNavigate();

  const token = localStorage.getItem('token');
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const url = `${API_URL}/api/assisted/requests${filter ? `?status_filter=${filter}` : ''}`;
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des demandes');
      }

      const data = await response.json();
      setRequests(data);
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors du chargement des demandes');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      PENDING: { label: 'En attente', color: 'bg-yellow-100 text-yellow-800' },
      IN_PROGRESS: { label: 'En cours', color: 'bg-blue-100 text-blue-800' },
      COMPLETED: { label: 'Terminée', color: 'bg-green-100 text-green-800' },
      CANCELLED: { label: 'Annulée', color: 'bg-red-100 text-red-800' },
    };
    const { label, color } = statusMap[status] || { label: status, color: 'bg-gray-100 text-gray-800' };
    return <span className={`px-3 py-1 rounded-full text-sm font-medium ${color}`}>{label}</span>;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Demandes de recherche personnalisée</h1>
        <p className="text-gray-600">Gérez les demandes des clients et proposez-leur des véhicules</p>
      </div>

      {/* Filtres */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setFilter('PENDING')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'PENDING'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          En attente
        </button>
        <button
          onClick={() => setFilter('IN_PROGRESS')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'IN_PROGRESS'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          En cours
        </button>
        <button
          onClick={() => setFilter('COMPLETED')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'COMPLETED'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Terminées
        </button>
        <button
          onClick={() => setFilter('')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === ''
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Toutes
        </button>
      </div>

      {/* Liste des demandes */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Chargement des demandes...</p>
        </div>
      ) : requests.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500 text-lg">Aucune demande trouvée</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {requests.map((request) => (
            <div
              key={request.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 cursor-pointer"
              onClick={() => navigate(`/expert/requests/${request.id}`)}
            >
              <div className="flex justify-between items-start mb-4">
                {getStatusBadge(request.status)}
                <span className="text-sm text-gray-500">
                  {formatDate(request.created_at)}
                </span>
              </div>

              <h3 className="font-semibold text-lg mb-2 text-gray-900">
                Demande de recherche
              </h3>

              <p className="text-gray-600 mb-4 line-clamp-3">
                {request.description}
              </p>

              <div className="space-y-2 text-sm">
                {request.budget_max && (
                  <div className="flex items-center text-gray-700">
                    <span className="font-medium mr-2">Budget max:</span>
                    <span>{request.budget_max.toLocaleString()} €</span>
                  </div>
                )}
                {request.preferred_fuel_type && (
                  <div className="flex items-center text-gray-700">
                    <span className="font-medium mr-2">Carburant:</span>
                    <span className="capitalize">{request.preferred_fuel_type}</span>
                  </div>
                )}
                {request.max_mileage && (
                  <div className="flex items-center text-gray-700">
                    <span className="font-medium mr-2">Kilométrage max:</span>
                    <span>{request.max_mileage.toLocaleString()} km</span>
                  </div>
                )}
                {request.min_year && (
                  <div className="flex items-center text-gray-700">
                    <span className="font-medium mr-2">Année min:</span>
                    <span>{request.min_year}</span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/expert/requests/${request.id}`);
                  }}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  {request.status === 'PENDING' ? 'Accepter la demande' : 'Voir les détails'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExpertRequestsPage;
