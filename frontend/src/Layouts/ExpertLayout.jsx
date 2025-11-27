import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ExpertLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showUserMenu, setShowUserMenu] = useState(false);

  function handleLogout() {
    logout();
    navigate('/login');
    setShowUserMenu(false);
  }

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div style={{
      display: 'flex',
      minHeight: '100vh',
      background: '#f5f7fa',
    }}>
      {/* Sidebar */}
      <aside style={{
        width: '280px',
        background: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
        padding: '24px 0',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '4px 0 12px rgba(0,0,0,0.1)',
        position: 'fixed',
        height: '100vh',
        zIndex: 100,
      }}>
        {/* Logo */}
        <div style={{
          padding: '0 24px',
          marginBottom: '32px',
        }}>
          <Link to="/expert" style={{
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}>
            <div style={{
              fontSize: '32px',
              lineHeight: 1,
            }}>⭐</div>
            <div>
              <div style={{
                color: 'white',
                fontSize: '20px',
                fontWeight: 700,
                lineHeight: 1.2,
              }}>Expert Panel</div>
              <div style={{
                color: 'rgba(255,255,255,0.8)',
                fontSize: '12px',
              }}>Recherche Personnalisée</div>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          padding: '0 12px',
        }}>
          <NavLink
            to="/expert"
            icon="📊"
            label="Dashboard"
            active={location.pathname === '/expert'}
          />
          <NavLink
            to="/expert/market"
            icon="🏪"
            label="Marché des demandes"
            active={isActive('/expert/market')}
          />
          <NavLink
            to="/expert/missions"
            icon="📋"
            label="Mes missions"
            active={isActive('/expert/missions')}
          />
          <NavLink
            to="/expert/search"
            icon="🔍"
            label="Rechercher véhicules"
            active={isActive('/expert/search')}
          />
          <NavLink
            to="/messages"
            icon="💬"
            label="Messagerie"
            active={isActive('/messages')}
          />
          <NavLink
            to="/profile"
            icon="👤"
            label="Mon profil"
            active={isActive('/profile')}
          />
        </nav>

        {/* User Menu */}
        <div style={{
          padding: '0 12px',
          marginTop: 'auto',
          borderTop: '1px solid rgba(255,255,255,0.2)',
          paddingTop: '16px',
        }}>
          <div style={{
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '12px',
            padding: '12px',
            position: 'relative',
          }}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              style={{
                width: '100%',
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: 0,
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #ffd89b 0%, #19547b 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px',
                fontWeight: 600,
              }}>
                {user?.full_name?.[0] || user?.email?.[0] || 'E'}
              </div>
              <div style={{ flex: 1, textAlign: 'left' }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {user?.full_name || user?.email}
                </div>
                <div style={{
                  fontSize: '12px',
                  opacity: 0.8,
                }}>Expert</div>
              </div>
              <div style={{ fontSize: '12px' }}>▼</div>
            </button>

            {showUserMenu && (
              <div style={{
                position: 'absolute',
                bottom: '100%',
                left: '12px',
                right: '12px',
                marginBottom: '8px',
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                overflow: 'hidden',
              }}>
                <button
                  onClick={handleLogout}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: 'none',
                    border: 'none',
                    color: '#dc3545',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '14px',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fa'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                  🚪 Déconnexion
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{
        flex: 1,
        marginLeft: '280px',
        minHeight: '100vh',
      }}>
        <Outlet />
      </main>
    </div>
  );
}

function NavLink({ to, icon, label, active }) {
  return (
    <Link
      to={to}
      style={{
        textDecoration: 'none',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 16px',
        borderRadius: '10px',
        background: active ? 'rgba(255,255,255,0.15)' : 'transparent',
        color: 'white',
        fontSize: '15px',
        fontWeight: active ? 600 : 500,
        transition: 'all 0.2s',
        border: active ? '1px solid rgba(255,255,255,0.2)' : '1px solid transparent',
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.background = 'rgba(255,255,255,0.08)';
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.background = 'transparent';
        }
      }}
    >
      <span style={{ fontSize: '20px', lineHeight: 1 }}>{icon}</span>
      <span>{label}</span>
    </Link>
  );
}
