from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.chatbot import Conversation, ChatMessage, QueryHistory
from app.models.user import User
from app.schemas.chatbot import (
    ChatRequest,
    ChatResponse,
    Conversation as ConversationSchema,
    ConversationCreate,
    ConversationList,
    ChatMessage as ChatMessageSchema,
    QueryHistory as QueryHistorySchema
)
from app.api.v1.deps import get_current_active_user
from app.services.chatbot import ChatbotService

router = APIRouter()
chatbot_service = ChatbotService()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a message to the chatbot and get a response."""
    try:
        result = chatbot_service.process_message(
            user=current_user,
            message=request.message,
            conversation_id=request.conversation_id,
            datasource_id=request.datasource_id,
            db=db
        )
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationList])
def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all conversations for the current user."""
    conversations = db.query(Conversation)\
        .filter(Conversation.user_id == current_user.id)\
        .order_by(desc(Conversation.updated_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    result = []
    for conv in conversations:
        message_count = db.query(ChatMessage)\
            .filter(ChatMessage.conversation_id == conv.id)\
            .count()
        
        result.append(ConversationList(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count
        ))
    
    return result


@router.post("/conversations", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new conversation."""
    db_conversation = Conversation(
        user_id=current_user.id,
        title=conversation.title
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a conversation with all its messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    return None


@router.get("/query-history", response_model=List[QueryHistorySchema])
def get_query_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get query history for the current user."""
    queries = db.query(QueryHistory)\
        .filter(QueryHistory.user_id == current_user.id)\
        .order_by(desc(QueryHistory.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return queries
