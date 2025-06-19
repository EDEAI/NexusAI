import asyncio
import json
import re

from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Set, Tuple, TYPE_CHECKING, Union

from jose import JWTError, jwt
from websockets import (
    ConnectionClosed,
    WebSocketClientProtocol, WebSocketServerProtocol,
    broadcast, connect, serve
)

from config import settings
from core.database import redis
from log import Logger


if TYPE_CHECKING:
    from .chatroom import Chatroom

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
        assert match_result, f'Invalid connection path: {connection_path}'
        token = match_result.group(1)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        except JWTError:
            raise Exception('Invalid token')
        assert (user_id := payload.get('uid')), 'Invalid user ID'

        stored_token = (
            redis.get(f'third_party_access_token:{user_id}')
            if payload.get('openid')
            else redis.get(f'access_token:{user_id}')
        )
        if not stored_token or stored_token.decode('utf-8') != token:
            raise Exception('Invalid token')
        return user_id
            
    def parse_instruction(self, instruction_str: str) -> Tuple[str, Optional[Union[int, str, bool, List[Union[int, str]]]]]:
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
        data: Any = None
    ):
        instruction = json.dumps([cmd, data], ensure_ascii=False)
        await connection.send(INSTRUCTION_TEMPLATE.format(instruction=instruction))
        
    async def send_instruction_by_connections(
        self,
        connections: Iterable[WebSocketServerProtocol],
        cmd: str,
        data: Any = None
    ):
        instruction = json.dumps([cmd, data], ensure_ascii=False)
        broadcast(connections, INSTRUCTION_TEMPLATE.format(instruction=instruction))
            
    async def send_instruction(self, chatroom_id: int, cmd: str, data: Any = None):
        if connections := self._connections_by_chatroom_id.get(chatroom_id):
            await self.send_instruction_by_connections(connections, cmd, data)
            
    async def send_agent_reply(
        self,
        chatroom_id: int,
        agent_id: int,
        ability_id: int,
        current_message_chunk: str,
        full_message: str,
        new_text: bool
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
            
            if current_message_chunk:
                if new_text:
                    await self.send_instruction_by_connections(replying_connections, 'TEXT')
                broadcast(replying_connections, current_message_chunk)

            await self.send_instruction_by_connections(not_replying_connections, 'REPLY', agent_id)
            await self.send_instruction_by_connections(not_replying_connections, 'ABILITY', ability_id)
            if full_message:
                await self.send_instruction_by_connections(not_replying_connections, 'TEXT')
                broadcast(not_replying_connections, full_message)
        
    async def end_agent_reply(
        self,
        chatroom_id: int,
    ):
        '''
        End the agent reply to the chatroom.
        '''
        if connections := self._connections_by_chatroom_id.get(chatroom_id):
            for connection in connections:
                if self._replying_status_by_connection_id[id(connection)]:
                    self._replying_status_by_connection_id[id(connection)] = False
            
    def stop(self):
        self._stop_future.set_result(None)
    

class WorkflowWebSocketManager():
    DEBUG_MSG = 'workflow_run_debug'
    CONFIRMATION_MSG = 'workflow_need_human_confirm'
    WAITING_FOR_CONFIRMATION_MSG = 'workflow_waiting_for_confirm'
    
    def __init__(
        self,
        event_loop: asyncio.BaseEventLoop,
        set_workflow_confirmation_status_cb: Callable[['Chatroom', int, Dict[str, Any]], Awaitable[None]],
        set_workflow_result_cb: Callable[['Chatroom', int, str], Awaitable[None]]
    ):
        self._event_loop = event_loop
        self._set_workflow_confirmation_status_cb = set_workflow_confirmation_status_cb
        self._set_workflow_result_cb = set_workflow_result_cb
        self._connection_by_user_id: Dict[int, WebSocketClientProtocol] = {}
        self._chatrooms_by_user_id: Dict[int, Set[int]] = {}
        # {user_id: {workflow_run_id: (Chatroom, mcp_tool_index)}}
        self._workflow_runs_by_user_id: Dict[int, Dict[int, Tuple['Chatroom', int]]] = {} 

    async def _start_connection(self, user_id: int):
        token = (
            redis.get(f'access_token:{user_id}')
            or redis.get(f'third_party_access_token:{user_id}')
        )
        if not token:
            raise Exception('Invalid token')
        token = token.decode('utf-8')
        connection = await connect(f'ws://localhost:{settings.WEBSOCKET_PORT}/ws?token={token}')
        self._connection_by_user_id[user_id] = connection
        logger.info(f'User {user_id} connected to Workflow WebSocket.')
        while True:
            try:
                message = await connection.recv()
                message = json.loads(message)
                message_type = message['type']
                try:
                    workflow_run_id = message['data']['app_run_id']
                except (KeyError, TypeError):
                    workflow_run_id = 0
                if (
                    workflow_runs := self._workflow_runs_by_user_id.get(user_id)
                    and workflow_run_id in workflow_runs
                ):
                    message_data = message['data']
                    chatroom, mcp_tool_index = workflow_runs[workflow_run_id]
                    if message_type == self.CONFIRMATION_MSG:
                        logger.info(f'User {user_id} received workflow message: {message}')
                        status = {
                            'id': message_data['workflow_id'],
                            'status': 'waiting_confirm',
                            'app_run_id': message_data['app_run_id'],
                            'node_exec_id': message_data['node_exec_data']['node_exec_id'],
                            'workflow_name': message_data['app_name'],
                            'need_user_confirm': False,
                            'show_todo_button': True
                        }
                        await self._set_workflow_confirmation_status_cb(chatroom, mcp_tool_index, status)
                    elif message_type == self.WAITING_FOR_CONFIRMATION_MSG:
                        logger.info(f'User {user_id} received workflow message: {message}')
                        user_names = [user['nickname'] for user in message_data['waiting_users']]
                        status = {
                            'id': message_data['workflow_id'],
                            'status': 'waiting_confirm',
                            'app_run_id': message_data['app_run_id'],
                            'node_exec_id': message_data['node_exec_data']['node_exec_id'],
                            'workflow_name': message_data['app_name'],
                            'need_user_confirm': True,
                            'show_todo_button': False,
                            'confirmer_name': f'[{", ".join(user_names)}]'
                        }
                        await self._set_workflow_confirmation_status_cb(chatroom, mcp_tool_index, status)
                    elif message_type == self.DEBUG_MSG:
                        if message_data['node_exec_data']['node_type'] == 'end':
                            logger.info(f'User {user_id} received workflow message: {message}')
                            try:
                                result = message_data['node_exec_data'].get('outputs', {})
                                await self._set_workflow_result_cb(
                                    chatroom, mcp_tool_index,
                                    json.dumps(result, ensure_ascii=False)
                                )
                            except:
                                self.remove_workflow_run(user_id, workflow_run_id)
                                raise
                # Else ignore the message
            except ConnectionClosed:
                logger.info(f'Connection closed for user {user_id}.')
                break
            except:
                logger.exception('ERROR!!!')
    
    def add_chatroom(self, user_id: int, chatroom_id: int):
        if user_id not in self._connection_by_user_id:
            self._event_loop.create_task(self._start_connection(user_id))
        self._chatrooms_by_user_id.setdefault(user_id, set()).add(chatroom_id)
    
    async def remove_chatroom(self, user_id: int, chatroom_id: int):
        if user_id in self._chatrooms_by_user_id:
            self._chatrooms_by_user_id[user_id].discard(chatroom_id)
            if not self._chatrooms_by_user_id[user_id]:
                del self._chatrooms_by_user_id[user_id]
        if (
            user_id not in self._chatrooms_by_user_id
            and (connection := self._connection_by_user_id.pop(user_id, None))
        ):
            await connection.close()

    def add_workflow_run(self, user_id: int, workflow_run_id: int, chatroom: 'Chatroom', mcp_tool_index: int):
        assert user_id in self._connection_by_user_id, f'No Websocket connection for user {user_id}'
        assert user_id in self._chatrooms_by_user_id, f'No chatroom for user {user_id}'
        self._workflow_runs_by_user_id.setdefault(user_id, {})[workflow_run_id] = (chatroom, mcp_tool_index)
    
    def remove_workflow_run(self, user_id: int, workflow_run_id: int):
        assert user_id in self._connection_by_user_id, f'No Websocket connection for user {user_id}'
        assert user_id in self._chatrooms_by_user_id, f'No chatroom for user {user_id}'
        if user_id in self._workflow_runs_by_user_id:
            self._workflow_runs_by_user_id[user_id].pop(workflow_run_id, None)
            if not self._workflow_runs_by_user_id[user_id]:
                del self._workflow_runs_by_user_id[user_id]
