// frontend/src/Pages/ConversationPage.jsx
import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import useSWR from 'swr'
import { 
  getConversationMessages, 
  sendMessage, 
  connectWebSocket,
  disconnectWebSocket 
} from '../services/messages'

export default function ConversationPage() {
  const { conversationId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [otherUser, setOtherUser] = useState(null)
  const messagesEndRef = useRef(null)

  // Charger les messages
  const { data: initialMessages, error } = useSWR(
    conversationId ? `/messages/${conversationId}` : null,
    () => getConversationMessages(conversationId)
  )

  useEffect(() => {
    if (initialMessages && initialMessages.length > 0) {
      setMessages(initialMessages)
      
      // Déterminer l'autre utilisateur
      const firstMessage = initialMessages[0]
      const otherId = firstMessage.sender_id === user.id 
        ? firstMessage.recipient_id 
        : firstMessage.sender_id
      
      // On pourrait charger les infos de l'autre user ici si nécessaire
      setOtherUser({ id: otherId })
    }
  }, [initialMessages, user.id])

  // WebSocket pour temps réel
  useEffect(() => {
    if (!user) return

    const ws = connectWebSocket(user.id)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'new_message') {
        const newMsg = data.message
        
        // Ajouter le message seulement s'il appartient à cette conversation
        if (newMsg.conversation_id === conversationId) {
          setMessages(prev => [...prev, newMsg])
        }
      }
    }

    // Ping pour garder la connexion active
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)

    return () => {
      clearInterval(pingInterval)
      disconnectWebSocket()
    }
  }, [user, conversationId])

  // Auto-scroll vers le bas
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    
    if (!inputValue.trim() || sending) return

    const content = inputValue.trim()
    setInputValue('')
    setSending(true)

    try {
      // Extraire l'ID du destinataire depuis conversationId
      const [id1, id2] = conversationId.split('_')
      const recipientId = id1 === user.id ? id2 : id1

      await sendMessage({
        recipient_id: recipientId,
        content,
        attachments: []
      })
      
      // Le message sera ajouté via WebSocket
    } catch (error) {
      console.error('Erreur envoi message:', error)
      alert('Erreur lors de l\'envoi du message')
      setInputValue(content) // Restaurer le texte
    } finally {
      setSending(false)
    }
  }

  if (error) {
    return (
      <div className="conversation-page">
        <div className="error-message">Erreur lors du chargement de la conversation</div>
      </div>
    )
  }

  if (!initialMessages) {
    return (
      <div className="conversation-page">
        <div className="loading">Chargement de la conversation...</div>
      </div>
    )
  }

  return (
    <div className="conversation-page">
      <div className="conversation-header">
        <button onClick={() => navigate('/messages')} className="back-btn">
          ← Retour
        </button>
        {otherUser && (
          <div className="conversation-title">
            <div className="other-user-avatar">
              {otherUser.full_name?.[0] || '?'}
            </div>
            <div>
              <h2>{otherUser.full_name || otherUser.email || 'Utilisateur'}</h2>
            </div>
          </div>
        )}
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-conversation">
            <p>Aucun message dans cette conversation</p>
            <p>Envoyez le premier message !</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <MessageBubble
              key={msg.id || idx}
              message={msg}
              isOwn={msg.sender_id === user.id}
              showTime={shouldShowTime(messages, idx)}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="message-input-form">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Écrivez votre message..."
          rows={2}
          disabled={sending}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend(e)
            }
          }}
        />
        <button type="submit" disabled={sending || !inputValue.trim()}>
          {sending ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  )
}

function MessageBubble({ message, isOwn, showTime }) {
  return (
    <div className={`message-bubble-wrapper ${isOwn ? 'own' : 'other'}`}>
      <div className={`message-bubble ${isOwn ? 'own' : 'other'}`}>
        <div className="message-content">{message.content}</div>
        {showTime && (
          <div className="message-time">
            {new Date(message.created_at).toLocaleTimeString('fr-FR', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function shouldShowTime(messages, index) {
  // Afficher l'heure sur le dernier message ou si 5+ minutes depuis le précédent
  if (index === messages.length - 1) return true
  
  const currentTime = new Date(messages[index].created_at)
  const nextTime = new Date(messages[index + 1].created_at)
  const diffMinutes = (nextTime - currentTime) / 1000 / 60
  
  return diffMinutes > 5
}