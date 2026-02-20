import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import create_application
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User

# Load all models so Base.metadata has all tables for create_all
import app.models  # noqa: F401


# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URI_TEST = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI_TEST,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create fresh tables and session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with overridden database."""
    app = create_application()
    app.dependency_overrides[get_db] = override_get_db
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
