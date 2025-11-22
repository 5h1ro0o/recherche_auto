// frontend/src/main.jsx - VERSION MISE À JOUR AVEC MESSAGERIE
import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

import App from './App'
import HomePage from './Pages/HomePage'
import SearchPage from './Pages/SearchPage'
import AdvancedSearchPage from './Pages/AdvancedSearchPage'
import EncyclopediaPage from './Pages/EncyclopediaPage'
import VehiclePage from './Pages/VehiclePage'
import LoginPage from './Pages/LoginPage'
import RegisterPage from './Pages/RegisterPage'
import ProfilePage from './Pages/ProfilePage'
import FavoritesPage from './Pages/FavoritesPage'
import AssistedRequestPage from './Pages/AssistedRequestPage'
import ExpertDashboard from './Pages/ExpertDashboard'
import ExpertRequestDetailPage from './Pages/ExpertRequestDetailPage'
import AdminDashboard from './Pages/AdminDashboard'
import MessagesPage from './Pages/MessagesPage'
import ConversationPage from './Pages/ConversationPage'
import './styles.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<App />}>
              {/* Routes publiques */}
              <Route index element={<HomePage />} />
              <Route path="/search" element={<AdvancedSearchPage />} />
              <Route path="/encyclopedia" element={<EncyclopediaPage />} />
              <Route path="/vehicle/:id" element={<VehiclePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/admin" element={<AdminDashboard />} />

              
              {/* Routes protégées - Utilisateur connecté */}
              <Route 
                path="/expert/request/:requestId" 
                element={
                  <ProtectedRoute requiredRole="EXPERT">
                    <ExpertRequestDetailPage />
                  </ProtectedRoute>
                } 
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/favorites"
                element={
                  <ProtectedRoute>
                    <FavoritesPage />
                  </ProtectedRoute>
                }
              />
              
              {/* Routes protégées - Messagerie */}
              <Route
                path="/messages"
                element={
                  <ProtectedRoute>
                    <MessagesPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/messages/:conversationId"
                element={
                  <ProtectedRoute>
                    <ConversationPage />
                  </ProtectedRoute>
                }
              />
              
              {/* Routes protégées - Mode Assisté Client */}
              <Route
                path="/assisted"
                element={
                  <ProtectedRoute>
                    <AssistedRequestPage />
                  </ProtectedRoute>
                }
              />
              
              {/* Routes protégées - Expert uniquement */}
              <Route
                path="/expert"
                element={
                  <ProtectedRoute requiredRole="EXPERT">
                    <ExpertDashboard />
                  </ProtectedRoute>
                }
              />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)