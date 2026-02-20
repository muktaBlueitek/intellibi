"""Integration tests for auth endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "hashed_password" not in data
    assert data["is_active"] is True


def test_register_duplicate_username(client: TestClient, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "other@example.com",
            "username": test_user.username,
            "password": "pass123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client: TestClient, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.username, "password": "testpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.username, "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "pass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
