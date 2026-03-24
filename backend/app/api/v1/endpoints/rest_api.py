"""REST API data source endpoints."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.datasource import DataSource, DataSourceType
from app.models.user import User
from app.schemas.datasource import DataSource as DataSourceSchema
from app.api.v1.deps import get_current_active_user
from app.services.rest_api_connector import RestApiConnector

router = APIRouter()
rest_api_connector = RestApiConnector()


class RestApiConnectionTest(BaseModel):
    """Request body for testing REST API connection."""

    url: str
    auth_type: str = "bearer"  # bearer, api_key, none
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    data_path: Optional[str] = None


class RestApiConnectionCreate(BaseModel):
    """Request body for creating REST API data source."""

    url: str
    name: str
    description: Optional[str] = None
    auth_type: str = "bearer"
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    data_path: Optional[str] = None


@router.post("/test", response_model=dict)
def test_rest_api_connection(
    connection: RestApiConnectionTest,
    current_user: User = Depends(get_current_active_user),
):
    """Test a REST API connection by fetching the URL."""
    result = rest_api_connector.test_connection(
        url=connection.url,
        auth_type=connection.auth_type,
        api_key=connection.api_key,
        headers=connection.headers,
        data_path=connection.data_path,
    )
    return result


@router.post("/", response_model=DataSourceSchema, status_code=status.HTTP_201_CREATED)
def create_rest_api_connection(
    connection: RestApiConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new REST API data source."""
    # Test connection first
    test_result = rest_api_connector.test_connection(
        url=connection.url,
        auth_type=connection.auth_type,
        api_key=connection.api_key,
        headers=connection.headers,
        data_path=connection.data_path,
    )

    if not test_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {test_result.get('message', 'Unknown error')}",
        )

    connection_config: Dict[str, Any] = {
        "auth_type": connection.auth_type,
        "data_path": connection.data_path,
    }
    if connection.headers:
        connection_config["headers"] = connection.headers
    if connection.api_key:
        connection_config["api_key"] = connection.api_key

    db_datasource = DataSource(
        name=connection.name,
        description=connection.description or f"REST API: {connection.url}",
        type=DataSourceType.REST_API,
        api_url=connection.url,
        api_key=connection.api_key,
        connection_config=connection_config,
        is_active=True,
        owner_id=current_user.id,
    )

    db.add(db_datasource)
    db.commit()
    db.refresh(db_datasource)
    return db_datasource
