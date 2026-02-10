from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class ChatMessageBase(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    conversation_id: int


class ChatMessage(ChatMessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    datasource_id: Optional[int] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    sql_query: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    visualization_suggestion: Optional[str] = None
    message_id: int


class QueryHistoryBase(BaseModel):
    query_text: str
    sql_query: Optional[str] = None
    datasource_id: Optional[int] = None
    execution_time: Optional[float] = None
    result_count: Optional[int] = None
    success: str = "true"
    error_message: Optional[str] = None


class QueryHistory(QueryHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
