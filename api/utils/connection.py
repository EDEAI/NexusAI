from fastapi import WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Connect the websocket.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect the websocket.
        """
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send a personal message to the websocket.
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Broadcast a message to all websockets.
        """
        for connection in self.active_connections:
            await connection.send_text(message)