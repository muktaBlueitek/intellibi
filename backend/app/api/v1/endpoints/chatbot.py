from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from datetime import datetime

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
    QueryHistory as QueryHistorySchema,
    QueryHistoryFilter,
    QueryHistoryStats
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
    datasource_id: Optional[int] = Query(None),
    success: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search_text: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get query history for the current user with filtering options."""
    query = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id)
    
    # Apply filters
    if datasource_id:
        query = query.filter(QueryHistory.datasource_id == datasource_id)
    
    if success:
        query = query.filter(QueryHistory.success == success)
    
    if start_date:
        query = query.filter(QueryHistory.created_at >= start_date)
    
    if end_date:
        query = query.filter(QueryHistory.created_at <= end_date)
    
    if search_text:
        search_filter = or_(
            QueryHistory.query_text.ilike(f"%{search_text}%"),
            QueryHistory.sql_query.ilike(f"%{search_text}%")
        )
        query = query.filter(search_filter)
    
    queries = query.order_by(desc(QueryHistory.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return queries


@router.get("/query-history/stats", response_model=QueryHistoryStats)
def get_query_history_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get query history statistics for the current user."""
    # Total queries
    total_queries = db.query(QueryHistory).filter(
        QueryHistory.user_id == current_user.id
    ).count()
    
    # Successful queries
    successful_queries = db.query(QueryHistory).filter(
        QueryHistory.user_id == current_user.id,
        QueryHistory.success == "true"
    ).count()
    
    # Failed queries
    failed_queries = total_queries - successful_queries
    
    # Average execution time
    avg_execution_time = db.query(func.avg(QueryHistory.execution_time)).filter(
        QueryHistory.user_id == current_user.id,
        QueryHistory.execution_time.isnot(None)
    ).scalar()
    
    # Most common queries (top 5)
    most_common = db.query(
        QueryHistory.query_text,
        func.count(QueryHistory.id).label('count')
    ).filter(
        QueryHistory.user_id == current_user.id
    ).group_by(
        QueryHistory.query_text
    ).order_by(
        desc('count')
    ).limit(5).all()
    
    most_common_queries = [
        {"query_text": q[0], "count": q[1]} for q in most_common
    ]
    
    return QueryHistoryStats(
        total_queries=total_queries,
        successful_queries=successful_queries,
        failed_queries=failed_queries,
        average_execution_time=float(avg_execution_time) if avg_execution_time else None,
        most_common_queries=most_common_queries
    )
