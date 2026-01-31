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
    widgets: List["WidgetSchema"] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
