import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from core.websocket.websocket_manager import websocket_router
from core.websocket.websocket_queue_pop import queue_processor

app = FastAPI(
    title="NexusAI WebSocket Server",
    description="WebSocket server for handling real-time connections.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket_router())

def start_queue_processor():
    asyncio.create_task(queue_processor())

app.add_event_handler("startup", start_queue_processor)

if __name__ == "__main__":
    uvicorn.run("websocket:app", host="0.0.0.0", port=settings.WEBSOCKET_PORT, workers=settings.FASTAPI_WORKERS, ws_ping_timeout=1)
