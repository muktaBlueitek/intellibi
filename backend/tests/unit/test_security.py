"""Unit tests for app.core.security."""
import pytest
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    def test_get_password_hash_returns_hash(self):
        password = "secret123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt

    def test_verify_password_correct(self):
        password = "secret123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        hashed = get_password_hash("secret123")
        assert verify_password("wrong", hashed) is False

    def test_same_password_different_hashes(self):
        """Bcrypt uses salt, so same password yields different hashes."""
        h1 = get_password_hash("same")
        h2 = get_password_hash("same")
        assert h1 != h2
        assert verify_password("same", h1) and verify_password("same", h2)


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(data={"sub": "alice", "user_id": 1})
        assert isinstance(token, str)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "alice"
        assert payload.get("user_id") == 1
        assert "exp" in payload

    def test_decode_invalid_token_returns_none(self):
        assert decode_access_token("invalid.token.here") is None
        assert decode_access_token("") is None

    def test_create_token_with_expiry(self):
        token = create_access_token(
            data={"sub": "bob"},
            expires_delta=timedelta(minutes=5)
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "bob"
