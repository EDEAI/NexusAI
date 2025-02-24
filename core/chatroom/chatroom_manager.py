import asyncio

from datetime import datetime
from time import time
from typing import Dict, Optional, Tuple

from websockets import (
    ConnectionClosed,
    WebSocketServerProtocol
)

from .chatroom import Chatroom
from .websocket import WebSocketManager
from core.database.models import (
    AppRuns,
    Apps,
    ChatroomAgentRelation,
    ChatroomMessages,
    Chatrooms,
    Users
)
from languages import get_language_content
from log import Logger


logger = Logger.get_logger('chatroom')

app_runs = AppRuns()
chatrooms = Chatrooms()
chatroom_messages = ChatroomMessages()
users = Users()


class ChatroomManager:
    def __init__(self, event_loop: asyncio.BaseEventLoop):
        self._event_loop = event_loop
        self._ws_manager = WebSocketManager(event_loop)
        
    def _get_chatroom_info(self, chatroom_id: int, user_id: int, check_chat_status: bool) -> Dict[str, int]:
        chatroom_info = chatrooms.select_one(
            columns=[
                'id',
                'app_id',
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
    
    def _get_user_message_id_and_topic(self, chatroom_id: int) -> Tuple[int, Optional[str]]:
        user_message = chatroom_messages.select_one(
            columns=['id', 'topic'],
            conditions=[
                {'column': 'chatroom_id', 'value': chatroom_id},
                {'column': 'user_id', 'op': '!=', 'value': 0}
            ],
            order_by='id DESC'
        )
        assert user_message, 'Chatroom has not been started yet.'
        return user_message['id'], user_message['topic']
    
    async def _start_chatroom(
        self,
        chatroom_info: Dict[str, int],
        user_id: int,
        team_id: int,
        user_input: Optional[str] = None
    ):
        chatroom_id = chatroom_info['id']
        app_id = chatroom_info['app_id']
        
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
            app_run_id = app_run['id']
            user_message_id, topic = self._get_user_message_id_and_topic(chatroom_id)
        else:
            # Start a new chatroom
            await self._ws_manager.send_instruction(chatroom_id, 'CHAT', user_input)
            
            chatrooms.update(
                {'column': 'id', 'value': chatroom_id},
                {'chat_status': 1}
            )
            Apps().increment_execution_times(app_id)
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
            user_message_id, topic = 0, None
        try:
            # Get related agents
            agent_relations = ChatroomAgentRelation().select(
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
                columns=['agent_id', 'message', 'topic'],
                conditions=[
                    {'column': 'chatroom_id', 'value': chatroom_id},
                    {'column': 'id', 'op': '>', 'value': chatroom_info['initial_message_id']},
                    [
                        {'column': 'chatroom_messages.agent_id', 'op': '!=', 'value': 0, 'logic': 'or'},
                        {'column': 'chatroom_messages.user_id', 'op': '!=', 'value': 0}
                    ]
                ]
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
                    user_id, team_id, chatroom_id, app_run_id,
                    all_agent_ids, absent_agent_ids,
                    chatroom_info['max_round'], bool(chatroom_info['smart_selection']),
                    self._ws_manager, user_message_id, topic
                )
                chatroom.load_history_messages(history_messages)
                await chatroom.chat(user_input)
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
            logger.exception('ERROR!!')
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
        
    async def _handle_data_and_start_chatroom(self, chatroom_id: int, user_id: int, team_id: int, user_input: Optional[str] = None) -> None:
        try:
            chatroom_info = self._get_chatroom_info(
                chatroom_id,
                user_id,
                check_chat_status = user_input is not None 
            )
            await self._start_chatroom(chatroom_info, user_id, team_id, user_input)
        except Exception as e:
            logger.exception('ERROR!!')
            await self._ws_manager.send_instruction(chatroom_id, 'ERROR', str(e))
        
    async def _ws_handler(self, connection: WebSocketServerProtocol):
        try:
            user_id = self._ws_manager.verify_connection(connection.path)
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
                    logger.info(f'cmd: {cmd}, data: {data}')
                    match cmd:
                        case 'ENTER':
                            # Enter a chatroom
                            assert chatroom_id == 0, 'You should not ENTER twice.'
                            assert isinstance(data, int), 'Chatroom ID should be an integer.'
                            chatroom_info = self._get_chatroom_info(data, user_id, check_chat_status=False)  # Also check if the chatroom is available
                            chatroom_id = data
                            last_message_id = self._get_last_message_id(chatroom_id)
                            self._ws_manager.save_connection(chatroom_id, connection)
                            if last_message_id and last_message_id > chatroom_info['initial_message_id']:
                                await self._ws_manager.send_instruction(chatroom_id, 'TRUNCATABLE', True)
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
                            assert chatroom_id, get_language_content('chatroom_does_not_exist', user_id)
                            match cmd:
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
    