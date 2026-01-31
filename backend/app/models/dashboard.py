from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table for many-to-many relationship between dashboards and datasources
dashboard_datasources = Table(
    "dashboard_datasources",
    Base.metadata,
    Column("dashboard_id", Integer, ForeignKey("dashboards.id"), primary_key=True),
    Column("datasource_id", Integer, ForeignKey("datasources.id"), primary_key=True),
)


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Layout configuration (stored as JSON)
    layout_config = Column(JSON, nullable=True, default=dict)
    
    # Sharing and permissions
    is_public = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    
    # Metadata
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", backref="dashboards")
    widgets = relationship("Widget", back_populates="dashboard", cascade="all, delete-orphan")
    datasources = relationship("DataSource", secondary=dashboard_datasources, back_populates="dashboards")
    
    def __repr__(self):
        return f"<Dashboard {self.name}>"
