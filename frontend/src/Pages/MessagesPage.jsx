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
      <div className="messages-page">
        <div className="error-message">Erreur lors du chargement des conversations</div>
      </div>
    )
  }

  if (!conversations) {
    return (
      <div className="messages-page">
        <div className="loading">Chargement de vos conversations...</div>
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
    <div className="messages-page">
      <div className="messages-header">
        <h1>💬 Mes Conversations</h1>
        {totalUnread > 0 && (
          <span className="unread-badge">{totalUnread} non lu(s)</span>
        )}
      </div>

      <div className="messages-filters">
        <button
          className={`filter-btn ${selectedFilter === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('all')}
        >
          Toutes ({conversations.length})
        </button>
        <button
          className={`filter-btn ${selectedFilter === 'unread' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('unread')}
        >
          Non lues ({totalUnread})
        </button>
      </div>

      {filteredConversations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>Aucune conversation</h3>
          <p>
            {selectedFilter === 'unread' 
              ? 'Vous n\'avez pas de messages non lus'
              : 'Vous n\'avez pas encore de conversations'
            }
          </p>
        </div>
      ) : (
        <div className="conversations-list">
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
  )
}

function ConversationCard({ conversation, currentUserId, onClick }) {
  const { other_user, last_message, unread_count } = conversation
  
  const isUnread = last_message.sender_id !== currentUserId && !last_message.is_read
  const timestamp = new Date(last_message.created_at)
  const timeAgo = formatTimeAgo(timestamp)

  return (
    <div 
      className={`conversation-card ${isUnread ? 'unread' : ''}`}
      onClick={onClick}
    >
      <div className="conversation-avatar">
        {getInitials(other_user.full_name || other_user.email)}
      </div>
      
      <div className="conversation-content">
        <div className="conversation-header">
          <div className="conversation-name">
            {other_user.full_name || other_user.email}
            {getRoleBadge(other_user.role)}
          </div>
          <div className="conversation-time">{timeAgo}</div>
        </div>
        
        <div className="conversation-preview">
          <span className={isUnread ? 'unread-text' : ''}>
            {last_message.sender_id === currentUserId && '✓ '}
            {last_message.content.slice(0, 60)}
            {last_message.content.length > 60 && '...'}
          </span>
        </div>
      </div>
      
      {unread_count > 0 && (
        <div className="unread-count">{unread_count}</div>
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
    'PRO': <span className="role-badge pro">🏢 Pro</span>,
    'EXPERT': <span className="role-badge expert">⭐ Expert</span>,
    'ADMIN': <span className="role-badge admin">🔧 Admin</span>
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