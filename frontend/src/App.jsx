// frontend/src/App.jsx
import React, { useState } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import MessageNotification from './components/MessageNotification'

export default function App() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)

  function handleLogout() {
    logout()
    navigate('/login')
    setShowMenu(false)
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="header-container">
          <Link to="/" className="logo">
            🚗 Voiture Search
          </Link>

          <nav className="header-nav">
            <Link to="/" className="nav-link">
              Accueil
            </Link>

            <Link to="/search" className="nav-link">
              🔍 Rechercher
            </Link>

            <Link to="/encyclopedia" className="nav-link">
              📚 Encyclopédie
            </Link>

            {isAuthenticated && (
              <>
                <Link to="/favorites" className="nav-link">
                  ❤️ Favoris
                </Link>

                <Link to="/assisted" className="nav-link">
                  🤝 Recherche Personnalisée
                </Link>

                {user?.role === 'EXPERT' && (
                  <Link to="/expert" className="nav-link expert-link">
                    ⭐ Dashboard Expert
                  </Link>
                )}

                <MessageNotification />

                <div className="user-menu">
                  <button
                    className="user-menu-btn"
                    onClick={() => setShowMenu(!showMenu)}
                  >
                    <div className="user-avatar">
                      {user?.full_name?.[0] || user?.email?.[0] || '?'}
                    </div>
                    <span className="user-name">
                      {user?.full_name || user?.email}
                    </span>
                    <span className="dropdown-arrow">▼</span>
                  </button>

                  {showMenu && (
                    <div className="user-dropdown">
                      <Link
                        to="/profile"
                        className="dropdown-item"
                        onClick={() => setShowMenu(false)}
                      >
                        👤 Mon Profil
                      </Link>
                      <Link
                        to="/messages"
                        className="dropdown-item"
                        onClick={() => setShowMenu(false)}
                      >
                        💬 Messages
                      </Link>
                      <Link
                        to="/favorites"
                        className="dropdown-item"
                        onClick={() => setShowMenu(false)}
                      >
                        ❤️ Favoris
                      </Link>
                      <div className="dropdown-divider" />
                      <button
                        className="dropdown-item logout"
                        onClick={handleLogout}
                      >
                        🚪 Déconnexion
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}

            {!isAuthenticated && (
              <>
                <Link to="/login" className="nav-link">
                  Connexion
                </Link>
                <Link to="/register" className="btn-register">
                  S'inscrire
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="app-main">
        <Outlet />
      </main>

      <footer className="app-footer">
        <div className="footer-container">
          <div className="footer-section">
            <h4>À propos</h4>
            <p>Plateforme de recherche de véhicules avec IA</p>
          </div>
          <div className="footer-section">
            <h4>Fonctionnalités</h4>
            <ul>
              <li>Recherche intelligente</li>
              <li>Mode assisté par expert</li>
              <li>Messagerie intégrée</li>
              <li>Alertes personnalisées</li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Contact</h4>
            <p>support@voituresearch.fr</p>
          </div>
        </div>
        <div className="footer-bottom">
          © 2025 Voiture Search - MVP en développement
        </div>
      </footer>
    </div>
  )
}