from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.core.database import get_db
from app.models.dashboard import Dashboard, DashboardShare, DashboardVersion, SharePermission
from app.models.widget import Widget
from app.models.user import User
from app.schemas.dashboard import (
    Dashboard as DashboardSchema,
    DashboardCreate,
    DashboardUpdate,
    DashboardShareCreate,
    DashboardShareUpdate,
    DashboardShare as DashboardShareSchema,
    DashboardVersionCreate,
    DashboardVersion as DashboardVersionSchema,
    LayoutUpdate
)
from app.api.v1.deps import get_current_active_user
from app.api.v1.utils import check_dashboard_access

router = APIRouter()


@router.post("/", response_model=DashboardSchema, status_code=status.HTTP_201_CREATED)
def create_dashboard(
    dashboard: DashboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new dashboard."""
    db_dashboard = Dashboard(
        **dashboard.model_dump(),
        owner_id=current_user.id,
        version=1
    )
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    
    # Create initial version
    _create_dashboard_version(db, db_dashboard, current_user.id, "Initial version")
    
    return db_dashboard


@router.get("/", response_model=List[DashboardSchema])
def read_dashboards(
    skip: int = 0,
    limit: int = 100,
    include_shared: bool = True,
    include_public: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all dashboards accessible to the current user."""
    query = db.query(Dashboard)
    
    # Build filter conditions
    conditions = [Dashboard.owner_id == current_user.id]
    
    if include_shared:
        # Get dashboards shared with user
        shared_dashboard_ids = db.query(DashboardShare.dashboard_id).filter(
            DashboardShare.user_id == current_user.id
        ).subquery()
        conditions.append(Dashboard.id.in_(db.query(shared_dashboard_ids)))
    
    if include_public:
        conditions.append(Dashboard.is_public == True)
    
    dashboards = query.filter(or_(*conditions)).offset(skip).limit(limit).all()
    return dashboards


@router.get("/{dashboard_id}", response_model=DashboardSchema)
def read_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific dashboard by ID."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check access
    if not check_dashboard_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return dashboard


@router.put("/{dashboard_id}", response_model=DashboardSchema)
def update_dashboard(
    dashboard_id: int,
    dashboard_update: DashboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check edit access
    if not check_dashboard_access(dashboard, current_user, require_edit=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this dashboard"
        )
    
    update_data = dashboard_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dashboard, field, value)
    
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Only owner can delete
    if dashboard.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this dashboard"
        )
    
    db.delete(dashboard)
    db.commit()
    return None


