import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    phone: '',
    role: 'PARTICULAR'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    setLoading(true)

    try {
      const { confirmPassword, ...registerData } = formData
      await register(registerData)

      // Rediriger selon le rôle
      if (formData.role === 'EXPERT') {
        navigate('/expert')
      } else {
        navigate('/')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription')
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
        maxWidth: '500px',
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
            Créer un compte
          </h2>
          <p style={{
            fontSize: '15px',
            color: 'var(--text-secondary)',
            margin: 0,
            fontWeight: 'var(--font-weight-medium)'
          }}>
            Rejoignez la plateforme dès aujourd'hui
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
              fontSize: '13px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="form-input"
              style={{
                width: '100%',
                padding: 'var(--space-3) var(--space-4)',
                fontSize: '15px'
              }}
            />
          </div>

          <div style={{ marginBottom: 'var(--space-5)' }}>
            <label style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Nom complet
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="form-input"
              style={{
                width: '100%',
                padding: 'var(--space-3) var(--space-4)',
                fontSize: '15px'
              }}
            />
          </div>

          <div style={{ marginBottom: 'var(--space-5)' }}>
            <label style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Téléphone
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="06 12 34 56 78"
              className="form-input"
              style={{
                width: '100%',
                padding: 'var(--space-3) var(--space-4)',
                fontSize: '15px'
              }}
            />
          </div>

          <div style={{ marginBottom: 'var(--space-5)' }}>
            <label style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Type de compte
            </label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="form-select"
              style={{
                width: '100%',
                padding: 'var(--space-3) var(--space-4)',
                fontSize: '15px'
              }}
            >
              <option value="PARTICULAR">Particulier - Recherche de véhicule</option>
              <option value="PRO">Professionnel - Vente de véhicules</option>
            </select>
            <div style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              marginTop: 'var(--space-2)',
              fontWeight: 'var(--font-weight-regular)'
            }}>
              {formData.role === 'PARTICULAR' ?
                'Trouvez votre véhicule idéal avec l\'aide d\'experts' :
                'Gérez et vendez vos véhicules sur la plateforme'}
            </div>
          </div>

          <div style={{ marginBottom: 'var(--space-5)' }}>
            <label style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Mot de passe * (min. 8 caractères)
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
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
              fontSize: '13px',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Confirmer le mot de passe *
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              minLength={8}
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
            {loading ? 'Inscription en cours...' : 'Créer mon compte'}
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
          Vous avez déjà un compte ?{' '}
          <Link
            to="/login"
            style={{
              color: 'var(--red-accent)',
              textDecoration: 'none',
              fontWeight: 'var(--font-weight-semibold)',
              transition: 'opacity var(--transition-fast)'
            }}
            onMouseEnter={(e) => e.target.style.opacity = '0.8'}
            onMouseLeave={(e) => e.target.style.opacity = '1'}
          >
            Se connecter
          </Link>
        </div>
      </div>
    </div>
  )
}
