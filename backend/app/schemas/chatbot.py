from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    conversation_id: int


class ChatMessage(ChatMessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


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


class VisualizationSuggestion(BaseModel):
    chart_type: str
    config: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None


class StatisticalSummary(BaseModel):
    column: str
    mean: Optional[float] = None
    median: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    std_dev: Optional[float] = None
    count: Optional[int] = None


class QueryInsights(BaseModel):
    summary: Optional[str] = None
    trends: Optional[List[str]] = None
    anomalies: Optional[List[str]] = None
    correlations: Optional[List[str]] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    sql_query: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    visualization_suggestion: Optional[VisualizationSuggestion] = None
    statistical_summary: Optional[List[StatisticalSummary]] = None
    insights: Optional[QueryInsights] = None
    suggested_queries: Optional[List[str]] = None
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


class QueryHistoryFilter(BaseModel):
    datasource_id: Optional[int] = None
    success: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None


class QueryHistoryStats(BaseModel):
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_execution_time: Optional[float] = None
    most_common_queries: Optional[List[Dict[str, Any]]] = None
