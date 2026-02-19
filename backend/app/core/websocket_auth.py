from typing import Optional
from fastapi import WebSocket, WebSocketException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User


async def get_user_from_websocket(websocket: WebSocket) -> Optional[User]:
    """Authenticate WebSocket connection and return user."""
    # Get token from query parameters or headers
    token = None
    
    # Try query parameter first
    if "token" in websocket.query_params:
        token = websocket.query_params["token"]
    # Try Authorization header
    elif "authorization" in websocket.headers:
        auth_header = websocket.headers["authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication required"
        )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token"
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token payload"
        )
    
    # Get user from database
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None or not user.is_active:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="User not found or inactive"
            )
        return user
    finally:
        db.close()
