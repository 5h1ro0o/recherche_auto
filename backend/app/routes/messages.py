# backend/app/routes/messages.py
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.db import SessionLocal
from app.models import User, Message
from app.schemas import MessageCreate, MessageOut, ConversationOut
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/messages", tags=["messages"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")

manager = ConnectionManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ REST ENDPOINTS ============

@router.get("/conversations", response_model=List[ConversationOut])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer toutes mes conversations"""
    # Récupérer tous les messages où je suis sender ou recipient
    messages = db.query(Message).filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.created_at.desc()).all()
    
    # Grouper par conversation_id
    conversations = {}
    for msg in messages:
        conv_id = msg.conversation_id
        if conv_id not in conversations:
            # Déterminer l'autre participant
            other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
            other_user = db.get(User, other_user_id)
            
            conversations[conv_id] = {
                "conversation_id": conv_id,
                "other_user": {
                    "id": other_user.id,
                    "email": other_user.email,
                    "full_name": other_user.full_name,
                    "role": other_user.role
                },
                "last_message": {
                    "content": msg.content,
                    "created_at": msg.created_at,
                    "is_read": msg.is_read,
                    "sender_id": msg.sender_id
                },
                "unread_count": 0
            }
        
        # Compter les non lus
        if msg.recipient_id == current_user.id and not msg.is_read:
            conversations[conv_id]["unread_count"] += 1
    
    return list(conversations.values())

@router.post("/conversations/{other_user_id}")
async def get_or_create_conversation(
    other_user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer ou récupérer une conversation avec un utilisateur"""
    if other_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas créer une conversation avec vous-même"
        )
    
    # Vérifier que l'autre utilisateur existe
    other_user = db.get(User, other_user_id)
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Chercher conversation existante
    existing = db.query(Message).filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.recipient_id == current_user.id))
    ).first()
    
    if existing:
        conversation_id = existing.conversation_id
    else:
        # Créer nouvel ID de conversation
        conversation_id = f"{min(current_user.id, other_user_id)}_{max(current_user.id, other_user_id)}"
    
    return {
        "conversation_id": conversation_id,
        "other_user": {
            "id": other_user.id,
            "email": other_user.email,
            "full_name": other_user.full_name,
            "role": other_user.role
        }
    }

@router.get("/{conversation_id}", response_model=List[MessageOut])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """Récupérer l'historique d'une conversation"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        ((Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    # Marquer comme lus les messages reçus
    for msg in messages:
        if msg.recipient_id == current_user.id and not msg.is_read:
            msg.is_read = True
            msg.read_at = datetime.utcnow()
    
    db.commit()
    
    return list(reversed(messages))

@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Envoyer un message"""
    # Vérifier que le destinataire existe
    recipient = db.get(User, message_data.recipient_id)
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destinataire non trouvé"
        )
    
    if message_data.recipient_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas vous envoyer un message"
        )
    
    # Créer conversation_id standard
    conversation_id = f"{min(current_user.id, message_data.recipient_id)}_{max(current_user.id, message_data.recipient_id)}"
    
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        content=message_data.content,
        attachments=message_data.attachments or [],
        is_read=False
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    logger.info(f"Message envoyé: {current_user.id} -> {message_data.recipient_id}")
    
    # Envoyer via WebSocket au destinataire
    await manager.send_personal_message(
        {
            "type": "new_message",
            "message": {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "sender": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "full_name": current_user.full_name
                }
            }
        },
        message_data.recipient_id
    )
    
    return message

@router.patch("/{message_id}/read", response_model=MessageOut)
async def mark_as_read(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marquer un message comme lu"""
    message = db.get(Message, message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message non trouvé"
        )
    
    if message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas le destinataire de ce message"
        )
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    return message

@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compter les messages non lus"""
    count = db.query(Message).filter(
        Message.recipient_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return {"unread_count": count}

# ============ WEBSOCKET ENDPOINT ============

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    """WebSocket pour messages temps réel"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Recevoir messages du client (ping/pong pour keep-alive)
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)