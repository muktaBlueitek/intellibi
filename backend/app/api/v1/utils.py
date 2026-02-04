from app.models.dashboard import Dashboard, SharePermission
from app.models.user import User


def check_dashboard_access(
    dashboard: Dashboard,
    user: User,
    require_edit: bool = False,
    require_admin: bool = False
) -> bool:
    """Check if user has access to dashboard."""
    # Owner always has access
    if dashboard.owner_id == user.id:
        return True
    
    # Check public access
    if dashboard.is_public and not require_edit:
        return True
    
    # Check shared access
    share = dashboard.shares
    if share:
        for s in share:
            if s.user_id == user.id:
                if require_admin:
                    return s.permission == SharePermission.ADMIN
                elif require_edit:
                    return s.permission in [SharePermission.EDIT, SharePermission.ADMIN]
                return True
    
    return False


def check_dashboard_edit_access(dashboard: Dashboard, user: User) -> bool:
    """Check if user has edit access to dashboard."""
    if dashboard.owner_id == user.id:
        return True
    
    # Check shared access with edit permission
    for share in dashboard.shares:
        if share.user_id == user.id and share.permission in [SharePermission.EDIT, SharePermission.ADMIN]:
            return True
    
    return False
