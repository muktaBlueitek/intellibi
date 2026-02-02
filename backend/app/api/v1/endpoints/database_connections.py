from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.datasource import DataSource, DataSourceType
from app.models.user import User
from app.schemas.datasource import DataSource as DataSourceSchema, DataSourceCreate
from app.api.v1.deps import get_current_active_user
from app.services.database_connector import DatabaseConnector

router = APIRouter()
db_connector = DatabaseConnector()


class DatabaseConnectionTest(BaseModel):
    datasource_id: Optional[int] = None
    type: DataSourceType
    host: str
    port: int
    database_name: str
    username: str
    password: str


class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 1000


@router.post("/test", response_model=dict)
def test_database_connection(
    connection: DatabaseConnectionTest,
    current_user: User = Depends(get_current_active_user)
):
    """Test a database connection."""
    # Create temporary datasource object for testing
    test_datasource = DataSource(
        id=connection.datasource_id or 0,
        type=connection.type,
        host=connection.host,
        port=connection.port,
        database_name=connection.database_name,
        username=connection.username,
        owner_id=current_user.id
    )
    
    result = db_connector.test_connection(test_datasource, connection.password)
    return result


@router.post("/", response_model=DataSourceSchema, status_code=status.HTTP_201_CREATED)
def create_database_connection(
    connection: DatabaseConnectionTest,
    name: str = Body(...),
    description: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new database connection data source."""
    # Test connection first
    test_datasource = DataSource(
        id=0,
        type=connection.type,
        host=connection.host,
        port=connection.port,
        database_name=connection.database_name,
        username=connection.username,
        owner_id=current_user.id
    )
    
    test_result = db_connector.test_connection(test_datasource, connection.password)
    if not test_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {test_result.get('message', 'Unknown error')}"
        )
    
    # Encrypt password for storage
    from app.services.database_connector import DatabaseConnector
    connector = DatabaseConnector()
    encrypted_password = connector._encrypt_password(connection.password)
    
    # Create datasource
    db_datasource = DataSource(
        name=name,
        description=description,
        type=connection.type,
        host=connection.host,
        port=connection.port,
        database_name=connection.database_name,
        username=connection.username,
        connection_config={
            "encrypted_password": encrypted_password
        },
        is_active=True,
        owner_id=current_user.id
    )
    
    db.add(db_datasource)
    db.commit()
    db.refresh(db_datasource)
    return db_datasource


@router.post("/{datasource_id}/test", response_model=dict)
def test_existing_connection(
    datasource_id: int,
    password: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Test an existing database connection."""
    datasource = db.query(DataSource).filter(
        DataSource.id == datasource_id,
        DataSource.owner_id == current_user.id,
        DataSource.type.in_([DataSourceType.POSTGRESQL, DataSourceType.MYSQL])
    ).first()
    
    if datasource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    
    result = db_connector.test_connection(datasource, password)
    return result


@router.post("/{datasource_id}/query", response_model=dict)
def execute_query(
    datasource_id: int,
    query_request: QueryRequest,
    password: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Execute a SQL query on a database connection."""
    datasource = db.query(DataSource).filter(
        DataSource.id == datasource_id,
        DataSource.owner_id == current_user.id,
        DataSource.type.in_([DataSourceType.POSTGRESQL, DataSourceType.MYSQL])
    ).first()
    
    if datasource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    
    result = db_connector.execute_query(
        datasource,
        query_request.query,
        password,
        query_request.limit
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Query execution failed")
        )
    
    return result


@router.get("/{datasource_id}/tables", response_model=list)
def get_tables(
    datasource_id: int,
    password: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of tables in the database."""
    datasource = db.query(DataSource).filter(
        DataSource.id == datasource_id,
        DataSource.owner_id == current_user.id,
        DataSource.type.in_([DataSourceType.POSTGRESQL, DataSourceType.MYSQL])
    ).first()
    
    if datasource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    
    try:
        tables = db_connector.get_tables(datasource, password)
        return tables
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{datasource_id}/tables/{table_name}/schema", response_model=dict)
def get_table_schema(
    datasource_id: int,
    table_name: str,
    password: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get schema information for a specific table."""
    datasource = db.query(DataSource).filter(
        DataSource.id == datasource_id,
        DataSource.owner_id == current_user.id,
        DataSource.type.in_([DataSourceType.POSTGRESQL, DataSourceType.MYSQL])
    ).first()
    
    if datasource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    
    try:
        schema = db_connector.get_table_schema(datasource, table_name, password)
        return schema
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
