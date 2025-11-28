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
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#F9FAFB',
      }}>
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>⚠️</div>
          <div style={{ fontSize: '18px', color: '#222222' }}>Erreur lors du chargement</div>
        </div>
      </div>
    )
  }

  if (!initialMessages) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#F9FAFB',
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
        <div style={{ fontSize: '18px', color: '#6B7280' }}>Chargement...</div>
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: '#F9FAFB',
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #E5E7EB',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
      }}>
        <button
          onClick={() => navigate('/messages')}
          style={{
            padding: '8px 16px',
            background: 'white',
            border: '2px solid #E5E7EB',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            color: '#222222',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = '#DC2626'
            e.target.style.color = '#DC2626'
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = '#E5E7EB'
            e.target.style.color = '#222222'
          }}
        >
          ← Retour
        </button>

        {otherUser && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: '#DC2626',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '18px',
              fontWeight: 700,
              color: 'white',
            }}>
              {otherUser.full_name?.[0] || '?'}
            </div>
            <div>
              <h2 style={{
                margin: 0,
                fontSize: '18px',
                fontWeight: 600,
                color: '#222222',
              }}>
                {otherUser.full_name || otherUser.email || 'Utilisateur'}
              </h2>
              {otherUserTyping && (
                <span style={{
                  fontSize: '13px',
                  color: '#DC2626',
                  fontStyle: 'italic',
                }}>
                  En train d'écrire...
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Messages Container */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}>
        {messages.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>💬</div>
            <p style={{ fontSize: '18px', color: '#222222', marginBottom: '8px' }}>
              Aucun message dans cette conversation
            </p>
            <p style={{ fontSize: '14px', color: '#6B7280', margin: 0 }}>
              Envoyez le premier message !
            </p>
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
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
          }}>
            <div style={{
              background: '#E5E7EB',
              borderRadius: '18px',
              padding: '12px 16px',
              display: 'inline-flex',
              gap: '4px',
            }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#6B7280',
                animation: 'bounce 1.4s infinite ease-in-out',
              }} />
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#6B7280',
                animation: 'bounce 1.4s infinite ease-in-out 0.2s',
              }} />
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#6B7280',
                animation: 'bounce 1.4s infinite ease-in-out 0.4s',
              }} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} style={{
        background: 'white',
        borderTop: '1px solid #E5E7EB',
        padding: '16px 20px',
      }}>
        {/* Templates dropdown */}
        {showTemplates && (
          <div style={{
            position: 'absolute',
            bottom: '100%',
            left: '20px',
            right: '20px',
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 -4px 24px rgba(0, 0, 0, 0.15)',
            marginBottom: '8px',
            maxHeight: '300px',
            overflowY: 'auto',
          }}>
            <div style={{
              padding: '16px',
              borderBottom: '1px solid #E5E7EB',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <h4 style={{
                margin: 0,
                fontSize: '16px',
                fontWeight: 600,
                color: '#222222',
              }}>
                💬 Messages rapides
              </h4>
              <button
                type="button"
                onClick={() => setShowTemplates(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '20px',
                  cursor: 'pointer',
                  color: '#6B7280',
                }}
              >
                ✕
              </button>
            </div>
            <div style={{ padding: '8px' }}>
              {Object.entries(templates).map(([key, template]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => useTemplate(key)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    marginBottom: '8px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.borderColor = '#DC2626'
                    e.target.style.background = '#FEE2E2'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.borderColor = '#E5E7EB'
                    e.target.style.background = 'white'
                  }}
                >
                  <strong style={{ display: 'block', marginBottom: '4px', color: '#222222' }}>
                    {template.label}
                  </strong>
                  <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>
                    {template.text.slice(0, 60)}...
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Fichiers sélectionnés */}
        {selectedFiles.length > 0 && (
          <div style={{
            display: 'flex',
            gap: '8px',
            marginBottom: '12px',
            flexWrap: 'wrap',
          }}>
            {selectedFiles.map((file, idx) => (
              <div
                key={idx}
                style={{
                  position: 'relative',
                  width: '80px',
                  height: '80px',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  border: '2px solid #E5E7EB',
                }}
              >
                <img
                  src={file.url}
                  alt={file.filename}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />
                <button
                  type="button"
                  onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== idx))}
                  style={{
                    position: 'absolute',
                    top: '4px',
                    right: '4px',
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: '#DC2626',
                    color: 'white',
                    border: 'none',
                    fontSize: '12px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input principal */}
        <div style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-end',
        }}>
          <button
            type="button"
            onClick={() => setShowTemplates(!showTemplates)}
            title="Messages rapides"
            style={{
              padding: '10px',
              background: 'white',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '20px',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = '#DC2626'
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = '#E5E7EB'
            }}
          >
            💬
          </button>

          <textarea
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Écrivez votre message..."
            rows={2}
            disabled={sending || uploading}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '2px solid #E5E7EB',
              borderRadius: '12px',
              fontSize: '15px',
              fontFamily: 'inherit',
              resize: 'none',
              outline: 'none',
              transition: 'all 0.2s',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#DC2626'
              e.target.style.boxShadow = '0 0 0 3px rgba(220, 38, 38, 0.1)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#E5E7EB'
              e.target.style.boxShadow = 'none'
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend(e)
              }
            }}
          />

          <div style={{ display: 'flex', gap: '8px' }}>
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
              disabled={uploading}
              title="Joindre une image"
              style={{
                padding: '10px',
                background: 'white',
                border: '2px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '20px',
                cursor: uploading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: uploading ? 0.5 : 1,
              }}
              onMouseEnter={(e) => {
                if (!uploading) e.target.style.borderColor = '#DC2626'
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = '#E5E7EB'
              }}
            >
              {uploading ? '⏳' : '📎'}
            </button>

            <button
              type="submit"
              disabled={sending || uploading || (!inputValue.trim() && selectedFiles.length === 0)}
              style={{
                padding: '10px 20px',
                background: '#DC2626',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: (sending || uploading || (!inputValue.trim() && selectedFiles.length === 0)) ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: (sending || uploading || (!inputValue.trim() && selectedFiles.length === 0)) ? 0.5 : 1,
              }}
              onMouseEnter={(e) => {
                if (!sending && !uploading && (inputValue.trim() || selectedFiles.length > 0)) {
                  e.target.style.background = '#B91C1C'
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.background = '#DC2626'
              }}
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
    <div style={{
      display: 'flex',
      justifyContent: isOwn ? 'flex-end' : 'flex-start',
    }}>
      <div style={{
        maxWidth: '70%',
        background: isOwn ? '#DC2626' : 'white',
        color: isOwn ? 'white' : '#222222',
        borderRadius: '18px',
        padding: '12px 16px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      }}>
        <div style={{
          fontSize: '15px',
          lineHeight: 1.5,
          wordWrap: 'break-word',
        }}>
          {message.content}
        </div>

        {/* Afficher les images jointes */}
        {message.attachments && message.attachments.length > 0 && (
          <div style={{
            marginTop: '8px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
            gap: '8px',
          }}>
            {message.attachments.map((url, idx) => (
              <img
                key={idx}
                src={url}
                alt="Pièce jointe"
                style={{
                  width: '100%',
                  height: '150px',
                  objectFit: 'cover',
                  borderRadius: '8px',
                  cursor: 'pointer',
                }}
                onClick={() => window.open(url, '_blank')}
              />
            ))}
          </div>
        )}

        {showTime && (
          <div style={{
            fontSize: '11px',
            marginTop: '6px',
            opacity: 0.7,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            {new Date(message.created_at).toLocaleTimeString('fr-FR', {
              hour: '2-digit',
              minute: '2-digit'
            })}
            {isOwn && (
              <span>
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
