from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class DataSourceType(str, enum.Enum):
    FILE = "file"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REST_API = "rest_api"


class DataSource(Base):
    __tablename__ = "datasources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(DataSourceType), nullable=False)
    
    # Connection details (stored as JSON for flexibility)
    connection_config = Column(JSON, nullable=True)
    
    # File-specific fields
    file_path = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Database connection fields
    host = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    database_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    # Password should be encrypted in production
    
    # API connection fields
    api_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", backref="datasources")
    dashboards = relationship("Dashboard", secondary="dashboard_datasources", back_populates="datasources")
    
    def __repr__(self):
        return f"<DataSource {self.name} ({self.type.value})>"
