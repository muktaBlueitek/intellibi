"""Integration tests for health endpoint."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture
def client_no_db():
    """Client without DB override for health check (no DB needed)."""
    app = create_application()
    with TestClient(app) as c:
        yield c


def test_health_check_returns_ok(client_no_db: TestClient):
    response = client_no_db.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert data["service"] == "IntelliBI"
    assert "environment" in data


def test_root_returns_app_info(client_no_db: TestClient):
    response = client_no_db.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "IntelliBI Backend"
    assert "environment" in data
