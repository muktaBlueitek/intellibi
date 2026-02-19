from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Types of notifications."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DASHBOARD_SHARED = "dashboard_shared"
    DASHBOARD_UPDATED = "dashboard_updated"
    DATA_SOURCE_UPDATED = "data_source_updated"
    QUERY_COMPLETE = "query_complete"
    SYSTEM = "system"


class Notification(Base):
    """Model for user notifications."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(NotificationType), default=NotificationType.INFO, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    # Optional metadata (e.g., link to dashboard, action buttons)
    metadata = Column(JSON, nullable=True)
    
    # Read status
    is_read = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.type.value} for user {self.user_id}>"
