import asyncio
import json
import re

from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union

from jose import JWTError, jwt
from websockets import WebSocketServerProtocol, broadcast, serve

from config import settings
from core.database import redis
from log import Logger


logger = Logger.get_logger('chatroom')

INSTRUCTION_TEMPLATE = '--NEXUSAI-INSTRUCTION-{instruction}--'

SECRET_KEY = settings.ACCESS_TOKEN_SECRET_KEY
ALGORITHM = 'HS256'

connection_path_pattern = re.compile(r'/\?token=([A-Za-z0-9\.\-_]+)')
connection_path_pattern_docker = re.compile(r'/ws_chat\?token=([A-Za-z0-9\.\-_]+)')

class WebSocketManager:
    def __init__(self, event_loop: asyncio.BaseEventLoop):
        self._stop_future = event_loop.create_future()
        self._connections_by_chatroom_id: Dict[int, Set[WebSocketServerProtocol]] = {}
        self._replying_status_by_connection_id: Dict[int, bool] = {}
        
    async def start(self, callback: Callable[[WebSocketServerProtocol], Awaitable[Any]]):
        async with serve(callback, '0.0.0.0', settings.CHATROOM_WEBSOCKET_PORT):
            await self._stop_future  # run forever
    
    def verify_connection(self, connection_path: str) -> int:
        match_result = (
            connection_path_pattern.fullmatch(connection_path) or
            connection_path_pattern_docker.fullmatch(connection_path)
        )
        assert match_result, 'Invalid connection path'
        token = match_result.group(1)
        assert redis.sismember('blacklisted_tokens', token) == 0, 'Blacklisted token'
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        except JWTError:
            raise Exception('Invalid token')
        assert (user_id := payload.get('uid')), 'Invalid user ID'
        return user_id
            
    def parse_instruction(self, instruction_str: str) -> Tuple[str, Optional[Union[int, str, bool]]]:
        try:
            cmd, data = json.loads(instruction_str)
            return cmd, data
        except:
            logger.error('Invalid instruction: %s', instruction_str)
            raise ValueError(f'Invalid instruction: {instruction_str}')
    
    def save_connection(self, chatroom_id: int, connection: WebSocketServerProtocol):
        connections = self._connections_by_chatroom_id.setdefault(chatroom_id, set())
        connections.add(connection)
        logger.debug(f'Connection {id(connection)} saved for chatroom {chatroom_id}')
        self._replying_status_by_connection_id[id(connection)] = False
        
    def remove_connection(self, chatroom_id: int, connection: WebSocketServerProtocol):
        if connections := self._connections_by_chatroom_id.get(chatroom_id):
            connections.discard(connection)
            logger.debug(f'Connection {id(connection)} removed from chatroom {chatroom_id}')
            del self._replying_status_by_connection_id[id(connection)]
            if not connections:
                del self._connections_by_chatroom_id[chatroom_id]
    
    def has_connections(self, chatroom_id: int) -> bool:
        return bool(self._connections_by_chatroom_id.get(chatroom_id))
            
    async def send_instruction_by_connection(
        self,
        connection: WebSocketServerProtocol,
        cmd: str,
        data: Optional[Union[int, str, bool]] = None
    ):
        instruction = json.dumps([cmd, data])
        await connection.send(INSTRUCTION_TEMPLATE.format(instruction=instruction))
        
    async def send_instruction_by_connections(
        self,
        connections: Iterable[WebSocketServerProtocol],
        cmd: str,
        data: Optional[Union[int, str, bool]] = None
    ):
        instruction = json.dumps([cmd, data])
        broadcast(connections, INSTRUCTION_TEMPLATE.format(instruction=instruction))
            
    async def send_instruction(self, chatroom_id: int, cmd: str, data: Optional[Union[int, str, bool]] = None):
        if connections := self._connections_by_chatroom_id.get(chatroom_id):
            await self.send_instruction_by_connections(connections, cmd, data)
            
    async def send_agent_reply(
        self,
        chatroom_id: int,
        agent_id: int,
        current_message_chunk: str,
        full_message: str
    ):
        '''
        Send the agent reply to the chatroom.
        '''
        if connections := self._connections_by_chatroom_id.get(chatroom_id):
            replying_connections = set()
            not_replying_connections = set()
            
            for connection in connections:
                if self._replying_status_by_connection_id[id(connection)]:
                    replying_connections.add(connection)
                else:
                    not_replying_connections.add(connection)
                    self._replying_status_by_connection_id[id(connection)] = True
            
            broadcast(replying_connections, current_message_chunk)
            await self.send_instruction_by_connections(not_replying_connections, 'REPLY', agent_id)
            broadcast(not_replying_connections, full_message)
        
    async def end_agent_reply(
        self,
        chatroom_id: int,
        agent_id: int,
        full_message: str
    ):
        '''
        End the agent reply to the chatroom.
        '''
        if connections := self._connections_by_chatroom_id.get(chatroom_id):
            not_replying_connections = set()
            
            for connection in connections:
                if self._replying_status_by_connection_id[id(connection)]:
                    self._replying_status_by_connection_id[id(connection)] = False
                else:
                    not_replying_connections.add(connection)
            
            await self.send_instruction_by_connections(not_replying_connections, 'REPLY', agent_id)
            broadcast(not_replying_connections, full_message)
            
    def stop(self):
        self._stop_future.set_result(None)
    