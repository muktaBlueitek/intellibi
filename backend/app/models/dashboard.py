from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

# Association table for many-to-many relationship between dashboards and datasources
dashboard_datasources = Table(
    "dashboard_datasources",
    Base.metadata,
    Column("dashboard_id", Integer, ForeignKey("dashboards.id"), primary_key=True),
    Column("datasource_id", Integer, ForeignKey("datasources.id"), primary_key=True),
)


class SharePermission(str, enum.Enum):
    """Permissions for shared dashboards."""
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin"


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
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    current_version_id = Column(Integer, ForeignKey("dashboard_versions.id"), nullable=True)
    
    # Metadata
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", backref="dashboards")
    widgets = relationship("Widget", back_populates="dashboard", cascade="all, delete-orphan")
    datasources = relationship("DataSource", secondary=dashboard_datasources, back_populates="dashboards")
    shares = relationship("DashboardShare", back_populates="dashboard", cascade="all, delete-orphan")
    versions = relationship("DashboardVersion", back_populates="dashboard", cascade="all, delete-orphan", foreign_keys="DashboardVersion.dashboard_id")
    current_version = relationship("DashboardVersion", foreign_keys=[current_version_id], remote_side="DashboardVersion.id", post_update=True)
    
    def __repr__(self):
        return f"<Dashboard {self.name}>"


class DashboardShare(Base):
    """Model for dashboard sharing with specific users."""
    __tablename__ = "dashboard_shares"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    permission = Column(Enum(SharePermission), default=SharePermission.VIEW, nullable=False)
    
    # Metadata
    shared_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="shares")
    user = relationship("User", foreign_keys=[user_id], backref="shared_dashboards")
    shared_by = relationship("User", foreign_keys=[shared_by_id])
    
    def __repr__(self):
        return f"<DashboardShare dashboard_id={self.dashboard_id} user_id={self.user_id} permission={self.permission.value}>"


class DashboardVersion(Base):
    """Model for dashboard versioning."""
    __tablename__ = "dashboard_versions"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, index=True)
    
    # Snapshot of dashboard state
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    layout_config = Column(JSON, nullable=True)
    
    # Widgets snapshot (stored as JSON array)
    widgets_snapshot = Column(JSON, nullable=True)
    
    # Metadata
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    comment = Column(Text, nullable=True)  # Optional comment for version
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="versions", foreign_keys=[dashboard_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<DashboardVersion dashboard_id={self.dashboard_id} version={self.version_number}>"
