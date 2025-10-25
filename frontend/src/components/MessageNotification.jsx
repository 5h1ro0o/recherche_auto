// frontend/src/components/MessageNotification.jsx
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import useSWR from 'swr'
import { getUnreadCount, connectWebSocket } from '../services/messages'

export default function MessageNotification() {
  const { user, isAuthenticated } = useAuth()
  const [unreadCount, setUnreadCount] = useState(0)

  // Charger le compte initial
  const { data } = useSWR(
    isAuthenticated ? '/messages/unread/count' : null,
    getUnreadCount,
    { refreshInterval: 30000 } // Refresh toutes les 30 secondes
  )

  useEffect(() => {
    if (data?.unread_count !== undefined) {
      setUnreadCount(data.unread_count)
    }
  }, [data])

  // WebSocket pour mises à jour temps réel
  useEffect(() => {
    if (!isAuthenticated || !user) return

    const ws = connectWebSocket(user.id)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'new_message') {
        // Incrémenter le compteur si on n'est pas sur la page de conversation
        const isOnMessagesPage = window.location.pathname.startsWith('/messages')
        if (!isOnMessagesPage) {
          setUnreadCount(prev => prev + 1)
        }
      }
    }

    return () => {
      // Ne pas déconnecter ici car d'autres composants peuvent utiliser le WS
    }
  }, [isAuthenticated, user])

  if (!isAuthenticated) return null

  return (
    <Link to="/messages" className="message-notification-btn">
      💬
      {unreadCount > 0 && (
        <span className="notification-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
      )}
    </Link>
  )
}