from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.schemas.widget import Widget as WidgetSchema


class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_public: bool = False
    is_shared: bool = False


class DashboardCreate(DashboardBase):
    pass


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_shared: Optional[bool] = None


class Dashboard(DashboardBase):
    id: int
    owner_id: int
    version: int
    widgets: List["WidgetSchema"] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sharing schemas
class DashboardShareCreate(BaseModel):
    user_id: int
    permission: str = "view"  # view, edit, admin


class DashboardShareUpdate(BaseModel):
    permission: str


class DashboardShare(BaseModel):
    id: int
    dashboard_id: int
    user_id: int
    permission: str
    shared_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Versioning schemas
class DashboardVersionCreate(BaseModel):
    comment: Optional[str] = None


class DashboardVersion(BaseModel):
    id: int
    dashboard_id: int
    version_number: int
    name: str
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    widgets_snapshot: Optional[List[Dict[str, Any]]] = None
    created_by_id: int
    created_at: datetime
    comment: Optional[str] = None

    class Config:
        from_attributes = True


# Layout schemas
class LayoutUpdate(BaseModel):
    layout_config: Dict[str, Any]
