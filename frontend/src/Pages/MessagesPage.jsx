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

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
        padding: '80px 20px',
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          textAlign: 'center',
          background: 'white',
          borderRadius: '16px',
          padding: '40px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>⚠️</div>
          <h3 style={{ fontSize: '24px', color: '#222222', marginBottom: '12px' }}>
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
        background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
        padding: '80px 20px',
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
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
      background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
      paddingBottom: '60px',
    }}>
      {/* Header Section */}
      <div style={{
        background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
        color: 'white',
        padding: '60px 20px',
        marginBottom: '40px',
      }}>
        <div style={{
          maxWidth: '900px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}>
          <h1 style={{
            fontSize: '42px',
            fontWeight: 700,
            margin: 0,
            lineHeight: 1.2,
          }}>
            💬 Mes Conversations
          </h1>
          {totalUnread > 0 && (
            <div style={{
              background: '#EF4444',
              color: 'white',
              padding: '8px 20px',
              borderRadius: '20px',
              fontSize: '16px',
              fontWeight: 600,
              boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)',
            }}>
              {totalUnread} non lu{totalUnread > 1 ? 's' : ''}
            </div>
          )}
        </div>
      </div>

      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '0 20px',
      }}>
        {/* Filters */}
        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '24px',
        }}>
          <button
            onClick={() => setSelectedFilter('all')}
            style={{
              padding: '12px 24px',
              background: selectedFilter === 'all' ? '#4F46E5' : 'white',
              color: selectedFilter === 'all' ? 'white' : '#222222',
              border: selectedFilter === 'all' ? 'none' : '2px solid #E5E7EB',
              borderRadius: '12px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (selectedFilter !== 'all') {
                e.target.style.borderColor = '#4F46E5'
              }
            }}
            onMouseLeave={(e) => {
              if (selectedFilter !== 'all') {
                e.target.style.borderColor = '#E5E7EB'
              }
            }}
          >
            Toutes ({conversations.length})
          </button>
          <button
            onClick={() => setSelectedFilter('unread')}
            style={{
              padding: '12px 24px',
              background: selectedFilter === 'unread' ? '#4F46E5' : 'white',
              color: selectedFilter === 'unread' ? 'white' : '#222222',
              border: selectedFilter === 'unread' ? 'none' : '2px solid #E5E7EB',
              borderRadius: '12px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (selectedFilter !== 'unread') {
                e.target.style.borderColor = '#4F46E5'
              }
            }}
            onMouseLeave={(e) => {
              if (selectedFilter !== 'unread') {
                e.target.style.borderColor = '#E5E7EB'
              }
            }}
          >
            Non lues ({totalUnread})
          </button>
        </div>

        {filteredConversations.length === 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '60px 40px',
            textAlign: 'center',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
          }}>
            <div style={{ fontSize: '80px', marginBottom: '24px' }}>📭</div>
            <h3 style={{
              fontSize: '28px',
              fontWeight: 700,
              color: '#222222',
              margin: '0 0 12px 0',
            }}>
              Aucune conversation
            </h3>
            <p style={{
              fontSize: '16px',
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
            gap: '12px',
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
        gap: '16px',
        background: 'white',
        borderRadius: '12px',
        padding: '20px',
        cursor: 'pointer',
        transition: 'all 0.2s',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
        border: isUnread ? '2px solid #4F46E5' : '2px solid #E5E7EB',
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
        background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '20px',
        fontWeight: 700,
        color: 'white',
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
          gap: '12px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            flex: 1,
            minWidth: 0,
          }}>
            <div style={{
              fontSize: '16px',
              fontWeight: 600,
              color: '#222222',
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
          color: isUnread ? '#222222' : '#6B7280',
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
          minWidth: '28px',
          height: '28px',
          borderRadius: '50%',
          background: '#EF4444',
          color: 'white',
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
        background: '#4F46E5',
        color: 'white',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 600,
      }}>
        🏢 Pro
      </span>
    ),
    'EXPERT': (
      <span style={{
        background: '#F59E0B',
        color: 'white',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 600,
      }}>
        ⭐ Expert
      </span>
    ),
    'ADMIN': (
      <span style={{
        background: '#EF4444',
        color: 'white',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 600,
      }}>
        🔧 Admin
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
