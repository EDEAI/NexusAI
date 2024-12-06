from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional, Set
from api.utils.jwt import *
from log import Logger

logger = Logger.get_logger('websocket')

class ConnectionManager():
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.user_team: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, team_id: Optional[int] = None):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        # print(f"User {user_id} connected.")
        logger.info('User %s connected.', user_id)

        if team_id:
            if team_id not in self.user_team:
                self.user_team[team_id] = set()
            self.user_team[team_id].add(user_id)
            # print(f"User {user_id} joined team {team_id}.")
            logger.info('User %s joined team %s.', user_id, team_id)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            for team_users in self.user_team.values():
                team_users.discard(user_id)

    async def send_personal_message(self, message: str, user_id: int):
        connections = self.active_connections.get(user_id, set())
        if user_id in self.active_connections:
            logger.info('User %s online.', user_id)
        else:
            logger.info('User %s offline.', user_id)
        for websocket in connections:
            await websocket.send_text(message)
            # print(f"Message sent to user {user_id} on connection {websocket}: {message}")
            logger.info('Message sent to user %s on connection %s: %s.', user_id, websocket, message)

    async def broadcast_to_team(self, message: str, team_id: int):
        user_ids = self.user_team.get(team_id, set())
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)


class WebSocketHandler:
    def __init__(self):
        self.manager = ConnectionManager()

    async def handle_websocket(self, websocket: WebSocket, user_id: int, team_id: Optional[int] = None):
        await self.manager.connect(websocket, user_id, team_id)
        try:
            while True:
                data = await websocket.receive_json()
                # Optional: Do something with the data received from client
        except WebSocketDisconnect:
            self.manager.disconnect(websocket, user_id)

    async def send_data_to_user(self, message: str, user_id: int):
        await self.manager.send_personal_message(message, user_id)

    async def send_data_to_team(self, message: str, team_id: int):
        await self.manager.broadcast_to_team(message, team_id)


ws_handler = WebSocketHandler()

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, userinfo: TokenData = Depends(get_ws_current_user)):
    user_id = userinfo.uid
    team_id = userinfo.team_id
    # print('user_id', user_id)
    # print('team_id', team_id)
    await ws_handler.handle_websocket(websocket, user_id, team_id)


def websocket_router():
    return router


def get_ws_handler():
    return ws_handler
