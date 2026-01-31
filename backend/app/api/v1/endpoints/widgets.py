from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.widget import Widget
from app.models.dashboard import Dashboard
from app.models.user import User
from app.schemas.widget import Widget as WidgetSchema, WidgetCreate, WidgetUpdate
from app.api.v1.deps import get_current_active_user

router = APIRouter()


@router.post("/", response_model=WidgetSchema, status_code=status.HTTP_201_CREATED)
def create_widget(
    widget: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new widget."""
    # Verify dashboard belongs to user
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == widget.dashboard_id,
        Dashboard.owner_id == current_user.id
    ).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    db_widget = Widget(**widget.model_dump())
    db.add(db_widget)
    db.commit()
    db.refresh(db_widget)
    return db_widget


@router.get("/dashboard/{dashboard_id}", response_model=List[WidgetSchema])
def read_widgets_by_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all widgets for a specific dashboard."""
    # Verify dashboard belongs to user
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.owner_id == current_user.id
    ).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    widgets = db.query(Widget).filter(Widget.dashboard_id == dashboard_id).all()
    return widgets


@router.get("/{widget_id}", response_model=WidgetSchema)
def read_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific widget by ID."""
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found"
        )
    
    # Verify dashboard belongs to user
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == widget.dashboard_id,
        Dashboard.owner_id == current_user.id
    ).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return widget


@router.put("/{widget_id}", response_model=WidgetSchema)
def update_widget(
    widget_id: int,
    widget_update: WidgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a widget."""
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found"
        )
    
    # Verify dashboard belongs to user
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == widget.dashboard_id,
        Dashboard.owner_id == current_user.id
    ).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = widget_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(widget, field, value)
    
    db.commit()
    db.refresh(widget)
    return widget


@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a widget."""
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found"
        )
    
    # Verify dashboard belongs to user
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == widget.dashboard_id,
        Dashboard.owner_id == current_user.id
    ).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(widget)
    db.commit()
    return None
