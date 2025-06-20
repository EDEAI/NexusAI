import json
import sys
import asyncio
import re

from collections import deque
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

from langchain_core.messages import AIMessageChunk

from .websocket import WebSocketManager, WorkflowWebSocketManager
from core.database.models import (
    AgentAbilities,
    Agents,
    AppRuns,
    Apps,
    ChatroomMessages,
    Chatrooms,
    CustomTools,
    Datasets,
    Models,
    Workflows
)
from core.helper import truncate_messages_by_token_limit, get_file_content_list
from core.llm import Prompt
from core.mcp.app_executor import skill_run, workflow_run
from core.mcp.client import MCPClient
from core.workflow.context import Context
from core.workflow.nodes import AgentNode, LLMNode
from core.workflow.variables import create_variable_from_dict, ObjectVariable
from languages import get_language_content
from log import Logger

project_root = Path(__file__).parent.parent.parent
logger = Logger.get_logger('chatroom')

agent_abilities = AgentAbilities()
agents = Agents()
app_runs = AppRuns()
apps = Apps()
chatrooms = Chatrooms()
chatroom_messages = ChatroomMessages()
custom_tools = CustomTools()
datasets = Datasets()
models = Models()
workflows = Workflows()

skill_pattern = re.compile(r'nexusai__skill-(\d+)')
workflow_pattern = re.compile(r'nexusai__workflow-(\d+)')

