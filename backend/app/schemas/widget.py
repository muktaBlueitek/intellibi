from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.widget import WidgetType


class WidgetBase(BaseModel):
    name: str
    type: WidgetType
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    query: Optional[str] = None
    datasource_id: Optional[int] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 4
    height: int = 3


class WidgetCreate(WidgetBase):
    dashboard_id: int


class WidgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    query: Optional[str] = None
    datasource_id: Optional[int] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class Widget(WidgetBase):
    id: int
    dashboard_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
