import asyncio
import json
from core.helper import pop_from_websocket_queue, get_websocket_queue_length
from core.websocket.websocket_manager import get_ws_handler
from log import Logger

logger = Logger.get_logger('websocket')

async def queue_processor():
    while True:

        item = pop_from_websocket_queue()
        if item:
            # logger.info(f"Get Redis Data: {json.dumps(item)}")

            ws_handler = get_ws_handler()

            await ws_handler.send_data_to_user(json.dumps(item), item['user_id'])
        else:
            await asyncio.sleep(1)