class Chatroom:
    @staticmethod
    def _console_log(content: Any) -> None:
        sys.stdout.write(f'\n{str(content)}\n' if not isinstance(content, str) else content)
        sys.stdout.flush()

    def _get_model_configs(self, all_agent_ids: Sequence[int], absent_agent_ids: Sequence[int]) -> None:
        model_info = models.get_model_by_type(1, self._team_id, uid=self._user_id)
        model_config_id = model_info['model_config_id']
        self._model_config_ids[0] = model_config_id
        model_info = models.get_model_by_config_id(model_config_id)
        assert model_info, f'Model configuration {model_config_id} not found.'
        self._model_configs[model_config_id] = model_info
        for agent_id in all_agent_ids:
            agent = agents.select_one(
                columns=['id', 'app_id', 'apps.name', 'apps.description', 'obligations', 'model_config_id'],
                joins=[('left', 'apps', 'agents.app_id = apps.id')],
                conditions={'column': 'id', 'value': agent_id}  # Include deleted agents (with status=3)
            )
            assert agent, f'Agent {agent_id} does not exist!'
            abilities = agent_abilities.get_abilities_by_agent_id(agent_id)
            agent['abilities'] = abilities

            self._all_agents[agent_id] = agent
            if agent_id not in absent_agent_ids:
                model_config_id = agent['model_config_id']
                self._model_config_ids[agent_id] = model_config_id
                model_info = models.get_model_by_config_id(model_config_id)
                assert model_info, f'Model configuration {model_config_id} not found.'
                self._model_configs[model_config_id] = model_info
    
    def __init__(
        self,
        user_id: int,
        team_id: int,
        chatroom_id: int,
        app_run_id: int,
        is_temporary: bool,
        all_agent_ids: Sequence[int],
        absent_agent_ids: Sequence[int],
        max_round: int,
        smart_selection: bool,
        ws_manager: WebSocketManager,
        workflow_ws_manager: WorkflowWebSocketManager,
        user_message: str,
        user_message_id: int = 0,
        ability_id: int = 0,
        topic: Optional[str] = None,
        mcp_client: MCPClient = None,
        is_desktop: bool = False,
        desktop_mcp_tool_list: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        self._user_id = user_id
        self._team_id = team_id
        self._chatroom_id = chatroom_id
        self._app_run_id = app_run_id
        self._is_temporary = is_temporary
        self._all_agents = {}
        # self._model_config_ids: dict
        # keys are IDs of all active agents with the addition of 0 (which is the Speaker Selector)
        # values are corresponding LLM model_config_ids
        self._model_config_ids: Dict[int, int] = {}
        self._model_configs: Dict[int, Dict[str, Any]] = {}
        self._get_model_configs(all_agent_ids, absent_agent_ids)
        self._max_round = max_round
        self._smart_selection = smart_selection
        self._ws_manager = ws_manager
        self._workflow_ws_manager = workflow_ws_manager
        self._user_message = user_message
        self._user_message_id = user_message_id
        self._ability_id = ability_id
        self._topic = topic
        # self._history_messages: list
        # each item is a dict with the following keys:
        # - agent_id: int, 0 means user, > 0 means agent
        # - message: str
        # - topic: str
        self._history_messages: List[Dict[str, Union[int, str]]] = []
        self._image_list: Optional[List[Union[int, str]]] = None
        self._current_round = 0
        self._current_agent_message_id = 0
        self._current_agent_message = ''
        self._last_speaker_id = 0
        self._mcp_client = mcp_client
        self._is_desktop = is_desktop
        self._desktop_mcp_tool_list = desktop_mcp_tool_list
        self._mcp_tool_is_using = False
        self._mcp_tool_use_is_interrupted = False
        self._mcp_tool_use_lock = asyncio.Event()
        self._mcp_tool_uses: List[Dict[str, Any]] = []

    def _get_agents_info(self) -> str:
        '''
        Get information of all active agents as a JSON string in an AI prompt.
        '''
        info = []
        for agent_id in self._model_config_ids:
            if agent_id != 0 and agent_id != self._last_speaker_id:
                agent = self._all_agents[agent_id]
                abilities = agent['abilities']
                if abilities:
                    abilities_content = json.dumps([ability['content'] for ability in abilities], ensure_ascii=False)
                    description: str = get_language_content(
                        'chatroom_agent_description_with_abilities',
                        self._user_id,
                        append_ret_lang_prompt=False
                    )
                    description = description.format(
                        obligations=agent['obligations'],
                        abilities_content=abilities_content
                    )
                else:
                    description: str = get_language_content(
                        'chatroom_agent_description_with_no_ability',
                        self._user_id,
                        append_ret_lang_prompt=False
                    )
                    description = description.format(obligations=agent['obligations'])
                info.append(
                    {
                        'id': agent_id,
                        'name': agent['name'],
                        'description': description
                    }
                )
        return json.dumps(info, ensure_ascii=False)
        
    def _get_history_messages_list(self, model_config_id: int) -> Tuple[
        List[Dict[str, Union[int, str]]],
        List[Dict[str, Union[int, str]]],
        List[str],
    ]:
        '''
        Get all history messages and the last section of them as JSON strings in an AI prompt.
        '''
        messages = []
        for message in self._history_messages:
            user_str = get_language_content('chatroom_role_user', self._user_id, append_ret_lang_prompt=False)
            agent_str = get_language_content('chatroom_role_agent', self._user_id, append_ret_lang_prompt=False)
            agent_id = message['agent_id']
            message_for_llm = {
                'id': agent_id,
                'name': user_str if agent_id == 0 else self._all_agents[agent_id]['name'],
                'role': user_str if agent_id == 0 else agent_str,
                'type': message['type'],
                'message': message['message']
            }
            # if (topic := message['topic']) is not None:
            #     message_for_llm['topic'] = topic
            messages.append(message_for_llm)
        messages = truncate_messages_by_token_limit(messages, self._model_configs[model_config_id])
        messages_in_last_section = deque()
        for message in reversed(messages):
            messages_in_last_section.appendleft(message)
            if message['id'] == 0 and message['type'] == 'text':
                break
        user_messages = []
        for message in messages:
            if message['id'] == 0 and message['type'] == 'text':
                user_messages.append(message['message'])
        return (
            messages,
            list(messages_in_last_section),
            user_messages
        )
    
    def _get_history_messages_list_grouped(self, model_config_id: int) -> Tuple[
        List[List[Dict[str, Union[int, str]]]],
        List[Dict[str, Union[int, str]]],
        List[str],
    ]:
        '''
        Get all history messages (grouped by sections) and the last section of them as JSON strings in an AI prompt.
        Each section starts with a user message and includes all subsequent agent messages until the next user message.
        
        Returns:
            Tuple containing:
            - List of message sections, where each section is a list of message dictionaries
            - List of messages in the last section (from the last user message)
            - List of all user messages
        '''
        # Process individual messages as in the original function
        messages = []
        for message in self._history_messages:
            user_str = get_language_content('chatroom_role_user', self._user_id, append_ret_lang_prompt=False)
            agent_str = get_language_content('chatroom_role_agent', self._user_id, append_ret_lang_prompt=False)
            agent_id = message['agent_id']
            message_for_llm = {
                'id': agent_id,
                'name': user_str if agent_id == 0 else self._all_agents[agent_id]['name'],
                'role': user_str if agent_id == 0 else agent_str,
                'type': message['type'],
                'message': message['message']
            }
            messages.append(message_for_llm)
        
        # Truncate messages based on token limit
        messages = truncate_messages_by_token_limit(messages, self._model_configs[model_config_id])
        
        # Group messages into sections
        message_sections = []
        current_section = []
        for message in messages:
            if message['id'] == 0 and message['type'] == 'text' and current_section:  # When encountering a user message and current section is not empty
                message_sections.append(current_section)
                current_section = []
            current_section.append(message)
        if current_section:  # Add the last section
            message_sections.append(current_section)
                
        # Get all user messages
        user_messages = []
        for message in messages:
            if message['id'] == 0 and message['type'] == 'text':
                user_messages.append(message['message'])
                
        return (
            message_sections,
            message_sections[-1],
            user_messages
        )
    
    def _user_speak(self, user_message: str, file_list: Optional[List[Union[int, str]]] = None) -> None:
        '''
        Append a user message to the history messages and insert it into the database.
        '''
        self._console_log(f'User message: \033[91m{user_message}\033[0m\n')
        # self._history_messages.append({'agent_id': 0, 'message': user_message, 'topic': self._topic})
        self._last_speaker_id = 0
        file_content_list = None
        if file_list:
            file_content_list = get_file_content_list(file_list)
            if file_content_list:
                self._image_list = []
                for file_var_value in file_list:
                    if isinstance(file_var_value, int):
                        attr = 'id'
                        value = file_var_value
                    elif isinstance(file_var_value, str):
                        attr = 'path'
                        if file_var_value[0] == '/':
                            value = file_var_value[1:]
                        file_path = project_root.joinpath('storage').joinpath(value)
                        value = str(file_path)
                    else:
                        raise Exception('Unsupported value type!')
                    for file_content in file_content_list:
                        if file_content[attr] == value and file_content['type'] == 'image':
                            self._image_list.append(file_var_value)
        self._user_message_id = chatroom_messages.insert(
            {
                'chatroom_id': self._chatroom_id,
                'app_run_id': self._app_run_id,
                'user_id': self._user_id,
                'message': user_message,
                'file_list': file_list,
                'file_content_list': file_content_list,
                'is_read': 1 if self._ws_manager.has_connections(self._chatroom_id) else 0
            }
        )
        chatrooms.update(
            {'column': 'id', 'value': self._chatroom_id},
            {'last_chat_time': datetime.now()}
        )
        self._history_messages.append({
            'agent_id': 0,
            'type': 'text',
            'message': user_message,
            'file_list': file_list,
            'file_content_list': file_content_list
        })
        self._add_file_content_to_message(self._history_messages[-1], 'document_only')
        app_runs.increment_steps(self._app_run_id)

    async def _select_next_speaker(self) -> int:
        agent_id = None
        last_speaker_id = self._history_messages[-1]['agent_id']

        for i in range(5):  # Try 5 times
            if last_speaker_id == 0:
                # If there is only one agent in the chatroom, handle directly
                if len(self._model_config_ids) <= 2:  # Including Speaker Selector (id=0) and one agent
                    # Set user message as topic directly
                    self._topic = self._user_message
                    logger.debug('Current topic: %s', self._topic)
                    chatroom_messages.update(
                        {'column': 'id', 'value': self._user_message_id},
                        {'topic': self._topic}
                    )
                    # Return the ID of the only agent
                    for agent_id in self._model_config_ids:
                        if agent_id != 0:
                            return agent_id
                    return 0
                # If the last speaker is the user, the Speaker Selector must choose an agent
                else:
                    schema_key = "chatroom_manager_system"
                    system_prompt = get_language_content(
                        'chatroom_manager_system',
                        self._user_id
                    )
                    user_prompt = get_language_content(
                        'chatroom_manager_user',
                        self._user_id,
                        append_ret_lang_prompt=False
                    )
            else:
                # If the last speaker is an agent,
                if self._smart_selection or len(self._model_config_ids) <= 2:
                    # and (smart selection is enabled or there is only one agent), the Speaker Selector must stop the chat
                    return 0
                else:
                    # and smart selection is disabled, the Speaker Selector will choose an agent, or stop the chat
                    schema_key = "chatroom_manager_system_with_optional_selection"
                    system_prompt = get_language_content(
                        'chatroom_manager_system_with_optional_selection',
                        self._user_id
                    )
                    user_prompt = get_language_content(
                        'chatroom_manager_user_with_optional_selection',
                        self._user_id,
                        append_ret_lang_prompt=False
                    )
            messages, messages_in_last_section, user_messages = self._get_history_messages_list_grouped(self._model_config_ids[0])
            user_prompt = user_prompt.format(
                agent_count = len(self._model_config_ids) - 1,
                agents = self._get_agents_info(),
                user_message = messages_in_last_section[0]['message'],
                topic = self._topic,
                messages = json.dumps(messages, ensure_ascii=False),
                messages_in_last_section = json.dumps(messages_in_last_section, ensure_ascii=False),
                user_messages = user_messages
            )
            if i > 0:
                # the Speaker Selector has tried more than once
                user_prompt = get_language_content(
                    'chatroom_manager_user_invalid_selection',
                    self._user_id,
                    append_ret_lang_prompt=False
                ).format(
                    agent_id=agent_id
                ) + user_prompt

            # Request LLM
            logger.debug('Requesting LLM...')
            llm_node = LLMNode(
                title='Speaker Selector',
                desc='Speaker Selector',
                model_config_id=self._model_config_ids[0],
                prompt=Prompt(system_prompt, user_prompt)
            )
            llm_node.schema_key = schema_key
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    llm_node.run,
                    return_json=True,
                    override_file_list=self._image_list if self._current_round == 0 else None
                ),
                timeout=120
            )
            assert result['status'] == 'success', result['message']
            result_data = result['data']
            manager_message = result_data['outputs']['value']
            logger.debug('Speaker selector output: %s', manager_message)
            model_data = result_data['model_data']
            llm_input_var = model_data['messages']
            llm_input = []
            for role, message_var in llm_input_var:
                if message_var['type'].startswith('array'):
                    message_values = []
                    for message_value in message_var['values']:
                        message_values.append(message_value['value'])
                    llm_input.append([role, message_values])
                else:
                    llm_input.append([role, message_var['value']])
            has_connections = self._ws_manager.has_connections(self._chatroom_id)
            prompt_tokens = result_data['prompt_tokens']
            completion_tokens = result_data['completion_tokens']
            total_tokens = result_data['total_tokens']
            chatroom_messages.insert(
                {
                    'chatroom_id': self._chatroom_id,
                    'app_run_id': self._app_run_id,
                    'llm_input': llm_input,
                    'message': manager_message,
                    'message_type': 1,
                    'model_data': model_data,
                    'is_read': 1 if has_connections else 0,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens
                }
            )
            app_runs.increment_token_usage(
                self._app_run_id,
                prompt_tokens, completion_tokens, total_tokens
            )

            llm_output = json.loads(manager_message)
            # Update the topic if the last speaker is the user
            if last_speaker_id == 0:
                # self._topic = llm_output['topic']
                self._topic = llm_output['summary']
                logger.debug('Current topic: %s', self._topic)
                # self._history_messages[-1]['topic'] = self._topic
                chatroom_messages.update(
                    {'column': 'id', 'value': self._user_message_id},
                    {'topic': self._topic}
                )
            # Get the agent ID from the Speaker Selector's output
            agent_id = llm_output['id']
            try:
                agent_id = int(agent_id)
            except ValueError:
                # The Speaker Selector returned an invalid agent ID, try again
                continue
            if agent_id in self._model_config_ids:
                return agent_id
            # else: the Speaker Selector returned an invalid agent ID, try again

        # If the Speaker Selector has tried 5 times and still returned an invalid agent ID, stop the chat
        return 0
    
    @property
    def mcp_tool_is_using(self) -> bool:
        return self._mcp_tool_is_using
    
    def _get_agent_message_with_mcp_tool_uses(self, agent_message: str) -> str:
        for mcp_tool_use in self._mcp_tool_uses:
            mcp_tool_str = json.dumps({
                'name': mcp_tool_use['name'],
                'skill_or_workflow_name': mcp_tool_use['skill_or_workflow_name'],
                'workflow_run_id': mcp_tool_use['workflow_run_id'],
                'workflow_confirmation_status': mcp_tool_use['workflow_confirmation_status'],
                'args': mcp_tool_use['args'],
                'result': mcp_tool_use['result']
            }, ensure_ascii=False)
            agent_message += (
                '<<<mcp-tool-start>>>'
                f'{mcp_tool_str}'
                '<<<mcp-tool-end>>>'
            )
        return agent_message

    def _create_chatroom_message(self, agent_id: int) -> int:
        chatroom_message_id = chatroom_messages.insert(
            {
                'chatroom_id': self._chatroom_id,
                'app_run_id': self._app_run_id,
                'agent_id': agent_id,
                'ability_id': self._ability_id,
                'message': '',
                'topic': self._topic,
                'is_read': 1 if self._ws_manager.has_connections(self._chatroom_id) else 0
            }
        )
        chatrooms.update(
            {'column': 'id', 'value': self._chatroom_id},
            {'last_chat_time': datetime.now()}
        )
        return chatroom_message_id
    
    def _update_chatroom_message(self, chatroom_message_id: int, message: str) -> None:
        chatroom_messages.update(
            {'column': 'id', 'value': chatroom_message_id},
            {'message': message}
        )
        chatrooms.update(
            {'column': 'id', 'value': self._chatroom_id},
            {'last_chat_time': datetime.now()}
        )
    
    def _update_chatroom_message_and_token_usage(
        self, chatroom_message_id: int, message: str,
        prompt_tokens: int, completion_tokens: int, total_tokens: int
    ) -> None:
        chatroom_messages.update(
            {'column': 'id', 'value': chatroom_message_id},
            {
                'message': message,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            }
        )
        chatrooms.update(
            {'column': 'id', 'value': self._chatroom_id},
            {'last_chat_time': datetime.now()}
        )
    
    async def set_mcp_tool_result(self, index: int, result: str) -> None:
        if not self._mcp_tool_is_using:
            raise Exception('There is no MCP tool use!')
        if index >= len(self._mcp_tool_uses):
            raise Exception('Invalid MCP tool use index!')
        if self._mcp_tool_uses[index]['result'] is not None:
            raise Exception('MCP tool use has finished!')
        self._console_log(f'MCP tool result: \033[91m{result}\033[0m\n')
        mcp_tool_use = self._mcp_tool_uses[index]
        mcp_tool_use['result'] = result
        if workflow_pattern.fullmatch(mcp_tool_use['name']):
            mcp_tool_use['workflow_confirmation_status'] = None
        self._update_chatroom_message(
            self._current_agent_message_id,
            self._get_agent_message_with_mcp_tool_uses(self._current_agent_message)
        )
        await self._ws_manager.send_instruction(
            self._chatroom_id,
            'WITHMCPTOOLRESULT', 
            {'index': index, 'result': result}
        )
        if workflow_run_id := mcp_tool_use['workflow_run_id']:
            self._workflow_ws_manager.remove_workflow_run(self._user_id, workflow_run_id)
        self._mcp_tool_use_lock.set()

    async def set_workflow_confirmation_status(self, index: int, status: Dict[str, Any]) -> None:
        if not self._mcp_tool_is_using:
            raise Exception('There is no MCP tool use!')
        if index >= len(self._mcp_tool_uses):
            raise Exception('Invalid MCP tool use index!')
        self._console_log(f'Workflow comfirmation status: \033[91m{status}\033[0m\n')
        self._mcp_tool_uses[index]['workflow_confirmation_status'] = status
        self._update_chatroom_message(
            self._current_agent_message_id,
            self._get_agent_message_with_mcp_tool_uses(self._current_agent_message)
        )
        await self._ws_manager.send_instruction(
            self._chatroom_id,
            'WITHWFCONFIRM', 
            {'index': index, 'status': status}
        )

    async def _stop_all_mcp_tool_uses(self, result: str) -> None:
        self._mcp_tool_use_is_interrupted = True
        for index, mcp_tool_use in enumerate(self._mcp_tool_uses):
            if mcp_tool_use['result'] is None:
                # Set the result of all unfinished MCP tool uses
                mcp_tool_name = mcp_tool_use['name']
                skill_match = skill_pattern.fullmatch(mcp_tool_name)
                workflow_match = workflow_pattern.fullmatch(mcp_tool_name)
                if skill_match or workflow_match:
                    result = json.dumps({
                        'status': 'failed',
                        'message': f'Error executing tool {mcp_tool_name}: {result}'
                    }, ensure_ascii=False)
                mcp_tool_use['result'] = result
                self._update_chatroom_message(
                    self._current_agent_message_id,
                    self._get_agent_message_with_mcp_tool_uses(self._current_agent_message)
                )
                await self._ws_manager.send_instruction(
                    self._chatroom_id,
                    'WITHMCPTOOLRESULT',
                    {'index': index, 'result': result}
                )
                if workflow_run_id := mcp_tool_use['workflow_run_id']:
                    self._workflow_ws_manager.remove_workflow_run(self._user_id, workflow_run_id)
        self._mcp_tool_use_lock.set()

    async def interrupt_all_mcp_tool_uses(self) -> None:
        if not self._mcp_tool_is_using:
            raise Exception('There is no MCP tool use!')
        await self._stop_all_mcp_tool_uses('Interrupted')

    async def _start_mcp_tool_uses(self) -> None:
        # Send the MCP tool use instructions to the frontend
        for index, mcp_tool_use in enumerate(self._mcp_tool_uses):
            mcp_tool_use['args'] = json.loads(mcp_tool_use['args'])
            if match := skill_pattern.fullmatch(mcp_tool_use['name']):
                skill = custom_tools.get_skill_by_id(int(match.group(1)))
                if not skill:
                    mcp_tool_use['result'] = 'Skill not found'
                else:
                    app = apps.get_app_by_id(skill['app_id'])
                    mcp_tool_use['skill_or_workflow_name'] = app['name']
            elif match := workflow_pattern.fullmatch(mcp_tool_use['name']):
                workflow = workflows.get_workflow_app(int(match.group(1)))
                if not workflow:
                    mcp_tool_use['result'] = 'Workflow not found'
                else:
                    mcp_tool_use['skill_or_workflow_name'] = workflow['name']
            self._update_chatroom_message(
                self._current_agent_message_id,
                self._get_agent_message_with_mcp_tool_uses(self._current_agent_message)
            )
            mcp_tool_use_in_message = {
                'index': index,
                'name': mcp_tool_use['name'],
                'skill_or_workflow_name': mcp_tool_use['skill_or_workflow_name'],
                'args': mcp_tool_use['args']
            }
            await self._ws_manager.send_instruction(
                self._chatroom_id,
                'MCPTOOLUSE',
                mcp_tool_use_in_message
            )

    async def _wait_for_mcp_tool_uses(self) -> None:
        # Invoke the MCP tool(s) of the built-in MCP server
        for index, mcp_tool_use in enumerate(self._mcp_tool_uses):
            mcp_tool_name = mcp_tool_use['name']
            mcp_tool_args = mcp_tool_use['args']
            skill_match = skill_pattern.fullmatch(mcp_tool_name)
            workflow_match = workflow_pattern.fullmatch(mcp_tool_name)
            if skill_match or workflow_match:
                if result := mcp_tool_use['result'] is None:
                    try:
                        logger.debug('Invoking MCP tool: %s', mcp_tool_name)
                        logger.debug('MCP tool args: %s', mcp_tool_args)
                        if skill_match:
                            result = await asyncio.wait_for(
                                skill_run(
                                    int(skill_match.group(1)),
                                    self._user_id, self._team_id,
                                    mcp_tool_args
                                ),
                                timeout=3600
                            )
                            result = json.dumps(result, ensure_ascii=False)
                            logger.debug('MCP tool result: %s', result)
                            mcp_tool_use['result'] = result
                            await self._ws_manager.send_instruction(
                                self._chatroom_id,
                                'WITHMCPTOOLRESULT',
                                {'index': index, 'result': result}
                            )
                            self._update_chatroom_message(
                                self._current_agent_message_id,
                                self._get_agent_message_with_mcp_tool_uses(self._current_agent_message)
                            )
                        elif workflow_match:
                            result_dict = await asyncio.wait_for(
                                workflow_run(
                                    int(workflow_match.group(1)),
                                    self._user_id, self._team_id,
                                    mcp_tool_args
                                ),
                                timeout=3600
                            )
                            logger.debug('Workflow run: %s', result_dict)
                            workflow_run_id = result_dict['app_run_id']
                            mcp_tool_use['workflow_run_id'] = workflow_run_id
                            self._workflow_ws_manager.add_workflow_run(
                                self._user_id, workflow_run_id,
                                self, index
                            )
                            result = json.dumps(result_dict, ensure_ascii=False)
                    except asyncio.TimeoutError:
                        await self._stop_all_mcp_tool_uses('Timeout')
                        break
                    except Exception as e:
                        logger.exception('ERROR!!')
                        result = {
                            'status': 'failed',
                            'message': f'Error executing tool {mcp_tool_name}: {e}'
                        }
                        result = json.dumps(result, ensure_ascii=False)
                        mcp_tool_use['result'] = result
                        await self._ws_manager.send_instruction(
                            self._chatroom_id,
                            'WITHMCPTOOLRESULT',
                            {'index': index, 'result': result}
                        )
                        self._update_chatroom_message(
                            self._current_agent_message_id,
                            self._get_agent_message_with_mcp_tool_uses(self._current_agent_message)
                        )
                        if workflow_run_id := mcp_tool_use['workflow_run_id']:
                            self._workflow_ws_manager.remove_workflow_run(self._user_id, workflow_run_id)

        # Wait for the MCP tool uses to finish
        while any(mcp_tool_use['result'] is None for mcp_tool_use in self._mcp_tool_uses):
            for index, mcp_tool_use in enumerate(self._mcp_tool_uses):
                try:
                    self._mcp_tool_use_lock.clear()
                    await asyncio.wait_for(self._mcp_tool_use_lock.wait(), timeout=3600)
                except asyncio.TimeoutError:
                    await self._stop_all_mcp_tool_uses('Timeout')
                    break

    def _append_mcp_tool_uses_to_history_messages(self, agent_id: int) -> None:
        # Append the tool use and tool result to the history messages
        for mcp_tool_use in self._mcp_tool_uses:
            self._history_messages.append({
                'agent_id': agent_id,
                'type': 'tool_use',
                'message': json.dumps(
                    {
                        'name': mcp_tool_use['name'],
                        'args': mcp_tool_use['args']
                    },
                    ensure_ascii=False
                )
            })
            self._history_messages.append({
                'agent_id': 0,
                'type': 'tool_result',
                'message': mcp_tool_use['result']
            })

    async def _talk_to_agent(self, agent_id: int) -> None:
        try:
            # Check if there is a temporary dataset for this chatroom
            override_dataset = datasets.select_one(
                columns=['id'],
                conditions=[
                    {'column': 'temporary_chatroom_id', 'value': self._chatroom_id},
                    {'column': 'status', 'value': 1}
                ]
            )

            self._current_agent_message_id = self._create_chatroom_message(agent_id)
            self._current_agent_message = ''
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            self._console_log('Agent message: \033[36m')  # Print the agent message in green
            for _ in range(20):
                agent_message = ''

                messages, messages_in_last_section, user_messages = self._get_history_messages_list_grouped(self._model_config_ids[agent_id])
                user_message = messages_in_last_section[0]['message']
                agent_user_subprompt = get_language_content(
                    'chatroom_agent_user_subprompt',
                    self._user_id,
                    append_ret_lang_prompt=False
                ).format(
                    messages = json.dumps(messages, ensure_ascii=False),
                    topic = self._topic,
                    user_message = user_message,
                    messages_in_last_section = json.dumps(messages_in_last_section, ensure_ascii=False),
                    user_messages = user_messages
                )
                prompt = Prompt(user=agent_user_subprompt)
                agent_node = AgentNode(
                    title=f'Agent {agent_id}',
                    input=ObjectVariable('Input'),
                    agent_id=agent_id,
                    # Ability ID takes effect only when the chatroom has only one agent
                    ability_id=self._ability_id if len(self._model_config_ids) <= 2 else 0,
                    prompt=prompt
                )

                new_text = True
                async for chunk in agent_node.run_in_chatroom(
                    context=Context(),
                    user_id=self._user_id,
                    type=2,
                    agent_run_type=3,
                    chatroom_id=self._chatroom_id,
                    override_rag_input=self._user_message,
                    override_dataset_id=override_dataset['id'] if override_dataset else None,
                    override_file_list=self._image_list if self._current_round == 0 else None,
                    mcp_tool_list=self._desktop_mcp_tool_list,
                    is_desktop=self._is_desktop
                ):
                    if isinstance(chunk, int):
                        # Agent run ID
                        app_runs.set_chatroom_message_id(chunk, self._current_agent_message_id)
                        continue
                    if tool_call_chunks := chunk.tool_call_chunks:
                        for tool_call_chunk in tool_call_chunks:
                            if tool_call_chunk['type'] == 'tool_call_chunk':
                                mcp_tool_index = tool_call_chunk['index']
                                if mcp_tool_name := tool_call_chunk['name']:
                                    self._console_log(
                                        '\033[91mTool call: '
                                        f'\033[0mName: \033[36m{mcp_tool_name} '
                                        '\033[0mArgs: \033[36m'
                                    )
                                    self._mcp_tool_uses.append({
                                        'index': mcp_tool_index,
                                        'name': mcp_tool_name,
                                        'skill_or_workflow_name': None,
                                        'workflow_run_id': 0,
                                        'workflow_confirmation_status': None,
                                        'args': '',
                                        'result': None
                                    })
                                if mcp_tool_input := tool_call_chunk['args']:
                                    self._console_log(mcp_tool_input)
                                    for mcp_tool_use in self._mcp_tool_uses:
                                        if mcp_tool_use['index'] == mcp_tool_index:
                                            mcp_tool_use['args'] += mcp_tool_input
                                            break
                                    else:
                                        raise Exception(f'Cannot find MCP tool use: {tool_call_chunk}')
                            else:
                                raise Exception(f'Unsupported tool call chunk type: {tool_call_chunk["type"]}')
                    if content := chunk.content:
                        if isinstance(content, str):
                            self._console_log(content)
                            agent_message += content
                            self._current_agent_message += content
                            await self._ws_manager.send_agent_reply(
                                self._chatroom_id,
                                agent_id, self._ability_id,
                                content, agent_message, new_text
                            )
                            new_text = False
                        elif isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict):
                                    if item['type'] == 'text':
                                        item_text: str = item['text']
                                        if item_text:
                                            self._console_log(item_text)
                                            agent_message += item_text
                                            self._current_agent_message += item_text
                                            await self._ws_manager.send_agent_reply(
                                                self._chatroom_id,
                                                agent_id, self._ability_id,
                                                item_text, agent_message, new_text
                                            )
                                            new_text = False
                                    elif item['type'] == 'tool_use':
                                        # Tool use has been handled in the tool_call_chunks
                                        pass
                                    else:
                                        raise Exception(f'Unsupported content item type: {item}')
                                else:
                                    raise Exception(f'Unsupported content item: {item}')
                        else:
                            raise Exception(f'Unsupported content: {content}')
                    if usage_metadata := chunk.usage_metadata:
                        prompt_tokens += usage_metadata['input_tokens']
                        completion_tokens += usage_metadata['output_tokens']
                        total_tokens += usage_metadata['total_tokens']
                        
                self._console_log('\n')
                
                self._history_messages.append({
                    'agent_id': agent_id,
                    'type': 'text',
                    'message': agent_message
                })
                
                if self._terminate():
                    break

                if not self._mcp_tool_uses:
                    # No MCP tool use, stop invoking the LLM
                    self._update_chatroom_message_and_token_usage(
                        self._current_agent_message_id, self._current_agent_message,
                        prompt_tokens, completion_tokens, total_tokens
                    )
                    break
                else:
                    self._update_chatroom_message_and_token_usage(
                        self._current_agent_message_id,
                        self._get_agent_message_with_mcp_tool_uses(self._current_agent_message),
                        prompt_tokens, completion_tokens, total_tokens
                    )
                    new_text = False
                    self._mcp_tool_is_using = True
                    self._mcp_tool_use_is_interrupted = False

                    await self._start_mcp_tool_uses()
                    await self._wait_for_mcp_tool_uses()
                    self._append_mcp_tool_uses_to_history_messages(agent_id)
                    self._current_agent_message = self._get_agent_message_with_mcp_tool_uses(self._current_agent_message)

                    # Clear the MCP tool uses and reset the MCP tool use flag
                    self._mcp_tool_uses.clear()
                    self._mcp_tool_is_using = False
                    if self._mcp_tool_use_is_interrupted:
                        # Terminate the chat if the MCP tool use is interrupted
                        chatrooms.update(
                            {'column': 'id', 'value': self._chatroom_id},
                            {'chat_status': 0}
                        )
                        self._mcp_tool_use_is_interrupted = False
                        break

                if self._terminate():
                    break

            await self._ws_manager.end_agent_reply(self._chatroom_id)
            self._last_speaker_id = agent_id
            app_runs.increment_steps(self._app_run_id)
            app_runs.increment_token_usage(
                self._app_run_id,
                prompt_tokens, completion_tokens, total_tokens
            )
        finally:
            self._console_log('\033[0m')  # Reset the color
            has_connections = self._ws_manager.has_connections(self._chatroom_id)
            if not has_connections:
                chatrooms.update(
                    {'column': 'id', 'value': self._chatroom_id},
                    {'active': 1}
                )

    def _terminate(self) -> bool:
        '''
        Check if the chat should terminate.
        '''
        chatroom = chatrooms.select_one(
            columns=['chat_status'],
            conditions=[
                {'column': 'id', 'value': self._chatroom_id},
                {'column': 'status', 'value': 1}
            ]
        )
        if chatroom:
            if chatroom['chat_status'] == 0:
                # Terminate chat if the user has pressed the stop button
                logger.debug('Stop button pressed. The chat will terminate soon')
                return True
        else:
            # Terminate chat if the chatroom has been disabled or deleted
            logger.debug('Chatroom is no longer available. The chat will terminate soon')
            return True
        return False
    
    def _add_file_content_to_message(
        self,
        message: Dict[str, Any],
        mode: Literal['all', 'image_only', 'document_only'] = 'all'
    ) -> None:
        if message.get('file_list') and message.get('file_content_list'):
            for file_var_value in message['file_list']:
                if isinstance(file_var_value, int):
                    attr = 'id'
                    value = file_var_value
                elif isinstance(file_var_value, str):
                    attr = 'path'
                    if file_var_value[0] == '/':
                        value = file_var_value[1:]
                    file_path = project_root.joinpath('storage').joinpath(value)
                    value = str(file_path)
                else:
                    raise Exception('Unsupported value type!')
                for file_content in message['file_content_list']:
                    if (mode == 'image_only' and file_content['type'] != 'image') or (mode == 'document_only' and file_content['type'] != 'document'):
                        continue
                    if file_content[attr] == value:
                        message['message'] += f'\n******Start of {file_content["name"]}******\n{file_content["content"]}\n******End of {file_content["name"]}******\n'

    def _split_agent_message(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        agent_id = message['agent_id']
        if agent_id == 0:
            message['type'] = 'text'
            return [message]
            
        topic = message['topic']
        content = message['message']
        
        pattern = r'<<<mcp-tool-start>>>(.*?)<<<mcp-tool-end>>>'
        # Find all matches
        matches = list(re.finditer(pattern, content, re.DOTALL))
        if not matches:
            message['type'] = 'text'
            return [message]
            
        # Split messages
        result = []
        last_end = 0
        
        for match in matches:
            # Add text before tool call
            if match.start() > last_end:
                text_content = content[last_end:match.start()]
                if text_content:
                    result.append({
                        'agent_id': agent_id,
                        'topic': topic,
                        'type': 'text',
                        'message': text_content
                    })
            
            # Add tool call messages
            mcp_tool = json.loads(match.group(1))
            
            result.append({
                'agent_id': agent_id,
                'topic': topic,
                'type': 'tool_use',
                'message': json.dumps({'name': mcp_tool['name'], 'args': mcp_tool['args']}, ensure_ascii=False)
            })
            
            result.append({
                'agent_id': 0,
                'topic': topic,
                'type': 'tool_result',
                'message': mcp_tool['result']
            })
            
            last_end = match.end()
        
        # Add the last piece of text
        if last_end < len(content):
            text_content = content[last_end:]
            if text_content:
                result.append({
                    'agent_id': agent_id,
                    'topic': topic,
                    'type': 'text',
                    'message': text_content
                })
                
        return result
    
    def load_history_messages(self, messages: List[Dict[str, Any]]) -> None:
        for message in messages:
            self._add_file_content_to_message(message, 'all')
            split_messages = self._split_agent_message(message)
            self._history_messages.extend(split_messages)

    async def _generate_title(self):
        logger.debug('Generating title...')
        messages, _, _ = self._get_history_messages_list(self._model_config_ids[0])
        
        system_prompt = get_language_content(
            'chatroom_title_system',
            self._user_id
        )
        user_prompt = get_language_content(
            'chatroom_title_user',
            self._user_id,
            append_ret_lang_prompt=False
        ).format(
            messages=json.dumps(messages, ensure_ascii=False)
        )

        llm_node = LLMNode(
            title='Title Generator',
            desc='Generate title',
            model_config_id=self._model_config_ids[0],
            prompt=Prompt(system_prompt, user_prompt)
        )
        result = llm_node.run()
        assert result['status'] == 'success', result['message']
        
        result_data = result['data']
        title = result_data['outputs']['value']
        logger.debug('Generated title: %s', title)
        await self._ws_manager.send_instruction(self._chatroom_id, 'TITLE', title)
        
        model_data = result_data['model_data']
        llm_input_var = model_data['messages']
        llm_input = []
        for role, message_var in llm_input_var:
            if message_var['type'].startswith('array'):
                message_values = []
                for message_value in message_var['values']:
                    message_values.append(message_value['value'])
                llm_input.append([role, message_values])
            else:
                llm_input.append([role, message_var['value']])
            
        has_connections = self._ws_manager.has_connections(self._chatroom_id)
        prompt_tokens = result_data['prompt_tokens']
        completion_tokens = result_data['completion_tokens']
        total_tokens = result_data['total_tokens']
        
        chatroom_messages.insert(
            {
                'chatroom_id': self._chatroom_id,
                'app_run_id': self._app_run_id,
                'llm_input': llm_input,
                'message': title,
                'message_type': 2,
                'model_data': model_data,
                'is_read': 1 if has_connections else 0,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            }
        )
        app_runs.increment_token_usage(
            self._app_run_id,
            prompt_tokens, completion_tokens, total_tokens
        )
        
        app_run = app_runs.select_one(
            columns=['app_id'],
            conditions={'column': 'id', 'value': self._app_run_id}
        )
        apps.update(
            {'column': 'id', 'value': app_run['app_id']},
            {'name': title}
        )

    async def chat(self, resume: bool, file_list: Optional[List[Union[int, str]]] = None) -> None:
        history_messages_count_on_start = len(self._history_messages)
        performed_rounds = 0
        if resume:
            # Resume the unfinished chat
            for message in reversed(self._history_messages):
                if message['agent_id'] == 0:
                    break
                else:
                    performed_rounds += 1
        else:
            # Start a new chat
            self._user_speak(self._user_message, file_list)
        
        for self._current_round in range(performed_rounds, self._max_round):
            agent_id = await self._select_next_speaker()
            if self._terminate():
                break
            
            logger.debug('Selected agent: %s', agent_id)
            if agent_id == 0:
                logger.debug('Terminating chat...')
                break

            await self._talk_to_agent(agent_id)

            if self._current_round == 0:
                # Add image content to current user message content
                for message in reversed(self._history_messages):
                    if message['agent_id'] == 0:
                        self._add_file_content_to_message(message, 'image_only')
                        break

            if self._terminate():
                self._current_round += 1
                break
        else:
            self._current_round += 1

        logger.debug('Total chat rounds: %d', self._current_round)

        if self._is_temporary and history_messages_count_on_start == 0:
            # Generate title if the chat is new
            await self._generate_title()
