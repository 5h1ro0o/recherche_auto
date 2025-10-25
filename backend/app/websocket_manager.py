# backend/app/websocket_manager.py
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Gestionnaire centralisé des connexions WebSocket"""
    
    def __init__(self):
        # Dict[user_id, List[WebSocket]]
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accepter une nouvelle connexion WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connecté: user {user_id} (total: {len(self.active_connections[user_id])})")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Supprimer une connexion WebSocket"""
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"WebSocket déconnecté: user {user_id}")
                
                # Nettoyer si plus de connexions
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Envoyer un message à toutes les connexions d'un utilisateur"""
        if user_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Erreur envoi message WS à {user_id}: {e}")
                    disconnected.append(connection)
            
            # Nettoyer les connexions mortes
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast_to_users(self, message: dict, user_ids: List[str]):
        """Envoyer un message à plusieurs utilisateurs"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def is_user_connected(self, user_id: str) -> bool:
        """Vérifier si un utilisateur a des connexions actives"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_connection_count(self, user_id: str) -> int:
        """Obtenir le nombre de connexions d'un utilisateur"""
        return len(self.active_connections.get(user_id, []))

# Instance globale
ws_manager = WebSocketManager()