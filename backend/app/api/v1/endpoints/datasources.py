from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.datasource import DataSource, DataSourceType
from app.models.user import User
from app.schemas.datasource import DataSource as DataSourceSchema, DataSourceCreate, DataSourceUpdate
from app.api.v1.deps import get_current_active_user
from app.services.file_upload import FileUploadService

router = APIRouter()
file_upload_service = FileUploadService()


@router.post("/", response_model=DataSourceSchema, status_code=status.HTTP_201_CREATED)
def create_datasource(
    datasource: DataSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new data source."""
    db_datasource = DataSource(
        **datasource.model_dump(),
        owner_id=current_user.id
    )
    db.add(db_datasource)
    db.commit()
    db.refresh(db_datasource)
    return db_datasource


@router.post("/upload", response_model=DataSourceSchema, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    name: str = None,
    description: str = None,
    clean_data: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a CSV or Excel file and create a data source."""
    # Process file upload
    result = await file_upload_service.process_upload(
        file=file,
        user_id=current_user.id,
        clean=clean_data
    )
    
    # Determine data source type based on file extension
    file_ext = Path(result["file_info"]["file_name"]).suffix.lower()
    if file_ext == ".csv":
        source_type = DataSourceType.FILE
    elif file_ext in [".xlsx", ".xls"]:
        source_type = DataSourceType.FILE
    else:
        source_type = DataSourceType.FILE
    
    # Create data source
    datasource_name = name or Path(result["file_info"]["file_name"]).stem
    db_datasource = DataSource(
        name=datasource_name,
        description=description or f"Uploaded file: {result['file_info']['file_name']}",
        type=source_type,
        file_path=result["file_info"]["file_path"],
        file_name=result["file_info"]["file_name"],
        file_size=result["file_info"]["file_size"],
        connection_config={
            "metadata": result["metadata"],
            "preview": result["preview"]
        },
        is_active=True,
        owner_id=current_user.id
    )
    db.add(db_datasource)
    db.commit()
    db.refresh(db_datasource)
    return db_datasource


@router.get("/", response_model=List[DataSourceSchema])
def read_datasources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all data sources for the current user."""
    datasources = db.query(DataSource).filter(
        DataSource.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return datasources


@router.get("/{datasource_id}", response_model=DataSourceSchema)
def read_datasource(
    datasource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific data source by ID."""
    datasource = db.query(DataSource).filter(
        DataSource.id == datasource_id,
        DataSource.owner_id == current_user.id
    ).first()
    if datasource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    return datasource


@router.put("/{datasource_id}", response_model=DataSourceSchema)
def update_datasource(
    datasource_id: int,
    datasource_update: DataSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a data source."""
    datasource = db.query(DataSource).filter(
        DataSource.id == datasource_id,
        DataSource.owner_id == current_user.id
    ).first()
    if datasource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    update_data = datasource_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(datasource, field, value)
    
    db.commit()
    db.refresh(datasource)
    return datasource


@router.delete("/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_datasource(
    datasource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a data source."""
    datasource = db.query(DataSource).filter(
        DataSource.id == datasource_id,
        DataSource.owner_id == current_user.id
    ).first()
    if datasource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    db.delete(datasource)
    db.commit()
    return None
