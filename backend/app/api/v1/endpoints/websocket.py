from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

from app.core.websocket_manager import manager
from app.core.websocket_auth import get_user_from_websocket

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time updates."""
    user = await get_user_from_websocket(websocket)
    await manager.connect(websocket, user.id)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            {
                "type": "connected",
                "user_id": user.id,
                "username": user.username,
                "message": "Connected to IntelliBI real-time updates",
            },
            websocket
        )
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "subscribe_dashboard":
                dashboard_id = data.get("dashboard_id")
                if dashboard_id:
                    manager.subscribe_to_dashboard(websocket, dashboard_id)
                    await manager.send_personal_message(
                        {
                            "type": "subscribed",
                            "dashboard_id": dashboard_id,
                            "message": f"Subscribed to dashboard {dashboard_id}",
                        },
                        websocket
                    )
            
            elif message_type == "unsubscribe_dashboard":
                dashboard_id = data.get("dashboard_id")
                if dashboard_id:
                    manager.unsubscribe_from_dashboard(websocket, dashboard_id)
                    await manager.send_personal_message(
                        {
                            "type": "unsubscribed",
                            "dashboard_id": dashboard_id,
                            "message": f"Unsubscribed from dashboard {dashboard_id}",
                        },
                        websocket
                    )
            
            elif message_type == "subscribe_chat":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    manager.subscribe_to_chat(websocket, conversation_id)
                    await manager.send_personal_message(
                        {
                            "type": "subscribed",
                            "conversation_id": conversation_id,
                            "message": f"Subscribed to conversation {conversation_id}",
                        },
                        websocket
                    )
            
            elif message_type == "unsubscribe_chat":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    manager.unsubscribe_from_chat(websocket, conversation_id)
                    await manager.send_personal_message(
                        {
                            "type": "unsubscribed",
                            "conversation_id": conversation_id,
                            "message": f"Unsubscribed from conversation {conversation_id}",
                        },
                        websocket
                    )
            
            elif message_type == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": data.get("timestamp")},
                    websocket
                )
            
            else:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    },
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Helper functions to broadcast updates
async def broadcast_dashboard_update(dashboard_id: int, update_type: str, data: Dict[str, Any]):
    """Broadcast a dashboard update to all subscribed connections."""
    await manager.broadcast_to_dashboard(
        dashboard_id,
        {
            "type": "dashboard_update",
            "dashboard_id": dashboard_id,
            "update_type": update_type,
            "data": data,
            "timestamp": str(datetime.utcnow()),
        }
    )


async def broadcast_widget_update(dashboard_id: int, widget_id: int, data: Dict[str, Any]):
    """Broadcast a widget data update."""
    await broadcast_dashboard_update(
        dashboard_id,
        "widget_update",
        {
            "widget_id": widget_id,
            "widget_data": data,
        }
    )


async def broadcast_dashboard_layout_change(dashboard_id: int, layout: Dict[str, Any]):
    """Broadcast a dashboard layout change."""
    await broadcast_dashboard_update(
        dashboard_id,
        "layout_change",
        {"layout": layout}
    )


async def broadcast_collaborator_update(dashboard_id: int, user_id: int, action: str, username: str):
    """Broadcast a collaborator action (join/leave/edit)."""
    await broadcast_dashboard_update(
        dashboard_id,
        "collaborator_update",
        {
            "user_id": user_id,
            "username": username,
            "action": action,  # "joined", "left", "editing"
        }
    )


async def broadcast_chat_message(conversation_id: int, message: Dict[str, Any]):
    """Broadcast a new chat message."""
    await manager.broadcast_to_chat(
        conversation_id,
        {
            "type": "chat_message",
            "conversation_id": conversation_id,
            "message": message,
            "timestamp": str(datetime.utcnow()),
        }
    )


async def broadcast_user_message(conversation_id: int, user_id: int, content: str):
    """Broadcast a user message to chat subscribers."""
    await manager.broadcast_to_chat(
        conversation_id,
        {
            "type": "chat_message",
            "conversation_id": conversation_id,
            "message": {
                "role": "user",
                "content": content,
                "created_at": str(datetime.utcnow()),
            },
            "timestamp": str(datetime.utcnow()),
        }
    )


async def broadcast_notification(user_id: int, notification: Dict[str, Any]):
    """Send a notification to a specific user."""
    await manager.send_to_user(
        user_id,
        {
            "type": "notification",
            "notification": notification,
            "timestamp": str(datetime.utcnow()),
        }
    )
