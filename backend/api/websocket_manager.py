"""
WebSocket manager for real-time agent status updates.
Allows the frontend to see the agent working live.
"""

import json
import logging
from typing import Dict
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections per user."""

    def __init__(self):
        self.active_connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user={user_id}, total={len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections for a user."""
        if user_id not in self.active_connections:
            return
        dead = []
        for ws in self.active_connections[user_id]:
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"WebSocket send failed: {e}")
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, user_id)

    async def broadcast(self, message: dict):
        """Send to all connected users."""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)


ws_manager = WebSocketManager()
