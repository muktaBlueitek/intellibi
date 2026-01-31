from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.datasource import DataSourceType


class DataSourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: DataSourceType
    connection_config: Optional[Dict[str, Any]] = None


class DataSourceCreate(DataSourceBase):
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    api_url: Optional[str] = None
    api_key: Optional[str] = None


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DataSource(DataSourceBase):
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
