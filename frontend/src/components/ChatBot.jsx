import React, { useState, useRef, useEffect } from 'react'
import { chatSearch } from '../services/chatbot'
import { Link } from 'react-router-dom'

export default function ChatBot({ onFiltersDetected, onSearchResults }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { type: 'bot', text: "👋 Bonjour ! Décrivez-moi le véhicule que vous recherchez.", timestamp: new Date() }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  async function handleSend() {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Ajouter message utilisateur
    const newMessages = [...messages, { type: 'user', text: userMessage, timestamp: new Date() }]
    setMessages(newMessages)
    setLoading(true)

    try {
      // Parser avec l'IA
      const response = await chatSearch(userMessage)
      
      // Message bot avec interprétation
      const botMessages = [
        ...newMessages,
        { 
          type: 'bot', 
          text: response.interpretation || "Voici les résultats", 
          timestamp: new Date() 
        }
      ]

      // Ajouter résultats si présents
      if (response.total > 0) {
        botMessages.push({
          type: 'results',
          data: {
            total: response.total,
            hits: response.hits,
            filters: response.filters_used
          },
          timestamp: new Date()
        })
      } else {
        botMessages.push({
          type: 'bot',
          text: "😕 Aucun véhicule ne correspond. Essayez d'élargir vos critères.",
          timestamp: new Date()
        })
      }

      setMessages(botMessages)

      // Notifier parent si besoin
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
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>

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
        <div className="results-filters">
          {Object.entries(message.data.filters).map(([key, value]) => (
            <span key={key} className="filter-badge">
              {key}: {value}
            </span>
          ))}
        </div>
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