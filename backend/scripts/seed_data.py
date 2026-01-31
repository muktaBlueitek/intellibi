"""
Seed data script for IntelliBI database.
Run this script to populate the database with initial data.
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.datasource import DataSource, DataSourceType
from app.models.dashboard import Dashboard
from app.models.widget import Widget, WidgetType
from app.core.security import get_password_hash


def create_seed_data(db: Session):
    """Create seed data for development."""
    
    # Create admin user
    admin_user = db.query(User).filter(User.email == "admin@intellibi.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@intellibi.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Created admin user: {admin_user.email}")
    
    # Create regular user
    regular_user = db.query(User).filter(User.email == "user@intellibi.com").first()
    if not regular_user:
        regular_user = User(
            email="user@intellibi.com",
            username="user",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            is_active=True,
            is_superuser=False,
            role=UserRole.USER
        )
        db.add(regular_user)
        db.commit()
        db.refresh(regular_user)
        print(f"Created regular user: {regular_user.email}")
    
    # Create sample data source
    sample_datasource = db.query(DataSource).filter(DataSource.name == "Sample CSV Data").first()
    if not sample_datasource:
        sample_datasource = DataSource(
            name="Sample CSV Data",
            description="Sample CSV data source for testing",
            type=DataSourceType.FILE,
            file_name="sample_data.csv",
            is_active=True,
            owner_id=admin_user.id
        )
        db.add(sample_datasource)
        db.commit()
        db.refresh(sample_datasource)
        print(f"Created sample data source: {sample_datasource.name}")
    
    # Create sample dashboard
    sample_dashboard = db.query(Dashboard).filter(Dashboard.name == "Sample Dashboard").first()
    if not sample_dashboard:
        sample_dashboard = Dashboard(
            name="Sample Dashboard",
            description="A sample dashboard for demonstration",
            layout_config={"grid": {"columns": 12, "rows": 6}},
            is_public=False,
            is_shared=False,
            owner_id=admin_user.id
        )
        db.add(sample_dashboard)
        db.commit()
        db.refresh(sample_dashboard)
        print(f"Created sample dashboard: {sample_dashboard.name}")
        
        # Create sample widget
        sample_widget = Widget(
            name="Sample Chart",
            type=WidgetType.LINE_CHART,
            description="A sample line chart widget",
            config={"xAxis": "date", "yAxis": "value"},
            position_x=0,
            position_y=0,
            width=6,
            height=3,
            dashboard_id=sample_dashboard.id,
            datasource_id=sample_datasource.id
        )
        db.add(sample_widget)
        db.commit()
        print(f"Created sample widget: {sample_widget.name}")
    
    print("\nSeed data creation completed!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_seed_data(db)
    except Exception as e:
        print(f"Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()
