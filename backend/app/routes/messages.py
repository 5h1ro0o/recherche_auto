# backend/app/routes/messages.py - VERSION COMPLÈTE
import uuid
import logging
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.db import SessionLocal
from app.models import User, Message
from app.schemas import MessageCreate, MessageOut, ConversationOut
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/messages", tags=["messages"])

# Configuration uploads
UPLOAD_DIR = Path("uploads/messages")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Templates de messages
MESSAGE_TEMPLATES = {
    "interested": {
        "label": "Intéressé par le véhicule",
        "text": "Bonjour, je suis intéressé(e) par ce véhicule. Est-il toujours disponible ?"
    },
    "request_info": {
        "label": "Demander des informations",
        "text": "Pourriez-vous me donner plus d'informations sur l'état du véhicule (historique d'entretien, accidents, etc.) ?"
    },
    "schedule_visit": {
        "label": "Planifier une visite",
        "text": "Serait-il possible d'organiser une visite pour voir le véhicule ? Je suis disponible cette semaine."
    },
    "price_negotiation": {
        "label": "Négocier le prix",
        "text": "Le prix est-il négociable ? Je suis sérieusement intéressé(e)."
    },
    "request_documents": {
        "label": "Demander les documents",
        "text": "Pourriez-vous me transmettre le certificat de non-gage et le rapport de contrôle technique ?"
    },
    "thank_you": {
        "label": "Remercier",
        "text": "Merci pour votre réponse rapide et les informations détaillées !"
    },
    "payment_method": {
        "label": "Moyen de paiement",
        "text": "Quels moyens de paiement acceptez-vous ? (chèque de banque, virement, etc.)"
    },
    "test_drive": {
        "label": "Essai routier",
        "text": "Est-il possible d'effectuer un essai routier du véhicule ?"
    }
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.typing_status: Dict[str, Dict[str, bool]] = {}  # {conversation_id: {user_id: is_typing}}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast_typing_status(self, conversation_id: str, user_id: str, is_typing: bool, recipient_id: str):
        """Diffuser le statut 'en train d'écrire'"""
        await self.send_personal_message(
            {
                "type": "typing_status",
                "conversation_id": conversation_id,
                "user_id": user_id,
                "is_typing": is_typing
            },
            recipient_id
        )

manager = ConnectionManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ TEMPLATES ============

@router.get("/templates")
async def get_message_templates():
    """Récupérer les templates de messages pré-définis"""
    return {"templates": MESSAGE_TEMPLATES}

# ============ ATTACHMENTS ============

@router.post("/attachments")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload un fichier joint (image uniquement)"""
    
    # Vérifier l'extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non supporté. Extensions autorisées: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Lire et vérifier la taille
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop volumineux (max 5MB)"
        )
    
    # Générer nom unique
    filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
    filepath = UPLOAD_DIR / filename
    
    # Sauvegarder
    try:
        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Erreur upload fichier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la sauvegarde du fichier"
        )
    
    logger.info(f"Fichier uploadé: {filename} par {current_user.email}")
    
    return {
        "url": f"/uploads/messages/{filename}",
        "filename": file.filename,
        "size": len(contents),
        "type": file.content_type
    }

# ============ REST ENDPOINTS (Existants + Améliorations) ============

@router.get("/conversations", response_model=List[ConversationOut])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer toutes mes conversations"""
    messages = db.query(Message).filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.created_at.desc()).all()
    
    conversations = {}
    for msg in messages:
        conv_id = msg.conversation_id
        if conv_id not in conversations:
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
    
    other_user = db.get(User, other_user_id)
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    existing = db.query(Message).filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.recipient_id == current_user.id))
    ).first()
    
    if existing:
        conversation_id = existing.conversation_id
    else:
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
    
    # Marquer comme lus
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
    
    # Envoyer via WebSocket
    await manager.send_personal_message(
        {
            "type": "new_message",
            "message": {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "attachments": message.attachments,
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
            detail="Vous n'êtes pas le destinataire"
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

# ============ WEBSOCKET ============

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket pour messages temps réel + typing indicators"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif data.get("type") == "typing_start":
                # Diffuser que l'utilisateur est en train d'écrire
                conversation_id = data.get("conversation_id")
                recipient_id = data.get("recipient_id")
                
                if conversation_id and recipient_id:
                    await manager.broadcast_typing_status(
                        conversation_id, user_id, True, recipient_id
                    )
            
            elif data.get("type") == "typing_stop":
                # Diffuser que l'utilisateur a arrêté d'écrire
                conversation_id = data.get("conversation_id")
                recipient_id = data.get("recipient_id")
                
                if conversation_id and recipient_id:
                    await manager.broadcast_typing_status(
                        conversation_id, user_id, False, recipient_id
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)