# Layout Management Endpoints
@router.put("/{dashboard_id}/layout", response_model=DashboardSchema)
def update_dashboard_layout(
    dashboard_id: int,
    layout_update: LayoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update dashboard layout configuration."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check edit access
    if not check_dashboard_access(dashboard, current_user, require_edit=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this dashboard"
        )
    
    dashboard.layout_config = layout_update.layout_config
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.get("/{dashboard_id}/layout")
def get_dashboard_layout(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard layout configuration."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check access
    if not check_dashboard_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return {
        "dashboard_id": dashboard.id,
        "layout_config": dashboard.layout_config or {}
    }


# Sharing Endpoints
@router.post("/{dashboard_id}/share", response_model=DashboardShareSchema, status_code=status.HTTP_201_CREATED)
def share_dashboard(
    dashboard_id: int,
    share_data: DashboardShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Share a dashboard with a user."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Only owner or admin can share
    if dashboard.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can share this dashboard"
        )
    
    # Check if user exists
    target_user = db.query(User).filter(User.id == share_data.user_id).first()
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already shared
    existing_share = db.query(DashboardShare).filter(
        and_(
            DashboardShare.dashboard_id == dashboard_id,
            DashboardShare.user_id == share_data.user_id
        )
    ).first()
    
    if existing_share:
        # Update existing share
        existing_share.permission = SharePermission(share_data.permission)
        db.commit()
        db.refresh(existing_share)
        return existing_share
    
    # Create new share
    share = DashboardShare(
        dashboard_id=dashboard_id,
        user_id=share_data.user_id,
        permission=SharePermission(share_data.permission),
        shared_by_id=current_user.id
    )
    db.add(share)
    dashboard.is_shared = True
    db.commit()
    db.refresh(share)
    return share


@router.get("/{dashboard_id}/shares", response_model=List[DashboardShareSchema])
def get_dashboard_shares(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all shares for a dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Only owner can view shares
    if dashboard.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can view shares"
        )
    
    shares = db.query(DashboardShare).filter(
        DashboardShare.dashboard_id == dashboard_id
    ).all()
    return shares


@router.put("/{dashboard_id}/share/{share_id}", response_model=DashboardShareSchema)
def update_dashboard_share(
    dashboard_id: int,
    share_id: int,
    share_update: DashboardShareUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a dashboard share permission."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Only owner can update shares
    if dashboard.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can update shares"
        )
    
    share = db.query(DashboardShare).filter(
        and_(
            DashboardShare.id == share_id,
            DashboardShare.dashboard_id == dashboard_id
        )
    ).first()
    
    if share is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    share.permission = SharePermission(share_update.permission)
    db.commit()
    db.refresh(share)
    return share


@router.delete("/{dashboard_id}/share/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
def unshare_dashboard(
    dashboard_id: int,
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a dashboard share."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Only owner can remove shares
    if dashboard.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can remove shares"
        )
    
    share = db.query(DashboardShare).filter(
        and_(
            DashboardShare.id == share_id,
            DashboardShare.dashboard_id == dashboard_id
        )
    ).first()
    
    if share is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    db.delete(share)
    
    # Check if there are any remaining shares
    remaining_shares = db.query(DashboardShare).filter(
        DashboardShare.dashboard_id == dashboard_id
    ).count()
    
    if remaining_shares == 0:
        dashboard.is_shared = False
    
    db.commit()
    return None


# Versioning Endpoints
def _create_dashboard_version(
    db: Session,
    dashboard: Dashboard,
    created_by_id: int,
    comment: Optional[str] = None
) -> DashboardVersion:
    """Helper function to create a dashboard version."""
    # Get current widgets
    widgets = db.query(Widget).filter(Widget.dashboard_id == dashboard.id).all()
    widgets_snapshot = [
        {
            "id": w.id,
            "name": w.name,
            "type": w.type.value,
            "description": w.description,
            "config": w.config,
            "query": w.query,
            "datasource_id": w.datasource_id,
            "position_x": w.position_x,
            "position_y": w.position_y,
            "width": w.width,
            "height": w.height
        }
        for w in widgets
    ]
    
    version = DashboardVersion(
        dashboard_id=dashboard.id,
        version_number=dashboard.version,
        name=dashboard.name,
        description=dashboard.description,
        layout_config=dashboard.layout_config,
        widgets_snapshot=widgets_snapshot,
        created_by_id=created_by_id,
        comment=comment
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    
    dashboard.current_version_id = version.id
    db.commit()
    
    return version


@router.post("/{dashboard_id}/versions", response_model=DashboardVersionSchema, status_code=status.HTTP_201_CREATED)
def create_dashboard_version(
    dashboard_id: int,
    version_data: DashboardVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new version of a dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check edit access
    if not check_dashboard_access(dashboard, current_user, require_edit=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create versions"
        )
    
    # Increment version number
    dashboard.version += 1
    
    # Create version
    version = _create_dashboard_version(
        db,
        dashboard,
        current_user.id,
        version_data.comment
    )
    
    return version


@router.get("/{dashboard_id}/versions", response_model=List[DashboardVersionSchema])
def get_dashboard_versions(
    dashboard_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all versions of a dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check access
    if not check_dashboard_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    versions = db.query(DashboardVersion).filter(
        DashboardVersion.dashboard_id == dashboard_id
    ).order_by(DashboardVersion.version_number.desc()).offset(skip).limit(limit).all()
    
    return versions


@router.get("/{dashboard_id}/versions/{version_id}", response_model=DashboardVersionSchema)
def get_dashboard_version(
    dashboard_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific dashboard version."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check access
    if not check_dashboard_access(dashboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    version = db.query(DashboardVersion).filter(
        and_(
            DashboardVersion.id == version_id,
            DashboardVersion.dashboard_id == dashboard_id
        )
    ).first()
    
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return version


@router.post("/{dashboard_id}/versions/{version_id}/restore", response_model=DashboardSchema)
def restore_dashboard_version(
    dashboard_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Restore a dashboard to a specific version."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check edit access
    if not check_dashboard_access(dashboard, current_user, require_edit=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to restore versions"
        )
    
    version = db.query(DashboardVersion).filter(
        and_(
            DashboardVersion.id == version_id,
            DashboardVersion.dashboard_id == dashboard_id
        )
    ).first()
    
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # Restore dashboard from version
    dashboard.name = version.name
    dashboard.description = version.description
    dashboard.layout_config = version.layout_config
    
    # Delete current widgets
    db.query(Widget).filter(Widget.dashboard_id == dashboard_id).delete()
    
    # Restore widgets from snapshot
    if version.widgets_snapshot:
        for widget_data in version.widgets_snapshot:
            widget = Widget(
                name=widget_data["name"],
                type=widget_data["type"],
                description=widget_data.get("description"),
                config=widget_data.get("config"),
                query=widget_data.get("query"),
                datasource_id=widget_data.get("datasource_id"),
                position_x=widget_data.get("position_x", 0),
                position_y=widget_data.get("position_y", 0),
                width=widget_data.get("width", 4),
                height=widget_data.get("height", 3),
                dashboard_id=dashboard_id
            )
            db.add(widget)
    
    # Create a new version for the restore action
    dashboard.version += 1
    _create_dashboard_version(db, dashboard, current_user.id, f"Restored from version {version.version_number}")
    
    db.commit()
    db.refresh(dashboard)
    return dashboard
