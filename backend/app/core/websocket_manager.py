from typing import Dict, Set, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio
from datetime import datetime

from app.models.user import User


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""

    def __init__(self):
        # Map of user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Map of dashboard_id -> Set of WebSocket connections
        self.dashboard_connections: Dict[int, Set[WebSocket]] = {}
        # Map of conversation_id -> Set of WebSocket connections
        self.chat_connections: Dict[int, Set[WebSocket]] = {}
        # Map of WebSocket -> user_id for quick lookup
        self.connection_users: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        self.connection_users[websocket] = user_id

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        user_id = self.connection_users.get(websocket)
        if user_id:
            # Remove from user connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from dashboard connections
            for dashboard_id, connections in list(self.dashboard_connections.items()):
                connections.discard(websocket)
                if not connections:
                    del self.dashboard_connections[dashboard_id]
            
            # Remove from chat connections
            for conversation_id, connections in list(self.chat_connections.items()):
                connections.discard(websocket)
                if not connections:
                    del self.chat_connections[conversation_id]
            
            del self.connection_users[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def send_to_user(self, user_id: int, message: dict):
        """Send a message to all connections of a specific user."""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.disconnect(ws)

    async def broadcast_to_dashboard(self, dashboard_id: int, message: dict):
        """Broadcast a message to all connections watching a dashboard."""
        if dashboard_id in self.dashboard_connections:
            disconnected = set()
            for websocket in self.dashboard_connections[dashboard_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.disconnect(ws)

    async def broadcast_to_chat(self, conversation_id: int, message: dict):
        """Broadcast a message to all connections in a conversation."""
        if conversation_id in self.chat_connections:
            disconnected = set()
            for websocket in self.chat_connections[conversation_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.disconnect(ws)

    def subscribe_to_dashboard(self, websocket: WebSocket, dashboard_id: int):
        """Subscribe a connection to dashboard updates."""
        if dashboard_id not in self.dashboard_connections:
            self.dashboard_connections[dashboard_id] = set()
        self.dashboard_connections[dashboard_id].add(websocket)

    def unsubscribe_from_dashboard(self, websocket: WebSocket, dashboard_id: int):
        """Unsubscribe a connection from dashboard updates."""
        if dashboard_id in self.dashboard_connections:
            self.dashboard_connections[dashboard_id].discard(websocket)
            if not self.dashboard_connections[dashboard_id]:
                del self.dashboard_connections[dashboard_id]

    def subscribe_to_chat(self, websocket: WebSocket, conversation_id: int):
        """Subscribe a connection to chat updates."""
        if conversation_id not in self.chat_connections:
            self.chat_connections[conversation_id] = set()
        self.chat_connections[conversation_id].add(websocket)

    def unsubscribe_from_chat(self, websocket: WebSocket, conversation_id: int):
        """Unsubscribe a connection from chat updates."""
        if conversation_id in self.chat_connections:
            self.chat_connections[conversation_id].discard(websocket)
            if not self.chat_connections[conversation_id]:
                del self.chat_connections[conversation_id]

    def get_user_id(self, websocket: WebSocket) -> Optional[int]:
        """Get the user ID associated with a WebSocket connection."""
        return self.connection_users.get(websocket)

    def get_dashboard_subscribers(self, dashboard_id: int) -> List[int]:
        """Get list of user IDs subscribed to a dashboard."""
        if dashboard_id not in self.dashboard_connections:
            return []
        user_ids = []
        for ws in self.dashboard_connections[dashboard_id]:
            user_id = self.connection_users.get(ws)
            if user_id:
                user_ids.append(user_id)
        return user_ids


# Global connection manager instance
manager = ConnectionManager()
