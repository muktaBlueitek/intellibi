from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.widget import Widget
from app.models.dashboard import Dashboard, SharePermission
from app.models.user import User
from app.schemas.widget import Widget as WidgetSchema, WidgetCreate, WidgetUpdate
from app.api.v1.deps import get_current_active_user
from app.api.v1.utils import check_dashboard_access, check_dashboard_edit_access

router = APIRouter()


class WidgetReorderRequest(BaseModel):
    widget_id: int
    position_x: int
    position_y: int


class WidgetBulkUpdateRequest(BaseModel):
    widget_ids: List[int]
    updates: Dict[str, Any]


class WidgetBulkDeleteRequest(BaseModel):
    widget_ids: List[int]


@router.post("/", response_model=WidgetSchema, status_code=status.HTTP_201_CREATED)
def create_widget(
    widget: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new widget."""
    # Verify dashboard exists and user has edit access
    dashboard = db.query(Dashboard).filter(Dashboard.id == widget.dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    if not check_dashboard_edit_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create widgets"
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
    # Verify dashboard exists and user has access
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check access (view access is enough)
    if not check_dashboard_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    widgets = db.query(Widget).filter(Widget.dashboard_id == dashboard_id).order_by(
        Widget.position_y, Widget.position_x
    ).all()
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
    
    # Verify dashboard exists and user has access
    dashboard = db.query(Dashboard).filter(Dashboard.id == widget.dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    if not check_dashboard_access(dashboard, current_user):
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
    
    # Verify dashboard exists and user has edit access
    dashboard = db.query(Dashboard).filter(Dashboard.id == widget.dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    if not check_dashboard_edit_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit widgets"
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
    
    # Verify dashboard exists and user has edit access
    dashboard = db.query(Dashboard).filter(Dashboard.id == widget.dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    if not check_dashboard_edit_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete widgets"
        )
    
    db.delete(widget)
    db.commit()
    return None


# Bulk Operations
@router.post("/bulk/reorder", status_code=status.HTTP_200_OK)
def reorder_widgets(
    reorder_requests: List[WidgetReorderRequest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reorder multiple widgets at once."""
    updated_widgets = []
    
    for req in reorder_requests:
        widget = db.query(Widget).filter(Widget.id == req.widget_id).first()
        if widget is None:
            continue
        
        # Verify dashboard exists and user has edit access
        dashboard = db.query(Dashboard).filter(Dashboard.id == widget.dashboard_id).first()
        if dashboard is None or not _check_dashboard_edit_access(dashboard, current_user):
            continue
        
        widget.position_x = req.position_x
        widget.position_y = req.position_y
        updated_widgets.append(widget)
    
    db.commit()
    
    return {
        "success": True,
        "updated_count": len(updated_widgets),
        "widgets": [WidgetSchema.model_validate(w) for w in updated_widgets]
    }


@router.put("/bulk/update", status_code=status.HTTP_200_OK)
def bulk_update_widgets(
    bulk_update: WidgetBulkUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bulk update multiple widgets."""
    updated_widgets = []
    
    widgets = db.query(Widget).filter(Widget.id.in_(bulk_update.widget_ids)).all()
    
    for widget in widgets:
        # Verify dashboard exists and user has edit access
        dashboard = db.query(Dashboard).filter(Dashboard.id == widget.dashboard_id).first()
        if dashboard is None or not _check_dashboard_edit_access(dashboard, current_user):
            continue
        
        # Apply updates
        for field, value in bulk_update.updates.items():
            if hasattr(widget, field):
                setattr(widget, field, value)
        
        updated_widgets.append(widget)
    
    db.commit()
    
    return {
        "success": True,
        "updated_count": len(updated_widgets),
        "widgets": [WidgetSchema.model_validate(w) for w in updated_widgets]
    }


@router.post("/bulk/delete", status_code=status.HTTP_200_OK)
def bulk_delete_widgets(
    bulk_delete: WidgetBulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bulk delete multiple widgets."""
    deleted_count = 0
    
    widgets = db.query(Widget).filter(Widget.id.in_(bulk_delete.widget_ids)).all()
    
    for widget in widgets:
        # Verify dashboard exists and user has edit access
        dashboard = db.query(Dashboard).filter(Dashboard.id == widget.dashboard_id).first()
        if dashboard is None or not _check_dashboard_edit_access(dashboard, current_user):
            continue
        
        db.delete(widget)
        deleted_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "deleted_count": deleted_count
    }
