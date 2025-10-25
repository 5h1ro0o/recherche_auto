// frontend/src/components/ChatBot.jsx - Version améliorée
import React, { useState, useRef, useEffect } from 'react'
import { chatSearch } from '../services/chatbot'
import { getSearchHistory } from '../services/searchHistory'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ChatBot({ onFiltersDetected, onSearchResults }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { type: 'bot', text: "👋 Bonjour ! Décrivez-moi le véhicule que vous recherchez.", timestamp: new Date() }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [history, setHistory] = useState([])
  const messagesEndRef = useRef(null)
  const { isAuthenticated } = useAuth()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && isAuthenticated && showHistory) {
      loadHistory()
    }
  }, [isOpen, showHistory, isAuthenticated])

  async function loadHistory() {
    try {
      const data = await getSearchHistory(10)
      setHistory(data)
    } catch (error) {
      console.error('Error loading history:', error)
    }
  }

  async function handleSend() {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    const newMessages = [...messages, { type: 'user', text: userMessage, timestamp: new Date() }]
    setMessages(newMessages)
    setLoading(true)

    try {
      const response = await chatSearch(userMessage)
      
      const botMessages = [
        ...newMessages,
        { 
          type: 'bot', 
          text: response.interpretation || "Voici les résultats", 
          timestamp: new Date() 
        }
      ]

      if (response.total > 0) {
        botMessages.push({
          type: 'results',
          data: {
            total: response.total,
            hits: response.hits.slice(0, 5), // Limiter à 5 pour le chat
            filters: response.filters_used,
            showAll: response.total > 5
          },
          timestamp: new Date()
        })
      } else {
        botMessages.push({
          type: 'bot',
          text: "😕 Aucun véhicule ne correspond. Essayez d'élargir vos critères.",
          timestamp: new Date()
        })
        
        // Ajouter suggestions si disponibles
        if (response.suggestions && response.suggestions.length > 0) {
          botMessages.push({
            type: 'suggestions',
            suggestions: response.suggestions,
            timestamp: new Date()
          })
        }
      }

      setMessages(botMessages)

      if (onFiltersDetected && response.filters_used) {
        onFiltersDetected(response.filters_used)
      }
      if (onSearchResults && response.hits) {
        onSearchResults(response.hits, response.total)
      }

    } catch (error) {
      console.error('Erreur chatbot:', error)
      setMessages([
        ...newMessages,
        { type: 'bot', text: "❌ Désolé, une erreur s'est produite.", timestamp: new Date() }
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleHistoryClick(historyItem) {
    const queryText = historyItem.query || 'Recherche sauvegardée'
    setInput(queryText)
    setShowHistory(false)
  }

  function handleReset() {
    setMessages([
      { type: 'bot', text: "👋 Nouvelle conversation ! Comment puis-je vous aider ?", timestamp: new Date() }
    ])
  }

  return (
    <>
      {/* Bouton flottant */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="chatbot-toggle"
        title="Assistant de recherche"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Fenêtre chat */}
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h3>🤖 Assistant Recherche</h3>
            <div className="chatbot-actions">
              {isAuthenticated && (
                <button 
                  onClick={() => setShowHistory(!showHistory)}
                  title="Historique"
                  className="icon-btn"
                >
                  📋
                </button>
              )}
              <button 
                onClick={handleReset}
                title="Nouvelle conversation"
                className="icon-btn"
              >
                🔄
              </button>
              <button onClick={() => setIsOpen(false)} className="close-btn">✕</button>
            </div>
          </div>

          {/* Historique */}
          {showHistory && isAuthenticated && (
            <div className="chatbot-history">
              <h4>Recherches récentes</h4>
              {history.length === 0 ? (
                <p className="no-history">Aucun historique</p>
              ) : (
                <div className="history-list">
                  {history.map(item => (
                    <button
                      key={item.id}
                      onClick={() => handleHistoryClick(item)}
                      className="history-item"
                    >
                      <span className="history-query">{item.query || 'Recherche'}</span>
                      <span className="history-count">{item.results_count} résultats</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}
            {loading && (
              <div className="chat-message bot">
                <div className="chat-bubble">
                  <div className="typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chatbot-input">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ex: citadine essence moins de 10000 euros"
              rows={2}
              disabled={loading}
            />
            <button onClick={handleSend} disabled={loading || !input.trim()}>
              {loading ? '...' : '📤'}
            </button>
          </div>
        </div>
      )}
    </>
  )
}

function ChatMessage({ message }) {
  if (message.type === 'results') {
    return (
      <div className="chat-results">
        <div className="results-summary">
          ✅ <strong>{message.data.total}</strong> véhicules trouvés
        </div>
        
        {/* Mini-cartes véhicules */}
        <div className="chat-vehicles">
          {message.data.hits.map(hit => (
            <Link
              key={hit.id}
              to={`/vehicle/${hit.id}`}
              className="chat-vehicle-card"
            >
              <div className="vehicle-title">
                {hit.source?.title || `${hit.source?.make} ${hit.source?.model}`}
              </div>
              {hit.source?.price && (
                <div className="vehicle-price">{hit.source.price} €</div>
              )}
              <div className="vehicle-details">
                {hit.source?.year} • {hit.source?.mileage} km
              </div>
            </Link>
          ))}
          
          {message.data.showAll && (
            <div className="see-more">
              Voir tous les {message.data.total} résultats sur la page
            </div>
          )}
        </div>

        {/* Filtres utilisés */}
        {Object.keys(message.data.filters).length > 0 && (
          <div className="results-filters">
            {Object.entries(message.data.filters).map(([key, value]) => (
              <span key={key} className="filter-badge">
                {key}: {value}
              </span>
            ))}
          </div>
        )}
      </div>
    )
  }

  if (message.type === 'suggestions') {
    return (
      <div className="chat-suggestions">
        <div className="suggestions-title">💡 Suggestions :</div>
        {message.suggestions.map((suggestion, i) => (
          <div key={i} className="suggestion-item">• {suggestion}</div>
        ))}
      </div>
    )
  }

  return (
    <div className={`chat-message ${message.type}`}>
      <div className="chat-bubble">
        {message.text}
      </div>
      <div className="chat-time">
        {message.timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  )
}