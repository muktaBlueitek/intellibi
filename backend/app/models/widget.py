from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class WidgetType(str, enum.Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    TABLE = "table"
    HEATMAP = "heatmap"
    METRIC = "metric"
    TEXT = "text"


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(WidgetType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Widget configuration (stored as JSON)
    config = Column(JSON, nullable=True, default=dict)
    
    # Query configuration
    query = Column(Text, nullable=True)
    datasource_id = Column(Integer, ForeignKey("datasources.id"), nullable=True)
    
    # Layout position
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)
    
    # Metadata
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")
    datasource = relationship("DataSource", backref="widgets")
    
    def __repr__(self):
        return f"<Widget {self.name} ({self.type.value})>"
