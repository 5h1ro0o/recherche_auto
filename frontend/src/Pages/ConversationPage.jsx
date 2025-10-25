// frontend/src/Pages/ConversationPage.jsx - VERSION COMPLÈTE
import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import useSWR from 'swr'
import { 
  getConversationMessages, 
  sendMessage, 
  connectWebSocket,
  getMessageTemplates,
  uploadAttachment,
  sendTypingStatus
} from '../services/messages'

export default function ConversationPage() {
  const { conversationId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [otherUser, setOtherUser] = useState(null)
  const [otherUserTyping, setOtherUserTyping] = useState(false)
  
  // Templates & Attachments
  const [showTemplates, setShowTemplates] = useState(false)
  const [templates, setTemplates] = useState({})
  const [selectedFiles, setSelectedFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  
  const messagesEndRef = useRef(null)
  const typingTimeoutRef = useRef(null)
  const fileInputRef = useRef(null)

  // Charger messages
  const { data: initialMessages, error } = useSWR(
    conversationId ? `/messages/${conversationId}` : null,
    () => getConversationMessages(conversationId)
  )

  // Charger templates
  useEffect(() => {
    async function loadTemplates() {
      try {
        const data = await getMessageTemplates()
        setTemplates(data.templates)
      } catch (error) {
        console.error('Erreur chargement templates:', error)
      }
    }
    loadTemplates()
  }, [])

  useEffect(() => {
    if (initialMessages && initialMessages.length > 0) {
      setMessages(initialMessages)
      
      const firstMessage = initialMessages[0]
      const otherId = firstMessage.sender_id === user.id 
        ? firstMessage.recipient_id 
        : firstMessage.sender_id
      
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
        
        if (newMsg.conversation_id === conversationId) {
          setMessages(prev => [...prev, newMsg])
        }
      }
      
      else if (data.type === 'typing_status') {
        if (data.conversation_id === conversationId && data.user_id !== user.id) {
          setOtherUserTyping(data.is_typing)
          
          // Auto-clear après 3 secondes
          if (data.is_typing) {
            setTimeout(() => setOtherUserTyping(false), 3000)
          }
        }
      }
    }

    return () => {
      // WebSocket reste connecté pour d'autres pages
    }
  }, [user, conversationId])

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Gérer indicateur "en train d'écrire"
  function handleInputChange(e) {
    const value = e.target.value
    setInputValue(value)
    
    // Envoyer typing_start
    if (value && otherUser) {
      sendTypingStatus(conversationId, otherUser.id, true)
      
      // Auto-stop après 3 secondes
      clearTimeout(typingTimeoutRef.current)
      typingTimeoutRef.current = setTimeout(() => {
        sendTypingStatus(conversationId, otherUser.id, false)
      }, 3000)
    }
  }

  // Upload fichiers
  async function handleFileSelect(e) {
    const files = Array.from(e.target.files)
    setUploading(true)
    
    for (const file of files) {
      if (file.size > 5 * 1024 * 1024) {
        alert(`${file.name} est trop volumineux (max 5MB)`)
        continue
      }
      
      try {
        const response = await uploadAttachment(file)
        setSelectedFiles(prev => [...prev, response])
      } catch (error) {
        console.error('Erreur upload:', error)
        alert(`Erreur lors de l'upload de ${file.name}`)
      }
    }
    
    setUploading(false)
  }

  // Envoyer message
  async function handleSend(e) {
    e.preventDefault()
    
    if ((!inputValue.trim() && selectedFiles.length === 0) || sending) return

    const content = inputValue.trim() || '[Image]'
    const attachments = selectedFiles.map(f => f.url)
    
    setInputValue('')
    setSelectedFiles([])
    setSending(true)
    
    // Arrêter typing indicator
    if (otherUser) {
      sendTypingStatus(conversationId, otherUser.id, false)
    }

    try {
      const [id1, id2] = conversationId.split('_')
      const recipientId = id1 === user.id ? id2 : id1

      await sendMessage({
        recipient_id: recipientId,
        content,
        attachments
      })
      
      // Message sera ajouté via WebSocket
    } catch (error) {
      console.error('Erreur envoi message:', error)
      alert('Erreur lors de l\'envoi du message')
      setInputValue(content)
      setSelectedFiles(attachments.map(url => ({ url })))
    } finally {
      setSending(false)
    }
  }

  // Utiliser un template
  function useTemplate(templateKey) {
    const template = templates[templateKey]
    if (template) {
      setInputValue(template.text)
      setShowTemplates(false)
    }
  }

  if (error) {
    return (
      <div className="conversation-page">
        <div className="error-message">Erreur lors du chargement</div>
      </div>
    )
  }

  if (!initialMessages) {
    return (
      <div className="conversation-page">
        <div className="loading">Chargement...</div>
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
              {otherUserTyping && (
                <span className="typing-indicator-text">En train d'écrire...</span>
              )}
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
        
        {otherUserTyping && (
          <div className="typing-indicator-bubble">
            <div className="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="message-input-form">
        {/* Templates dropdown */}
        {showTemplates && (
          <div className="templates-dropdown">
            <div className="templates-header">
              <h4>💬 Messages rapides</h4>
              <button 
                type="button" 
                onClick={() => setShowTemplates(false)}
                className="close-templates"
              >
                ✕
              </button>
            </div>
            <div className="templates-list">
              {Object.entries(templates).map(([key, template]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => useTemplate(key)}
                  className="template-item"
                >
                  <strong>{template.label}</strong>
                  <p>{template.text.slice(0, 60)}...</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Fichiers sélectionnés */}
        {selectedFiles.length > 0 && (
          <div className="selected-files">
            {selectedFiles.map((file, idx) => (
              <div key={idx} className="file-preview">
                <img src={file.url} alt={file.filename} />
                <button 
                  type="button"
                  onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== idx))}
                  className="remove-file"
                >
                  ✕
                </button>
                <span className="file-size">{formatFileSize(file.size)}</span>
              </div>
            ))}
          </div>
        )}

        {/* Input principal */}
        <div className="input-wrapper">
          <button
            type="button"
            onClick={() => setShowTemplates(!showTemplates)}
            className="template-btn"
            title="Messages rapides"
          >
            💬
          </button>

          <textarea
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Écrivez votre message..."
            rows={2}
            disabled={sending || uploading}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend(e)
              }
            }}
          />

          <div className="input-actions">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="attach-btn"
              disabled={uploading}
              title="Joindre une image"
            >
              {uploading ? '⏳' : '📎'}
            </button>

            <button 
              type="submit" 
              disabled={sending || uploading || (!inputValue.trim() && selectedFiles.length === 0)}
              className="send-btn"
            >
              {sending ? '⏳' : '📤'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

function MessageBubble({ message, isOwn, showTime }) {
  return (
    <div className={`message-bubble-wrapper ${isOwn ? 'own' : 'other'}`}>
      <div className={`message-bubble ${isOwn ? 'own' : 'other'}`}>
        <div className="message-content">{message.content}</div>
        
        {/* Afficher les images jointes */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="message-attachments">
            {message.attachments.map((url, idx) => (
              <img 
                key={idx} 
                src={url} 
                alt="Pièce jointe"
                className="attachment-image"
                onClick={() => window.open(url, '_blank')}
              />
            ))}
          </div>
        )}
        
        {showTime && (
          <div className="message-time">
            {new Date(message.created_at).toLocaleTimeString('fr-FR', {
              hour: '2-digit',
              minute: '2-digit'
            })}
            {isOwn && (
              <span className="message-status">
                {message.is_read ? ' ✓✓' : ' ✓'}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function shouldShowTime(messages, index) {
  if (index === messages.length - 1) return true
  
  const currentTime = new Date(messages[index].created_at)
  const nextTime = new Date(messages[index + 1].created_at)
  const diffMinutes = (nextTime - currentTime) / 1000 / 60
  
  return diffMinutes > 5
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}