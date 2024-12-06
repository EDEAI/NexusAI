import json
import sys

from collections import deque
from typing import Dict, List, Optional, Sequence, Tuple, Union

from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.outputs import ChatGeneration

from .websocket import WebSocketManager
from core.database.models import (
    AgentAbilities,
    Agents,
    AppRuns,
    ChatroomMessages,
    Chatrooms,
    Models
)
from core.llm import Messages, Prompt
from core.llm.models import LLMPipeline
from languages import get_language_content
from log import Logger


logger = Logger.get_logger('chatroom')

agent_abilities = AgentAbilities()
app_runs = AppRuns()
chatrooms = Chatrooms()
chatroom_messages = ChatroomMessages()


class Chatroom:
    @staticmethod
    def _get_llm_pipeline(model_info: Dict, return_json: bool = False) -> LLMPipeline:
        llm_config = {**model_info['supplier_config'], **model_info['model_config']}
        if return_json:
            llm_config['model_kwargs'] = {'response_format': {'type': 'json_object'}}
        return LLMPipeline(supplier=model_info['supplier_name'], config=llm_config)
    
    @staticmethod
    def _console_log(content: str) -> None:
        sys.stdout.write(content)
        sys.stdout.flush()

    def _init_llm_pipelines(self, all_agent_ids: Sequence[int], absent_agent_ids: Sequence[int]) -> None:
        model_info = Models().get_model_by_type(1, self._team_id, uid=self._user_id)
        self._llm_pipelines[0] = self._get_llm_pipeline(model_info, return_json=True)
        for agent_id in all_agent_ids:
            agent = Agents().select_one(
                columns=['id', 'apps.name', 'obligations', 'model_config_id'],
                joins=[('left', 'apps', 'agents.app_id = apps.id')],
                conditions={'column': 'id', 'value': agent_id}  # Include deleted agents (with status=3)
            )
            assert agent, f'Agent {agent_id} does not exist!'
            abilities = agent_abilities.get_abilities_by_agent_id(agent_id)
            agent['abilities'] = abilities

            self._all_agents[agent_id] = agent
            if agent_id not in absent_agent_ids:
                model_config_id = agent['model_config_id']
                model_info = Models().get_model_by_config_id(model_config_id)
                assert model_info, f'Model configuration {model_config_id} not found.'
                self._llm_pipelines[agent_id] = self._get_llm_pipeline(model_info)
    
    def __init__(
        self,
        user_id: int,
        team_id: int,
        chatroom_id: int,
        app_run_id: int,
        all_agent_ids: Sequence[int],
        absent_agent_ids: Sequence[int],
        max_round: int,
        smart_selection: bool,
        ws_manager: WebSocketManager,
        user_message_id: int = 0,
        topic: Optional[str] = None
    ) -> None:
        self._user_id = user_id
        self._team_id = team_id
        self._chatroom_id = chatroom_id
        self._app_run_id = app_run_id
        self._all_agents = {}
        # self._llm_pipelines: dict
        # keys are IDs of all active agents with the addition of 0 (which is the Speaker Selector)
        # values are LLMPipeline instances
        self._llm_pipelines: Dict[int, LLMPipeline] = {}
        self._init_llm_pipelines(all_agent_ids, absent_agent_ids)
        self._max_round = max_round
        self._smart_selection = smart_selection
        self._ws_manager = ws_manager
        self._user_message_id = user_message_id
        self._topic = topic
        # self._history_messages: list
        # each item is a dict with the following keys:
        # - agent_id: int, 0 means user, > 0 means agent
        # - message: str
        # - topic: str
        self._history_messages: List[Dict[str, Union[int, str]]] = []

    def _get_agents_info(self) -> str:
        '''
        Get information of all active agents as a JSON string in an AI prompt.
        '''
        info = []
        for agent_id in self._llm_pipelines:
            if agent_id != 0:
                agent = self._all_agents[agent_id]
                abilities = agent['abilities']
                if abilities:
                    abilities_content = json.dumps([ability['content'] for ability in abilities], ensure_ascii=False)
                    description: str = get_language_content('chatroom_agent_description_with_abilities', self._user_id)
                    description = description.format(
                        obligations=agent['obligations'],
                        abilities=abilities_content
                    )
                else:
                    description: str = get_language_content('chatroom_agent_description_with_no_ability', self._user_id)
                    description = description.format(obligations=agent['obligations'])
                info.append(
                    {
                        'id': agent_id,
                        'name': agent['name'],
                        'description': description
                    }
                )
        return json.dumps(info, ensure_ascii=False)
        
    def _get_history_messages_list(self) -> Tuple[
        List[Dict[str, Union[int, str]]],
        List[Dict[str, Union[int, str]]]
    ]:
        '''
        Get all history messages and the last section of them as JSON strings in an AI prompt.
        '''
        messages = []
        for message in self._history_messages:
            user_str = get_language_content('chatroom_role_user', self._user_id)
            agent_str = get_language_content('chatroom_role_agent', self._user_id)
            agent_id = message['agent_id']
            message_for_llm = {
                'id': agent_id,
                'name': user_str if agent_id == 0 else self._all_agents[agent_id]['name'],
                'role': user_str if agent_id == 0 else agent_str,
                'message': message['message']
            }
            if (topic := message['topic']) is not None:
                message_for_llm['topic'] = topic
            messages.append(message_for_llm)
        messages_in_last_section = deque()
        for message in reversed(messages):
            messages_in_last_section.appendleft(message)
            if message['id'] == 0:
                break
        return (
            messages,
            list(messages_in_last_section)
        )
    
    def _user_speak(self, user_message: str) -> None:
        '''
        Append a user message to the history messages and insert it into the database.
        '''
        self._console_log(f'User message: \033[91m{user_message}\033[0m\n')
        self._history_messages.append({'agent_id': 0, 'message': user_message, 'topic': self._topic})
        self._user_message_id = chatroom_messages.insert(
            {
                'chatroom_id': self._chatroom_id,
                'app_run_id': self._app_run_id,
                'user_id': self._user_id,
                'message': user_message,
                'is_read': 1 if self._ws_manager.has_connections(self._chatroom_id) else 0
            }
        )
        app_runs.increment_steps(self._app_run_id)

    async def _select_next_speaker(self) -> int:
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        llm_pipeline = self._llm_pipelines[0]  # Speaker Selector
        agent_id = None
        for i in range(5):  # Try 5 times
            last_speaker_id = self._history_messages[-1]['agent_id']
            if last_speaker_id == 0:
                # If the last speaker is the user, the Speaker Selector must choose an agent
                system_prompt = get_language_content(
                    'chatroom_manager_system',
                    self._user_id
                )
                user_prompt = get_language_content(
                    'chatroom_manager_user',
                    self._user_id
                )
            else:
                # If the last speaker is an agent,
                if self._smart_selection or len(self._llm_pipelines) <= 2:
                    # and (smart selection is enabled or there is only one agent), the Speaker Selector must stop the chat
                    return 0
                else:
                    # and smart selection is disabled, the Speaker Selector will choose an agent, or stop the chat
                    system_prompt = get_language_content(
                        'chatroom_manager_system_with_optional_selection',
                        self._user_id
                    )
                    user_prompt = get_language_content(
                        'chatroom_manager_user_with_optional_selection',
                        self._user_id
                    )
            messages, messages_in_last_section = self._get_history_messages_list()
            user_prompt = user_prompt.format(
                agent_count = len(self._llm_pipelines) - 1,
                agents = self._get_agents_info(),
                user_message = messages_in_last_section[0]['message'],
                topic = self._topic,
                messages = json.dumps(messages, ensure_ascii=False),
                messages_in_last_section = json.dumps(messages_in_last_section, ensure_ascii=False)
            )
            if i > 0:
                # the Speaker Selector has tried more than once
                user_prompt = get_language_content(
                    'chatroom_manager_user_invalid_selection',
                    self._user_id
                ).format(
                    agent_id=agent_id
                ) + user_prompt

            # Prepare the input for the Speaker Selector
            input_messages = Messages()
            input_messages.add_prompt(Prompt(system_prompt, user_prompt))
            input_ = [(role, message.value) for role, message in input_messages.messages]
            logger.debug('Requesting LLM...')
            # Request LLM
            result = await llm_pipeline.llm.agenerate([input_])
            result: ChatGeneration = result.generations[0][0]
            manager_message: AIMessage = result.message
            logger.debug('Speaker selector output: %s', manager_message.content)
            has_connections = self._ws_manager.has_connections(self._chatroom_id)

            # LLM output & token usage recording
            if usage_metadata := manager_message.usage_metadata:
                prompt_tokens = usage_metadata['input_tokens']
                completion_tokens = usage_metadata['output_tokens']
                total_tokens = usage_metadata['total_tokens']
            chatroom_messages.insert(
                {
                    'chatroom_id': self._chatroom_id,
                    'app_run_id': self._app_run_id,
                    'llm_input': input_,
                    'message': manager_message.content,
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

            llm_output = json.loads(manager_message.content)
            # Update the topic if the last speaker is the user
            if last_speaker_id == 0:
                self._topic = llm_output['topic']
                logger.debug('Current topic: %s', self._topic)
                self._history_messages[-1]['topic'] = self._topic
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
            if agent_id in self._llm_pipelines:
                return agent_id
            # else: the Speaker Selector returned an invalid agent ID, try again

        # If the Speaker Selector has tried 5 times and still returned an invalid agent ID, stop the chat
        return 0

    async def _talk_to_agent(self, agent_id: int) -> None:
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        llm_pipeline = self._llm_pipelines[agent_id]
        agent = self._all_agents[agent_id]
        abilities = agent['abilities']
        messages, messages_in_last_section = self._get_history_messages_list()

        # Prepare the input for the agent
        if abilities:
            # If the agent has abilities, use the prompt template for agents with abilities
            agent_user_prompt = get_language_content(
                'chatroom_agent_user_with_abilities',
                self._user_id
            ).format(
                messages = json.dumps(messages, ensure_ascii=False),
                topic = self._topic,
                user_message = messages_in_last_section[0]['message'],
                messages_in_last_section = json.dumps(messages_in_last_section, ensure_ascii=False),
                id_ = agent_id,
                name = agent['name'],
                obligations = agent['obligations'],
                abilities = json.dumps([ability['content'] for ability in abilities], ensure_ascii=False)
            )
        else:
            # If the agent has no abilities, use the prompt template for agents with no abilities
            agent_user_prompt = get_language_content(
                'chatroom_agent_user_with_no_ability',
                self._user_id
            ).format(
                messages = json.dumps(messages, ensure_ascii=False),
                topic = self._topic,
                user_message = messages_in_last_section[0]['message'],
                messages_in_last_section = json.dumps(messages_in_last_section, ensure_ascii=False),
                id_ = agent_id,
                name = agent['name'],
                obligations = agent['obligations']
            )
        input_messages = Messages()
        input_messages.add_prompt(
            Prompt(
                system=get_language_content('chatroom_agent_system', self._user_id),
                user=agent_user_prompt
            )
        )
        input_ = [(role, message.value) for role, message in input_messages.messages]
        logger.debug('Requesting LLM...')
        self._console_log('Agent message: \033[36m')  # Print the agent message in green
        chunk: AIMessageChunk
        full_chunk: Optional[AIMessageChunk] = None
        # Request LLM
        async for chunk in llm_pipeline.llm.astream(
            input_,
            stream_usage=True
        ):
            if content := chunk.content:
                self._console_log(content)
                full_chunk = chunk if full_chunk is None else full_chunk + chunk
                await self._ws_manager.send_agent_reply(
                    self._chatroom_id,
                    agent_id,
                    content,
                    full_chunk.content
                )
            # Get token usage
            if usage_metadata := chunk.usage_metadata:
                prompt_tokens = usage_metadata['input_tokens']
                completion_tokens = usage_metadata['output_tokens']
                total_tokens = usage_metadata['total_tokens']
        self._console_log('\033[0m\n')  # Reset the color
        agent_message = full_chunk.content if full_chunk else ''
        await self._ws_manager.end_agent_reply(
            self._chatroom_id,
            agent_id,
            agent_message
        )

        # Append the agent message to the history messages and insert it into the database
        self._history_messages.append({'agent_id': agent_id, 'message': agent_message, 'topic': self._topic})
        has_connections = self._ws_manager.has_connections(self._chatroom_id)
        chatroom_messages.insert(
            {
                'chatroom_id': self._chatroom_id,
                'app_run_id': self._app_run_id,
                'agent_id': agent_id,
                'llm_input': input_,
                'message': agent_message,
                'topic': self._topic,
                'is_read': 1 if has_connections else 0,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            }
        )
        app_runs.increment_steps(self._app_run_id)
        app_runs.increment_token_usage(
            self._app_run_id,
            prompt_tokens, completion_tokens, total_tokens
        )
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

    def load_history_messages(self, messages: List[Dict[str, Union[int, str]]]) -> None:
        self._history_messages.extend(messages)

    async def chat(self, user_message: Optional[str] = None) -> None:
        performed_rounds = 0
        if user_message is None:
            # Resume the unfinished chat
            for message in reversed(self._history_messages):
                if message['agent_id'] == 0:
                    break
                else:
                    performed_rounds += 1
        else:
            # Start a new chat
            self._user_speak(user_message)
            
        for round_ in range(performed_rounds, self._max_round):
            agent_id = await self._select_next_speaker()
            logger.debug('Selected agent: %s', agent_id)
            if agent_id == 0:
                logger.debug('Terminating chat...')
                break

            await self._talk_to_agent(agent_id)

            if self._terminate():
                round_ += 1
                break
        else:
            round_ += 1

        logger.debug('Total chat rounds: %d', round_)
    