import asyncio

from datetime import datetime
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional, Tuple, Union

from websockets import (
    ConnectionClosed,
    ServerConnection
)

from .chatroom import Chatroom
from .websocket import WebSocketManager, WorkflowWebSocketManager
from config import settings
from core.database.models import (
    AppRuns,
    Apps,
    ChatroomAgentRelation,
    ChatroomMessages,
    Chatrooms,
    UploadFiles,
    Users
)
from core.mcp.client import MCPClient
from languages import get_language_content
from log import Logger


project_root = Path(__file__).parent.parent.parent
logger = Logger.get_logger('chatroom')

app_runs = AppRuns()
apps = Apps()
chatroom_agent_relation = ChatroomAgentRelation()
chatrooms = Chatrooms()
chatroom_messages = ChatroomMessages()
upload_files = UploadFiles()
users = Users()


class ChatroomManager:
    def __init__(self, event_loop: asyncio.BaseEventLoop):
        self._event_loop = event_loop
        self._ws_manager = WebSocketManager(event_loop)
        self._workflow_ws_manager = WorkflowWebSocketManager(
            event_loop,
            Chatroom.set_workflow_confirmation_status,
            Chatroom.set_mcp_tool_result
        )
        self._mcp_client = MCPClient()
        self._chatrooms: Dict[int, Chatroom] = {}
        self._ability_id_by_chatroom: Dict[int, int] = {}
        self._file_list_by_chatroom: Dict[int, List[Union[int, str]]] = {}
        self._is_desktop_by_chatroom: Dict[int, bool] = {}
        self._desktop_mcp_tool_list_by_chatroom: Dict[int, List[Dict[str, Any]]] = {}

    def _get_chatroom_info(self, chatroom_id: int, user_id: int, check_chat_status: bool) -> Dict[str, int]:
        chatroom_info = chatrooms.select_one(
            columns=[
                'id',
                'app_id',
                'is_temporary',
                'max_round',
                'initial_message_id',
                'chat_status',
                'smart_selection'
            ],
            conditions=[
                {'column': 'id', 'value': chatroom_id},
                {'column': 'status', 'value': 1}
            ]
        )
        assert chatroom_info, get_language_content('chatroom_does_not_exist', user_id)
        if check_chat_status:
            assert chatroom_info['chat_status'] == 0, 'You cannot start a new chat when the chat room is in a chat session!'
        return chatroom_info
    
    def _get_last_message_id(self, chatroom_id: int) -> Optional[int]:
        last_message = chatroom_messages.select_one(
            columns=['id'],
            conditions={'column': 'chatroom_id', 'value': chatroom_id},
            order_by='id DESC'
        )
        if not last_message:
            return None
        return last_message['id']
    
    def _get_user_message_info(self, chatroom_id: int) -> Tuple[int, str, Optional[str]]:
        user_message = chatroom_messages.select_one(
            columns=['id', 'message', 'topic'],
            conditions=[
                {'column': 'chatroom_id', 'value': chatroom_id},
                {'column': 'user_id', 'op': '!=', 'value': 0}
            ],
            order_by='id DESC'
        )
        assert user_message, 'Chatroom has not been started yet.'
        return user_message['id'], user_message['message'], user_message['topic']
    
    async def _start_chatroom(
        self,
        chatroom_info: Dict[str, int],
        user_id: int,
        team_id: int,
        user_input: Optional[str] = None
    ):
        chatroom_id = chatroom_info['id']
        app_id = chatroom_info['app_id']
        file_list = self._file_list_by_chatroom.pop(chatroom_id, None)
        
        start_time = time()
        if user_input is None:
            # Resume the chatroom
            app_run = app_runs.select_one(
                columns=['id'],
                conditions=[
                    {'column': 'user_id', 'value': user_id},
                    {'column': 'app_id', 'value': app_id},
                    {'column': 'chatroom_id', 'value': chatroom_id},
                    {'column': 'status', 'value': 2}
                ]
            )
            if app_run is None:
                chatrooms.update(
                    {'column': 'id', 'value': chatroom_id},
                    {'chat_status': 0}
                )
                return
            app_run_id = app_run['id']
            user_message_id, user_message, topic = self._get_user_message_info(chatroom_id)
        else:
            # Start a new chatroom
            file_info_list = []
            if file_list:
                for file_value in file_list:
                    if file_value:
                        if isinstance(file_value, int):
                            # Upload file ID
                            file_data = upload_files.get_file_by_id(file_value)
                            file_name = file_data['name'] + file_data['extension']
                            file_path_relative_to_upload_files = Path(file_data['path']).relative_to('upload_files')
                            file_url = f"{settings.STORAGE_URL}/upload/{file_path_relative_to_upload_files}"
                        elif isinstance(file_value, str):
                            if file_value[0] == '/':
                                file_value = file_value[1:]
                            file_path = project_root.joinpath('storage').joinpath(file_value)
                            file_name = file_path.name
                            file_url = f"{settings.STORAGE_URL}/storage/{file_value}"
                        else:
                            # This should never happen
                            raise Exception('Unsupported value type!')
                        file_info_list.append({
                            'name': file_name,
                            'url': file_url
                        })
            await self._ws_manager.send_instruction(chatroom_id, 'CHAT', user_input)
            await self._ws_manager.send_instruction(chatroom_id, 'WITHFILELIST', file_info_list)
            
            chatrooms.update(
                {'column': 'id', 'value': chatroom_id},
                {'chat_status': 1}
            )
            apps.increment_execution_times(app_id)
            start_datetime_str = datetime.fromtimestamp(start_time) \
                .replace(microsecond=0).isoformat(sep='_')
            app_run_id = app_runs.insert(
                {
                    'user_id':user_id,
                    'app_id': app_id,
                    'chatroom_id': chatroom_id,
                    'type': 2,
                    'name': f'Chatroom_Run_{chatroom_id}_{start_datetime_str}',
                    'status': 2
                }
            )
            user_message_id, user_message, topic = 0, user_input, None
        try:
            # Get related agents
            agent_relations = chatroom_agent_relation.select(
                columns=['agent_id'],
                conditions=[
                    {'column': 'chatroom_id', 'value': chatroom_id},
                    {'column': 'active', 'value': 1}
                ]
            )
            current_active_agent_ids = set(
                relation['agent_id']
                for relation in agent_relations
            )
            history_messages = chatroom_messages.select(
                columns=['agent_id', 'message', 'file_list', 'file_content_list', 'topic'],
                conditions=[
                    {'column': 'chatroom_id', 'value': chatroom_id},
                    {'column': 'id', 'op': '>', 'value': chatroom_info['initial_message_id']},
                    [
                        {'column': 'chatroom_messages.agent_id', 'op': '!=', 'value': 0, 'logic': 'or'},
                        {'column': 'chatroom_messages.user_id', 'op': '!=', 'value': 0}
                    ]
                ],
                order_by='id ASC'
            )
            if user_input is None and not history_messages:
                # Chat history has been cleared, then end the chat directly
                pass
            else:
                all_agent_ids_in_history = set()
                for message in history_messages:
                    if (agent_id := message['agent_id']) != 0:
                        all_agent_ids_in_history.add(agent_id)
                all_agent_ids = all_agent_ids_in_history.union(current_active_agent_ids)
                absent_agent_ids = all_agent_ids_in_history.difference(current_active_agent_ids)
                
                # Create chatroom
                chatroom = Chatroom(
                    user_id, team_id, chatroom_id, app_run_id, bool(chatroom_info['is_temporary']),
                    all_agent_ids, absent_agent_ids,
                    chatroom_info['max_round'], bool(chatroom_info['smart_selection']),
                    self._ws_manager, self._workflow_ws_manager,
                    user_message, user_message_id,
                    self._ability_id_by_chatroom.get(chatroom_id, 0),
                    topic,
                    self._mcp_client,
                    self._is_desktop_by_chatroom.get(chatroom_id, False),
                    self._desktop_mcp_tool_list_by_chatroom.get(chatroom_id)
                )
                self._chatrooms[chatroom_id] = chatroom
                self._workflow_ws_manager.add_chatroom(user_id, chatroom_id)
                chatroom.load_history_messages(history_messages)
                await chatroom.chat(user_input is None, file_list)
            end_time = time()
            app_runs.update(
                {'column': 'id', 'value': app_run_id},
                {
                    'status': 3,
                    'elapsed_time': end_time - start_time,
                    'finished_time': datetime.fromtimestamp(end_time)
                }
            )
        except Exception as e:
            end_time = time()
            app_runs.update(
                {'column': 'id', 'value': app_run_id},
                {
                    'status': 4,
                    'error': str(e),
                    'elapsed_time': end_time - start_time,
                    'finished_time': datetime.fromtimestamp(end_time)
                }
            )
            raise
        finally:
            await self._ws_manager.send_instruction(chatroom_id, 'ENDCHAT')
            chatrooms.update(
                {'column': 'id', 'value': chatroom_id},
                {'chat_status': 0}
            )
            self._chatrooms.pop(chatroom_id, None)
            self._workflow_ws_manager.remove_chatroom(user_id, chatroom_id)
        
    async def _handle_data_and_start_chatroom(
        self,
        chatroom_id: int,
        user_id: int,
        team_id: int,
        user_input: Optional[str] = None
    ) -> None:
        try:
            # Interrupt all MCP tool uses and wait for the chatroom to be terminated, when the chatroom is resumed
            if user_input is None and chatroom_id in self._chatrooms:
                chatroom = self._chatrooms[chatroom_id]
                if chatroom.mcp_tool_is_using:
                    await chatroom.interrupt_all_mcp_tool_uses()
                    while chatroom_id in self._chatrooms:
                        await asyncio.sleep(0.1)

            chatroom_info = self._get_chatroom_info(
                chatroom_id,
                user_id,
                check_chat_status = user_input is not None 
            )
            await self._start_chatroom(chatroom_info, user_id, team_id, user_input)
        except Exception as e:
            logger.exception('ERROR!!')
            await self._ws_manager.send_instruction(chatroom_id, 'ERROR', str(e))
        
    async def _ws_handler(self, connection: ServerConnection):
        try:
            user_id = self._ws_manager.verify_connection(connection.request.path)
        except Exception as e:
            logger.exception('ERROR!!')
            await connection.send(str(e))
            return
        user = users.get_user_by_id(user_id)
        if user is None:
            await self._ws_manager.send_instruction_by_connection(connection, 'ERROR', 'User not found.')
            return
        team_id = user['team_id']
        logger.info(f'User {user_id} connected.')
        chatroom_id = 0
        try:
            while True:
                instruction_str = await connection.recv()
                try:
                    cmd, data = self._ws_manager.parse_instruction(instruction_str)
                    logger.info(f'cmd: {cmd}, data: {str(data) if len(str(data)) < 500 else str(data)[:500] + "..."}')
                    match cmd:
                        case 'ENTER':
                            # Enter a chatroom
                            assert chatroom_id == 0, 'You should not ENTER twice.'
                            assert isinstance(data, int), 'Chatroom ID should be an integer.'
                            chatroom_info = self._get_chatroom_info(data, user_id, check_chat_status=False)  # Also check if the chatroom is available
                            chatroom_id = data
                            last_message_id = self._get_last_message_id(chatroom_id)
                            self._ws_manager.save_connection(chatroom_id, connection)
                            await self._ws_manager.send_instruction_by_connection(connection, 'OK')
                            if last_message_id and last_message_id > chatroom_info['initial_message_id']:
                                await self._ws_manager.send_instruction_by_connection(connection, 'TRUNCATABLE', True)
                        case 'TRUNCATE':
                            # Truncate chat history
                            assert isinstance(data, int), 'Chatroom ID should be an integer.'
                            chatroom_to_truncate = data
                            if not chatroom_to_truncate:
                                chatroom_to_truncate = chatroom_id
                            if not chatroom_to_truncate:
                                assert chatroom_id, 'You should ENTER the chatroom first.'
                            self._get_chatroom_info(chatroom_to_truncate, user_id, check_chat_status=True)  # Also check if the chatroom is available
                            last_message_id = self._get_last_message_id(chatroom_to_truncate)
                            if last_message_id:
                                chatrooms.update(
                                    {'column': 'id', 'value': chatroom_to_truncate},
                                    {'initial_message_id': last_message_id}
                                )
                            await self._ws_manager.send_instruction(chatroom_to_truncate, 'TRUNCATABLE', False)
                            if chatroom_to_truncate != chatroom_id:
                                await self._ws_manager.send_instruction_by_connection(connection, 'TRUNCATEOK', chatroom_to_truncate)
                        case _:
                            # Other commands
                            assert chatroom_id, 'You should ENTER the chatroom first.'
                            match cmd:
                                case 'SETABILITY':
                                    # Set ability ID
                                    assert isinstance(data, int), 'Ability ID should be an integer.'
                                    self._ability_id_by_chatroom[chatroom_id] = data
                                    await self._ws_manager.send_instruction_by_connection(connection, 'OK')
                                case 'FILELIST':
                                    # File list
                                    assert isinstance(data, list), 'File list should be a list.'
                                    self._file_list_by_chatroom[chatroom_id] = data
                                    await self._ws_manager.send_instruction_by_connection(connection, 'OK')
                                case 'ISDESKTOP':
                                    # Is desktop
                                    assert isinstance(data, bool), 'Is desktop should be a boolean.'
                                    self._is_desktop_by_chatroom[chatroom_id] = data
                                    await self._ws_manager.send_instruction_by_connection(connection, 'OK')
                                case 'MCPTOOLLIST':
                                    # MCP tool list
                                    assert isinstance(data, list), 'MCP tool list should be a list.'
                                    self._desktop_mcp_tool_list_by_chatroom[chatroom_id] = data
                                    await self._ws_manager.send_instruction_by_connection(connection, 'OK')
                                case 'MCPTOOLRESULT':
                                    assert isinstance(data, dict), 'MCP tool result should be a dictionary.'
                                    assert isinstance(mcp_tool_use_id := data['id'], str), f'Invalid MCP tool use ID: {mcp_tool_use_id}'
                                    assert isinstance(result := data['result'], str), f'Invalid MCP tool result: {result}'
                                    await self._chatrooms[chatroom_id].set_mcp_tool_result(mcp_tool_use_id, result)
                                case 'INPUT':
                                    # User input
                                    assert isinstance(data, str), 'User input should be a string.'
                                    user_input = data
                                    logger.info('Starting chatroom %s...', chatroom_id)
                                    coro = self._handle_data_and_start_chatroom(chatroom_id, user_id, team_id, user_input)
                                    self._event_loop.create_task(coro)
                                case 'STOP':
                                    # Stop the chatroom
                                    chatrooms.update(
                                        {'column': 'id', 'value': chatroom_id},
                                        {'chat_status': 0}
                                    )
                                    await self._ws_manager.send_instruction(chatroom_id, 'STOPPABLE', False)
                                case _:
                                    raise Exception(f'Unknown command: {cmd}')
                except Exception as e:
                    logger.exception('ERROR!!')
                    await self._ws_manager.send_instruction_by_connection(connection, 'ERROR', str(e))
        except ConnectionClosed:
            logger.info(f'User {user_id} disconnected.')
        finally:
            self._ws_manager.remove_connection(chatroom_id, connection)

    async def _resume_chatrooms(self):
        '''
        Resume chatrooms that are in a chat session.
        '''
        chatrooms_info = chatrooms.select(
            columns=['id', 'user_id'],
            conditions=[
                {'column': 'chat_status', 'value': 1},
                {'column': 'status', 'value': 1}
            ]
        )
        for chatroom_info in chatrooms_info:
            logger.info('Resuming chatroom %s...', chatroom_info['id'])
            user_id = chatroom_info['user_id']
            user = users.get_user_by_id(user_id)
            if user:
                team_id = user['team_id']
                coro = self._handle_data_and_start_chatroom(chatroom_info['id'], user_id, team_id)
                self._event_loop.create_task(coro)
        
    async def start(self):
        logger.info('Ready.')
        self._event_loop.create_task(self._resume_chatrooms())
        await self._ws_manager.start(self._ws_handler)

    def stop(self):
        logger.info('Exiting...')
        self._ws_manager.stop()
    