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
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Inscription</h2>
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Nom complet</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Téléphone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Type de compte</label>
            <select name="role" value={formData.role} onChange={handleChange}>
              <option value="PARTICULAR">Particulier</option>
              <option value="PRO">Professionnel</option>
            </select>
          </div>

          <div className="form-group">
            <label>Mot de passe * (min. 8 caractères)</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
            />
          </div>

          <div className="form-group">
            <label>Confirmer le mot de passe *</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              minLength={8}
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Inscription...' : 'S\'inscrire'}
          </button>
        </form>

        <p className="auth-link">
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </p>
      </div>
    </div>
  )
}