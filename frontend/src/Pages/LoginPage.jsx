import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const loginData = await login(email, password)
      // Rediriger vers le dashboard expert si c'est un expert
      if (loginData?.user?.role === 'EXPERT') {
        navigate('/expert')
      } else {
        navigate('/')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur de connexion')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--gray-50)',
      padding: 'var(--space-6)'
    }}>
      <div style={{
        background: 'var(--white)',
        border: '1px solid var(--border-light)',
        boxShadow: 'var(--shadow-gloss-lg)',
        padding: 'var(--space-10)',
        maxWidth: '420px',
        width: '100%',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Top gloss overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '120px',
          background: 'var(--gloss-overlay)',
          pointerEvents: 'none'
        }} />

        {/* Header */}
        <div style={{
          textAlign: 'center',
          marginBottom: 'var(--space-8)',
          position: 'relative',
          zIndex: 1
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: 'var(--font-weight-bold)',
            color: 'var(--text-primary)',
            margin: '0 0 var(--space-2) 0',
            letterSpacing: '-0.02em'
          }}>
            Bon retour
          </h2>
          <p style={{
            fontSize: '15px',
            color: 'var(--text-secondary)',
            margin: 0,
            fontWeight: 'var(--font-weight-medium)'
          }}>
            Connectez-vous à votre compte
          </p>
        </div>

        {error && (
          <div style={{
            background: 'var(--red-accent-light)',
            border: '1px solid var(--red-accent)',
            padding: 'var(--space-3) var(--space-4)',
            marginBottom: 'var(--space-6)',
            color: 'var(--red-accent)',
            fontSize: '14px',
            fontWeight: 'var(--font-weight-medium)'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ marginBottom: 'var(--space-5)' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="votre@email.com"
              className="form-input"
              style={{
                width: '100%',
                padding: 'var(--space-3) var(--space-4)',
                fontSize: '15px'
              }}
            />
          </div>

          <div style={{ marginBottom: 'var(--space-6)' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              placeholder="••••••••"
              className="form-input"
              style={{
                width: '100%',
                padding: 'var(--space-3) var(--space-4)',
                fontSize: '15px'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              width: '100%',
              padding: 'var(--space-4) var(--space-6)',
              fontSize: '15px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontWeight: 'var(--font-weight-semibold)'
            }}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <div style={{
          textAlign: 'center',
          marginTop: 'var(--space-6)',
          fontSize: '14px',
          color: 'var(--text-secondary)',
          fontWeight: 'var(--font-weight-medium)',
          position: 'relative',
          zIndex: 1
        }}>
          Pas encore de compte ?{' '}
          <Link
            to="/register"
            style={{
              color: 'var(--red-accent)',
              textDecoration: 'none',
              fontWeight: 'var(--font-weight-semibold)',
              transition: 'opacity var(--transition-fast)'
            }}
            onMouseEnter={(e) => e.target.style.opacity = '0.8'}
            onMouseLeave={(e) => e.target.style.opacity = '1'}
          >
            S'inscrire
          </Link>
        </div>
      </div>
    </div>
  )
}
