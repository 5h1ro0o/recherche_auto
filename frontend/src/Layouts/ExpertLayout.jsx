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
      background: '#FAFAFA',
    }}>
      {/* Sidebar */}
      <aside style={{
        width: '260px',
        background: '#222222',
        padding: '24px 0',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid #EEEEEE',
        position: 'fixed',
        height: '100vh',
        zIndex: 100,
      }}>
        {/* Logo */}
        <div style={{
          padding: '0 20px',
          marginBottom: '40px',
        }}>
          <Link to="/expert" style={{
            textDecoration: 'none',
          }}>
            <div style={{
              color: 'white',
              fontSize: '18px',
              fontWeight: 600,
              letterSpacing: '-0.5px',
            }}>Expert Panel</div>
            <div style={{
              color: 'rgba(255,255,255,0.5)',
              fontSize: '12px',
              marginTop: '4px',
            }}>Recherche Personnalisée</div>
          </Link>
        </div>

        {/* Navigation */}
        <nav style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '2px',
          padding: '0 16px',
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
            to="/expert/messages"
            icon="💬"
            label="Messagerie"
            active={isActive('/expert/messages')}
          />
          <NavLink
            to="/expert/profile"
            icon="👤"
            label="Mon profil"
            active={isActive('/expert/profile')}
          />
        </nav>

        {/* User Menu */}
        <div style={{
          padding: '0 16px',
          marginTop: 'auto',
          borderTop: '1px solid rgba(255,255,255,0.1)',
          paddingTop: '16px',
        }}>
          <div style={{
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '8px',
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
                gap: '10px',
                padding: 0,
              }}
            >
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: '#DC2626',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 600,
              }}>
                {user?.full_name?.[0] || user?.email?.[0] || 'E'}
              </div>
              <div style={{ flex: 1, textAlign: 'left' }}>
                <div style={{
                  fontSize: '13px',
                  fontWeight: 500,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {user?.full_name || user?.email}
                </div>
                <div style={{
                  fontSize: '11px',
                  opacity: 0.5,
                }}>Expert</div>
              </div>
              <div style={{ fontSize: '10px', opacity: 0.5 }}>▼</div>
            </button>

            {showUserMenu && (
              <div style={{
                position: 'absolute',
                bottom: '100%',
                left: '16px',
                right: '16px',
                marginBottom: '8px',
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                overflow: 'hidden',
                border: '1px solid #EEEEEE',
              }}>
                <button
                  onClick={handleLogout}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: 'none',
                    border: 'none',
                    color: '#DC2626',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '13px',
                    fontWeight: 500,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#FAFAFA'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                  Déconnexion
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{
        flex: 1,
        marginLeft: '260px',
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
