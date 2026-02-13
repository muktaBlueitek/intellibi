"""
Quick script to create or verify test users exist.
Run this to ensure test users are available.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password


def create_or_verify_users(db: Session):
    """Create test users if they don't exist."""
    
    # Admin user
    admin_user = db.query(User).filter(User.username == "admin").first()
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
        print("✓ Created admin user")
    else:
        # Verify password works
        if verify_password("admin123", admin_user.hashed_password):
            print("✓ Admin user exists and password is correct")
        else:
            # Update password
            admin_user.hashed_password = get_password_hash("admin123")
            print("✓ Updated admin user password")
    
    # Regular user
    regular_user = db.query(User).filter(User.username == "user").first()
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
        print("✓ Created regular user")
    else:
        # Verify password works
        if verify_password("user123", regular_user.hashed_password):
            print("✓ Regular user exists and password is correct")
        else:
            # Update password
            regular_user.hashed_password = get_password_hash("user123")
            print("✓ Updated regular user password")
    
    db.commit()
    print("\n✅ Test users ready!")
    print("\nLogin credentials:")
    print("  Admin:  username=admin, password=admin123")
    print("  User:   username=user, password=user123")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_or_verify_users(db)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
