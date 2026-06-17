"""Collaboration endpoints — real-time multi-user editing via WebSocket."""

import uuid
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.core.deps import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for collaborative editing."""

    def __init__(self):
        # project_id -> list of (websocket, user_id) tuples
        self.active_connections: dict[uuid.UUID, list[tuple[WebSocket, str]]] = {}

    async def connect(self, websocket: WebSocket, project_id: uuid.UUID, user_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append((websocket, user_id))
        await self.broadcast(
            project_id,
            {"type": "user_joined", "user_id": user_id},
            exclude_user=user_id,
        )

    def disconnect(self, websocket: WebSocket, project_id: uuid.UUID, user_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id] = [
                (ws, uid) for ws, uid in self.active_connections[project_id]
                if ws != websocket
            ]
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def broadcast(self, project_id: uuid.UUID, message: dict, exclude_user: str | None = None):
        if project_id not in self.active_connections:
            return
        data = json.dumps(message)
        for ws, uid in self.active_connections[project_id]:
            if uid != exclude_user:
                try:
                    await ws.send_text(data)
                except Exception:
                    logger.warning("Failed to send to user %s in project %s", uid, project_id)

    async def send_user_count(self, project_id: uuid.UUID):
        if project_id in self.active_connections:
            count = len(self.active_connections[project_id])
            await self.broadcast(project_id, {"type": "user_count", "count": count})


manager = ConnectionManager()


@router.websocket("/ws/{project_id}")
async def collaboration_websocket(websocket: WebSocket, project_id: uuid.UUID, token: str = ""):
    """WebSocket endpoint for real-time collaboration on a project."""
    payload = verify_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload.get("sub", "anonymous")
    await manager.connect(websocket, project_id, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "cursor_move":
                await manager.broadcast(project_id, {
                    "type": "cursor_move",
                    "user_id": user_id,
                    "position": message.get("position"),
                }, exclude_user=user_id)

            elif msg_type == "element_update":
                await manager.broadcast(project_id, {
                    "type": "element_update",
                    "user_id": user_id,
                    "element_id": message.get("element_id"),
                    "changes": message.get("changes"),
                }, exclude_user=user_id)

            elif msg_type == "viewport_change":
                await manager.broadcast(project_id, {
                    "type": "viewport_change",
                    "user_id": user_id,
                    "viewport": message.get("viewport"),
                }, exclude_user=user_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id, user_id)
        await manager.broadcast(project_id, {"type": "user_left", "user_id": user_id})
        await manager.send_user_count(project_id)
