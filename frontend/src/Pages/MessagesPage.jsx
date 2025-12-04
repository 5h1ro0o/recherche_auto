// frontend/src/Pages/MessagesPage.jsx
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import useSWR from 'swr'
import { getConversations } from '../services/messages'

export default function MessagesPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { data: conversations, error, mutate } = useSWR('/messages/conversations', getConversations)
  const [selectedFilter, setSelectedFilter] = useState('all')

  const isExpert = user && user.role === 'EXPERT'

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'var(--gray-50)',
        padding: '80px 20px',
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          textAlign: 'center',
          background: 'var(--white)',
                    padding: 'var(--space-10)',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
        }}>
          <div style={{ fontSize: 'var(--space-16)', marginBottom: 'var(--space-5)' }}></div>
          <h3 style={{ fontSize: 'var(--space-6)', color: 'var(--text-primary)', marginBottom: 'var(--space-3)' }}>
            Erreur de chargement
          </h3>
          <p style={{ color: '#6B7280' }}>
            Impossible de charger vos conversations
          </p>
        </div>
      </div>
    )
  }

  if (!conversations) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'var(--gray-50)',
        padding: '80px 20px',
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
          <p style={{ color: '#6B7280', fontSize: '18px' }}>Chargement de vos conversations...</p>
        </div>
      </div>
    )
  }

  const filteredConversations = conversations.filter(conv => {
    if (selectedFilter === 'unread') {
      return conv.unread_count > 0
    }
    return true
  })

  const totalUnread = conversations.reduce((sum, conv) => sum + conv.unread_count, 0)

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--gray-50)',
      padding: isExpert ? 'var(--space-5)' : '0',
      paddingBottom: isExpert ? 'var(--space-5)' : 'var(--space-16)',
    }}>
      {/* Header Section - Only for non-experts */}
      {!isExpert && (
        <div style={{
          background: 'var(--red-accent)',
          color: 'var(--white)',
          padding: '60px 20px',
          marginBottom: 'var(--space-10)',
        }}>
          <div style={{
            maxWidth: '900px',
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 'var(--space-4)',
          }}>
            <h1 style={{
              fontSize: '42px',
              fontWeight: 700,
              margin: 0,
              lineHeight: 1.2,
            }}>
               Mes Conversations
            </h1>
            {totalUnread > 0 && (
              <div style={{
                background: 'var(--white)',
                color: 'var(--red-accent)',
                padding: '8px 20px',
                                fontSize: 'var(--space-4)',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
              }}>
                {totalUnread} non lu{totalUnread > 1 ? 's' : ''}
              </div>
            )}
          </div>
        </div>
      )}

      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: isExpert ? '0' : '0 20px',
      }}>
        {/* Filters */}
        <div style={{
          display: 'flex',
          gap: 'var(--space-3)',
          marginBottom: 'var(--space-6)',
        }}>
          <button
            onClick={() => setSelectedFilter('all')}
            style={{
              padding: '12px 24px',
              background: selectedFilter === 'all' ? 'var(--red-accent)' : 'var(--white)',
              color: selectedFilter === 'all' ? 'var(--white)' : 'var(--text-primary)',
              border: selectedFilter === 'all' ? 'none' : '2px solid #E5E7EB',
                            fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (selectedFilter !== 'all') {
                e.target.style.borderColor = 'var(--red-accent)'
              }
            }}
            onMouseLeave={(e) => {
              if (selectedFilter !== 'all') {
                e.target.style.borderColor = 'var(--border-light)'
              }
            }}
          >
            Toutes ({conversations.length})
          </button>
          <button
            onClick={() => setSelectedFilter('unread')}
            style={{
              padding: '12px 24px',
              background: selectedFilter === 'unread' ? 'var(--red-accent)' : 'var(--white)',
              color: selectedFilter === 'unread' ? 'var(--white)' : 'var(--text-primary)',
              border: selectedFilter === 'unread' ? 'none' : '2px solid #E5E7EB',
                            fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (selectedFilter !== 'unread') {
                e.target.style.borderColor = 'var(--red-accent)'
              }
            }}
            onMouseLeave={(e) => {
              if (selectedFilter !== 'unread') {
                e.target.style.borderColor = 'var(--border-light)'
              }
            }}
          >
            Non lues ({totalUnread})
          </button>
        </div>

        {filteredConversations.length === 0 ? (
          <div style={{
            background: 'var(--white)',
                        padding: '60px 40px',
            textAlign: 'center',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
          }}>
            <div style={{ fontSize: 'var(--space-20)', marginBottom: 'var(--space-6)' }}></div>
            <h3 style={{
              fontSize: 'var(--space-7)',
              fontWeight: 700,
              color: 'var(--text-primary)',
              margin: '0 0 12px 0',
            }}>
              Aucune conversation
            </h3>
            <p style={{
              fontSize: 'var(--space-4)',
              color: '#6B7280',
              margin: 0,
            }}>
              {selectedFilter === 'unread'
                ? 'Vous n\'avez pas de messages non lus'
                : 'Vous n\'avez pas encore de conversations'
              }
            </p>
          </div>
        ) : (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-3)',
          }}>
            {filteredConversations.map(conv => (
              <ConversationCard
                key={conv.conversation_id}
                conversation={conv}
                currentUserId={user.id}
                onClick={() => navigate(`/messages/${conv.conversation_id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function ConversationCard({ conversation, currentUserId, onClick }) {
  const { other_user, last_message, unread_count } = conversation

  const isUnread = last_message.sender_id !== currentUserId && !last_message.is_read
  const timestamp = new Date(last_message.created_at)
  const timeAgo = formatTimeAgo(timestamp)

  return (
    <div
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-4)',
        background: 'var(--white)',
                padding: 'var(--space-5)',
        cursor: 'pointer',
        transition: 'all 0.2s',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
        border: isUnread ? '2px solid #DC2626' : '2px solid #E5E7EB',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateX(4px)'
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateX(0)'
        e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)'
      }}
    >
      {/* Avatar */}
      <div style={{
        width: '56px',
        height: '56px',
        borderRadius: '50%',
        background: 'var(--red-accent)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 'var(--space-5)',
        fontWeight: 700,
        color: 'var(--white)',
        flexShrink: 0,
      }}>
        {getInitials(other_user.full_name || other_user.email)}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '6px',
          gap: 'var(--space-3)',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
            flex: 1,
            minWidth: 0,
          }}>
            <div style={{
              fontSize: 'var(--space-4)',
              fontWeight: 600,
              color: 'var(--text-primary)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {other_user.full_name || other_user.email}
            </div>
            {getRoleBadge(other_user.role)}
          </div>
          <div style={{
            fontSize: '13px',
            color: '#6B7280',
            whiteSpace: 'nowrap',
          }}>
            {timeAgo}
          </div>
        </div>

        <div style={{
          fontSize: '14px',
          color: isUnread ? 'var(--text-primary)' : '#6B7280',
          fontWeight: isUnread ? 600 : 400,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {last_message.sender_id === currentUserId && '✓ '}
          {last_message.content.slice(0, 60)}
          {last_message.content.length > 60 && '...'}
        </div>
      </div>

      {/* Unread Badge */}
      {unread_count > 0 && (
        <div style={{
          minWidth: 'var(--space-7)',
          height: 'var(--space-7)',
          borderRadius: '50%',
          background: 'var(--red-accent)',
          color: 'var(--white)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '13px',
          fontWeight: 700,
          flexShrink: 0,
        }}>
          {unread_count}
        </div>
      )}
    </div>
  )
}

function getInitials(name) {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function getRoleBadge(role) {
  const badges = {
    'PRO': (
      <span style={{
        background: 'var(--red-accent)',
        color: 'var(--white)',
        padding: '2px 8px',
                fontSize: '11px',
        fontWeight: 600,
      }}>
         Pro
      </span>
    ),
    'EXPERT': (
      <span style={{
        background: '#F59E0B',
        color: 'var(--white)',
        padding: '2px 8px',
                fontSize: '11px',
        fontWeight: 600,
      }}>
         Expert
      </span>
    ),
    'ADMIN': (
      <span style={{
        background: 'var(--text-primary)',
        color: 'var(--white)',
        padding: '2px 8px',
                fontSize: '11px',
        fontWeight: 600,
      }}>
         Admin
      </span>
    )
  }
  return badges[role] || null
}

function formatTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000)

  if (seconds < 60) return 'À l\'instant'
  if (seconds < 3600) return `Il y a ${Math.floor(seconds / 60)} min`
  if (seconds < 86400) return `Il y a ${Math.floor(seconds / 3600)} h`
  if (seconds < 604800) return `Il y a ${Math.floor(seconds / 86400)} j`

  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}
