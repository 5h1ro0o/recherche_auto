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
        background: 'var(--gray-50)',
      }}>
        <div style={{
          background: 'var(--white)',
                    padding: 'var(--space-10)',
          textAlign: 'center',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
        }}>
          <div style={{ fontSize: 'var(--space-16)', marginBottom: 'var(--space-5)' }}></div>
          <div style={{ fontSize: '18px', color: 'var(--text-primary)' }}>Erreur lors du chargement</div>
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
        background: 'var(--gray-50)',
      }}>
        <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
        <div style={{ fontSize: '18px', color: '#6B7280' }}>Chargement...</div>
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: 'var(--gray-50)',
    }}>
      {/* Header */}
      <div style={{
        background: 'var(--white)',
        borderBottom: '1px solid #E5E7EB',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-4)',
      }}>
        <button
          onClick={() => navigate('/messages')}
          style={{
            padding: '8px 16px',
            background: 'var(--white)',
            border: '2px solid #E5E7EB',
                        fontSize: '14px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = 'var(--red-accent)'
            e.target.style.color = 'var(--red-accent)'
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = 'var(--border-light)'
            e.target.style.color = 'var(--text-primary)'
          }}
        >
          ← Retour
        </button>

        {otherUser && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-3)',
          }}>
            <div style={{
              width: 'var(--space-10)',
              height: 'var(--space-10)',
              borderRadius: '50%',
              background: 'var(--red-accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '18px',
              fontWeight: 700,
              color: 'var(--white)',
            }}>
              {otherUser.full_name?.[0] || '?'}
            </div>
            <div>
              <h2 style={{
                margin: 0,
                fontSize: '18px',
                fontWeight: 600,
                color: 'var(--text-primary)',
              }}>
                {otherUser.full_name || otherUser.email || 'Utilisateur'}
              </h2>
              {otherUserTyping && (
                <span style={{
                  fontSize: '13px',
                  color: 'var(--red-accent)',
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
        padding: 'var(--space-5)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}>
        {messages.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
          }}>
            <div style={{ fontSize: 'var(--space-16)', marginBottom: 'var(--space-4)' }}></div>
            <p style={{ fontSize: '18px', color: 'var(--text-primary)', marginBottom: 'var(--space-2)' }}>
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
              background: 'var(--border-light)',
                            padding: '12px 16px',
              display: 'inline-flex',
              gap: 'var(--space-1)',
            }}>
              <span style={{
                width: 'var(--space-2)',
                height: 'var(--space-2)',
                borderRadius: '50%',
                background: '#6B7280',
                animation: 'bounce 1.4s infinite ease-in-out',
              }} />
              <span style={{
                width: 'var(--space-2)',
                height: 'var(--space-2)',
                borderRadius: '50%',
                background: '#6B7280',
                animation: 'bounce 1.4s infinite ease-in-out 0.2s',
              }} />
              <span style={{
                width: 'var(--space-2)',
                height: 'var(--space-2)',
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
        background: 'var(--white)',
        borderTop: '1px solid #E5E7EB',
        padding: '16px 20px',
      }}>
        {/* Templates dropdown */}
        {showTemplates && (
          <div style={{
            position: 'absolute',
            bottom: '100%',
            left: 'var(--space-5)',
            right: 'var(--space-5)',
            background: 'var(--white)',
                        boxShadow: '0 -4px 24px rgba(0, 0, 0, 0.15)',
            marginBottom: 'var(--space-2)',
            maxHeight: '300px',
            overflowY: 'auto',
          }}>
            <div style={{
              padding: 'var(--space-4)',
              borderBottom: '1px solid #E5E7EB',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <h4 style={{
                margin: 0,
                fontSize: 'var(--space-4)',
                fontWeight: 600,
                color: 'var(--text-primary)',
              }}>
                 Messages rapides
              </h4>
              <button
                type="button"
                onClick={() => setShowTemplates(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: 'var(--space-5)',
                  cursor: 'pointer',
                  color: '#6B7280',
                }}
              >
                ✕
              </button>
            </div>
            <div style={{ padding: 'var(--space-2)' }}>
              {Object.entries(templates).map(([key, template]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => useTemplate(key)}
                  style={{
                    width: '100%',
                    padding: 'var(--space-3)',
                    background: 'var(--white)',
                    border: '1px solid #E5E7EB',
                                        marginBottom: 'var(--space-2)',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.borderColor = 'var(--red-accent)'
                    e.target.style.background = '#FEE2E2'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.borderColor = 'var(--border-light)'
                    e.target.style.background = 'var(--white)'
                  }}
                >
                  <strong style={{ display: 'block', marginBottom: 'var(--space-1)', color: 'var(--text-primary)' }}>
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
            gap: 'var(--space-2)',
            marginBottom: 'var(--space-3)',
            flexWrap: 'wrap',
          }}>
            {selectedFiles.map((file, idx) => (
              <div
                key={idx}
                style={{
                  position: 'relative',
                  width: 'var(--space-20)',
                  height: 'var(--space-20)',
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
                    top: 'var(--space-1)',
                    right: 'var(--space-1)',
                    width: 'var(--space-5)',
                    height: 'var(--space-5)',
                    borderRadius: '50%',
                    background: 'var(--red-accent)',
                    color: 'var(--white)',
                    border: 'none',
                    fontSize: 'var(--space-3)',
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
          gap: 'var(--space-3)',
          alignItems: 'flex-end',
        }}>
          <button
            type="button"
            onClick={() => setShowTemplates(!showTemplates)}
            title="Messages rapides"
            style={{
              padding: '10px',
              background: 'var(--white)',
              border: '2px solid #E5E7EB',
                            fontSize: 'var(--space-5)',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = 'var(--red-accent)'
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = 'var(--border-light)'
            }}
          >
            
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
                            fontSize: '15px',
              fontFamily: 'inherit',
              resize: 'none',
              outline: 'none',
              transition: 'all 0.2s',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--red-accent)'
              e.target.style.boxShadow = '0 0 0 3px rgba(220, 38, 38, 0.1)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--border-light)'
              e.target.style.boxShadow = 'none'
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend(e)
              }
            }}
          />

          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
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
                background: 'var(--white)',
                border: '2px solid #E5E7EB',
                                fontSize: 'var(--space-5)',
                cursor: uploading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: uploading ? 0.5 : 1,
              }}
              onMouseEnter={(e) => {
                if (!uploading) e.target.style.borderColor = 'var(--red-accent)'
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = 'var(--border-light)'
              }}
            >
              {uploading ? '' : ''}
            </button>

            <button
              type="submit"
              disabled={sending || uploading || (!inputValue.trim() && selectedFiles.length === 0)}
              style={{
                padding: '10px 20px',
                background: 'var(--red-accent)',
                color: 'var(--white)',
                border: 'none',
                                fontSize: 'var(--space-4)',
                fontWeight: 600,
                cursor: (sending || uploading || (!inputValue.trim() && selectedFiles.length === 0)) ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: (sending || uploading || (!inputValue.trim() && selectedFiles.length === 0)) ? 0.5 : 1,
              }}
              onMouseEnter={(e) => {
                if (!sending && !uploading && (inputValue.trim() || selectedFiles.length > 0)) {
                  e.target.style.background = 'var(--red-accent)'
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'var(--red-accent)'
              }}
            >
              {sending ? '' : ''}
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
        background: isOwn ? 'var(--red-accent)' : 'var(--white)',
        color: isOwn ? 'var(--white)' : 'var(--text-primary)',
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
            marginTop: 'var(--space-2)',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
            gap: 'var(--space-2)',
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
            gap: 'var(--space-1)',
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
