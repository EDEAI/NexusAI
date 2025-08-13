import asyncio, sys, json, re
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from collections import deque
from copy import deepcopy
from typing import Any, AsyncIterator, Callable, Dict, Iterable, List, Optional, Tuple, Union

import dashscope
from google import genai
import httpx
import tiktoken

from anthropic import Anthropic
from langchain_core.documents import Document
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough
from langchain_core.runnables.utils import Input, Output


from core.database.models.agent_chat_messages import AgentChatMessages
from core.document import DocumentLoader

from . import Node
from ...variables import ArrayVariable, Variable
from ...context import Context
from database.models import Models, AppNodeExecutions, DocumentSegments, Documents, AIToolLLMRecords, UploadFiles
from llm.models import LLMPipeline
from llm.prompt import create_prompt_from_dict, replace_prompt_with_context
from llm.messages import Messages, create_messages_from_serialized_format

from core.helper import truncate_agent_messages_by_token_limit, get_file_content_list
from core.database.models import (Models, Users)


project_root = Path(__file__).absolute().parent.parent.parent.parent.parent

document_segments = DocumentSegments()
documents = Documents()
models = Models()
users = Users()

class LLMBaseNode(Node):
    """
    Base class for all LLM nodes.
    """
    
    schema_key = None # The schema key for the LLM model
    
    def __init__(self, **kwargs):
        """
        Initializes a new instance of the LLMBaseNode class.
        """
        super().__init__(**kwargs)
        
    def duplicate_braces(self, text: str) -> str:
        """
        Duplicates braces in the text.
        
        Args:
            text (str): The text to duplicate braces in.
            
        Returns:
            str: The text with duplicated braces.
        """
        return text.replace("{", "{{").replace("}", "}}")

    @classmethod
    def _get_tokenizer(cls, supplier_name: str, model_name: str, api_key: str) -> Callable[[str], int]:

        """
        Get the appropriate tokenizer based on the model name
        
        Args:
            supplier_name (str): Supplier name, e.g., 'OpenAI', 'Anthropic'
            model_name (str): Model name, e.g., 'gpt-3.5-turbo', 'gpt-4', 'claude-3-opus'
            api_key (str): API key for the supplier
            
        Returns:
            Callable[[str], int]: A function that takes a string and returns the number of tokens.
        """
        match supplier_name:
            case 'OpenAI':
                try:
                    encoding = tiktoken.encoding_for_model(model_name)
                except:
                    encoding = tiktoken.get_encoding("cl100k_base")
                return lambda text: len(encoding.encode(text))
            case 'Anthropic':
                anthropic = Anthropic(api_key=api_key)
                return lambda text: anthropic.messages.count_tokens(
                    model=model_name,
                    messages=[{'role': 'user', 'content': text}],
                ).input_tokens
            case 'Tongyi':
                tokenizer = dashscope.get_tokenizer('qwen-turbo')
                return lambda text: len(tokenizer.encode(text))
            case 'DeepSeek':
                from transformers import AutoTokenizer
                chat_tokenizer_dir = project_root.joinpath('core/helper/deepseek-tokenizer')
                tokenizer = AutoTokenizer.from_pretrained(chat_tokenizer_dir, trust_remote_code=True)
                return lambda text: len(tokenizer.encode(text))
            case 'Doubao':
                def _count_tokens(text: str) -> int:
                    response = httpx.post(
                        'https://ark.cn-beijing.volces.com/api/v3/tokenization',
                        json={
                            'model': model_name,
                            'text': text,
                        },
                        headers={
                            'Authorization': f'Bearer {api_key}',
                            'Content-Type': 'application/json',
                        }
                    )
                    response_data = response.json()
                    return response_data['data'][0]['total_tokens']

                return _count_tokens
            case 'Google':
                client = genai.Client(api_key=api_key)
                return lambda text: client.models.count_tokens(
                    model=model_name,
                    contents=text,
                ).total_tokens
            case _:
                return lambda _: 0


    @classmethod
    def _group_chatroom_messages(
        cls,
        messages: Iterable[Dict[str, Union[int, str]]]
    ) -> List[List[Dict[str, Union[int, str]]]]:
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
        return message_sections

    @classmethod
    def _count_tokens(
        cls,
        tokenizer: Callable[[str], int],
        messages: Messages,
        chatroom_prompt_args: Dict[str, Any],
        mcp_tool_list: Optional[List[Dict[str, Any]]],
        group_messages: bool,
        model_config: Dict[str, Any],
        restrict_max_rounds: bool,
        input_variables: Optional[Dict[str, Any]]
    ) -> int:
        chatroom_messages = chatroom_prompt_args['messages']
        if group_messages:
            chatroom_messages = cls._group_chatroom_messages(chatroom_messages)
        else:
            chatroom_messages = list(chatroom_messages)
        chatroom_prompt_args['messages'] = json.dumps(chatroom_messages, ensure_ascii=False)
        if 'user_prompt' in input_variables:
            input_variables['user_prompt'] = input_variables['user_prompt'].format(**chatroom_prompt_args)
        else:
            input_variables.update(chatroom_prompt_args)
        messages_as_langchain_format = messages.to_langchain_format(
            model_config['model_name'],
            model_config['supplier_name'],
            restrict_max_rounds,
            input_variables=input_variables
        )
        message_list = []
        for msg in messages_as_langchain_format:
            if isinstance(msg, tuple):
                message_list.append(msg)
            else:
                msg_role = msg.type
                msg_content = msg.content
                if isinstance(msg_content, str):
                    message_list.append((msg_role, msg_content))
                else:
                    for sub_msg in msg_content:
                        if sub_msg['type'] == 'text':
                            message_list.append((msg_role, sub_msg))
                        # else sub_msg is an image, just ignore it
        text = json.dumps(message_list, ensure_ascii=False)
        if mcp_tool_list:
            text += json.dumps(mcp_tool_list, ensure_ascii=False)
        return tokenizer(text)

    def _truncate_chatroom_messages_by_token_limit(
        self,
        messages: Messages,
        chatroom_prompt_args: Dict[str, Any],
        mcp_tool_list: Optional[List[Dict[str, Any]]],
        group_messages: bool,
        model_config: Dict[str, Any],
        restrict_max_rounds: bool,
        input_variables: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        chatroom_messages = chatroom_prompt_args['messages']
            
        # Get model information
        supplier_name = model_config['supplier_name']
        if supplier_name == 'Anthropic':
            model_name = model_config['model_config']['model_name']
        else:
            model_name = model_config['model_config']['model']


        api_key = model_config['supplier_config']['api_key']
        max_context_tokens = model_config['max_context_tokens']
        max_output_tokens = model_config['max_output_tokens']
        token_limit = max_context_tokens - max_output_tokens - 8192
        
        # Get appropriate tokenizer
        tokenizer = self._get_tokenizer(supplier_name, model_name, api_key)

        # Find the start index of current dialog (last user message)
        current_dialog_start = 0
        for i in reversed(range(len(chatroom_messages))):
            msg = chatroom_messages[i]
            if msg['id'] == 0 and msg['type'] == 'text':
                current_dialog_start = i  # Track the last user message position
                break

        # Split messages into history and current dialog
        history_messages = chatroom_messages[:current_dialog_start]
        current_dialog_messages = chatroom_messages[current_dialog_start:]
        
        truncated_messages = deque(current_dialog_messages)
        chatroom_prompt_args['messages'] = list(truncated_messages)
        current_tokens = self._count_tokens(
            tokenizer,
            messages, chatroom_prompt_args, mcp_tool_list, group_messages,
            model_config, restrict_max_rounds, input_variables.copy()
        )
        
        if current_tokens > token_limit:
            stop_truncating = False
            for msg in truncated_messages:
                if msg['type'] == 'tool_result':
                    # Skip if already truncated
                    if msg['message'] == '...':
                        continue

                    original_content = msg['message']

                    # Binary search for maximum allowable content length
                    low, high = 0, len(original_content)
                    while low <= high:
                        mid = (low + high) // 2
                        truncated_content = original_content[:mid] + '...'
                        msg['message'] = truncated_content

                        # Check if this truncation would bring total under limit
                        chatroom_prompt_args['messages'] = list(truncated_messages)
                        current_tokens = self._count_tokens(
                            tokenizer,
                            messages, chatroom_prompt_args, mcp_tool_list, group_messages,
                            model_config, restrict_max_rounds, input_variables.copy()
                        )
                        if current_tokens <= token_limit:
                            stop_truncating = True
                            low = mid + 1
                        else:
                            stop_truncating = False
                            high = mid - 1
                    if stop_truncating:
                        break
        else:
            # Traverse messages from newest to oldest
            for message in reversed(history_messages):
                chatroom_prompt_args['messages'] = [message] + list(truncated_messages)
                current_tokens = self._count_tokens(
                    tokenizer,
                    messages, chatroom_prompt_args, mcp_tool_list, group_messages,
                    model_config, restrict_max_rounds, input_variables.copy()
                )
                if current_tokens > token_limit:
                    break
                truncated_messages.appendleft(message)
        if group_messages:
            chatroom_messages = self._group_chatroom_messages(truncated_messages)
        else:
            chatroom_messages = list(truncated_messages)
        chatroom_prompt_args['messages'] = json.dumps(chatroom_messages, ensure_ascii=False)
        if 'user_prompt' in input_variables:
            input_variables['user_prompt'] = input_variables['user_prompt'].format(**chatroom_prompt_args)
        else:
            input_variables.update(chatroom_prompt_args)
        return input_variables
    
    def _prepare_messages_and_input(
        self, 
        app_run_id: int, 
        edge_id: str,
        context: Context,
        retrieval_chain: Optional[Runnable[Input, Output]] = None,
        input: Dict[str, Any] = {},
        file_list: Optional[List[Variable]] = None,
        correct_llm_output: bool = False,
        override_rag_input: Optional[str] = None,
        is_chat: bool = False,
        user_id: int = 0,
        agent_id: int = 0
    ) -> Tuple[Messages, Dict[str, Any]]:
        new_user_prompt = None
        if correct_llm_output:
            if edge_id:
                history = AppNodeExecutions().get_node_history(app_run_id, edge_id)
            else:
                history = AIToolLLMRecords().get_history_record(app_run_id)
            if not history or len(history) != 2:
                raise Exception("history not found.")
            if history[1].get("model_data"):
                messages = create_messages_from_serialized_format(history[1]["model_data"]["messages"])
                # Escape braces in the output text
                ai_output_str = self.duplicate_braces(history[1]["model_data"]["raw_output"])
                ai_output = Variable(name="text", type="string", value=ai_output_str)
                messages.add_ai_message(ai_output)
                correct_prompt = create_prompt_from_dict(history[0]["correct_prompt"])
                # Escape braces in the corrected prompt
                if system_prompt := correct_prompt.get_system():
                    correct_prompt.system.value = self.duplicate_braces(system_prompt)
                if user_prompt := correct_prompt.get_user():
                    correct_prompt.user.value = self.duplicate_braces(user_prompt)
                if assistant_prompt := correct_prompt.get_assistant():
                    correct_prompt.assistant.value = self.duplicate_braces(assistant_prompt)
                messages.add_prompt(correct_prompt)
            else:
                if context:
                    replace_prompt_with_context(self.data["prompt"], context, duplicate_braces=True)
                messages = Messages()
                messages.add_system_message(Variable(name="system", type="string", value=self.data["prompt"].get_system()))
                human_message = ArrayVariable(name="human", type="array[any]")
                human_message.add_value(Variable(name="text", type="string", value=self.data["prompt"].get_user()))
                if file_list:
                    for file_var in file_list:
                        human_message.add_value(file_var)
                messages.add_human_message(human_message)
        else:
            if context:
                replace_prompt_with_context(self.data["prompt"], context, duplicate_braces=True)
            messages = Messages()
            if is_chat:
                chat_history = AgentChatMessages().get_chat_agent_history(agent_id=agent_id, user_id=user_id)
                assert chat_history, 'Chat history not found.'

                # Get content of each file in the user message and fill into database
                last_user_message = chat_history[-1]
                if last_user_message['agent_run_id'] == 0 and last_user_message['file_list']:
                    file_content_list = get_file_content_list(last_user_message['file_list'])
                    last_user_message['file_content_list'] = file_content_list
                    AgentChatMessages().update_file_content_list_by_id(last_user_message['id'], file_content_list)

                # Add file content to the message content
                new_user_prompt = input['user_prompt']
                image_list = []
                for index, message in enumerate(chat_history):
                    if message['file_list'] and message['file_content_list']:
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
                                if file_content[attr] == value:
                                    if index == len(chat_history) - 1:
                                        if file_content['type'] == 'image':
                                            image_list.append(file_var_value)
                                        else:
                                            new_user_prompt += (
                                                '\n\n'
                                                '---\n\n'
                                                f'##{file_content["name"]}\n\n'
                                                f'**{attr}**: `{value}`\n\n'
                                                '```\n'
                                                f'{file_content["content"]}\n'
                                                '```\n\n'
                                                '---\n\n'
                                            )
                                    else:
                                        message['message'] += (
                                            '\n\n'
                                            '---\n\n'
                                            f'##{file_content["name"]}\n\n'
                                            f'**{attr}**: `{value}`\n\n'
                                            '```\n'
                                            f'{file_content["content"]}\n'
                                            '```\n\n'
                                            '---\n\n'
                                        )

                # Truncate Messages By Token Limit
                userinfo = users.get_user_by_id(user_id)
                model_info = models.get_model_by_type(1, userinfo['team_id'], uid=user_id)
                model_info = models.get_model_by_config_id(model_info['model_config_id'])
                chat_message_list = truncate_agent_messages_by_token_limit(chat_history, model_info)
                
                messages.add_system_message(Variable(name="text", type="string", value=self.data["prompt"].get_system()))
                human_message = ArrayVariable(name="human", type="array[any]")

                for index, chat in enumerate(chat_message_list):
                    chat_message = self.duplicate_braces(chat['message'])
                    if chat['agent_run_id'] > 0:
                        messages.add_ai_message(Variable(name="text", type="string", value=chat_message))
                    else:
                        # Determine if it is the last message
                        if index == len(chat_message_list) - 1:
                            human_message.add_value(Variable(name="text", type="string", value=self.data["prompt"].get_user()))
                        else:
                            messages.add_human_message(Variable(name="text", type="string", value=chat_message))
                if image_list:
                    for index, file_var_value in enumerate(image_list):
                        human_message.add_value(Variable(
                            name=f"file_{index}",
                            type="file",
                            sub_type="image",
                            value=file_var_value
                        ))
                messages.add_human_message(human_message)
            else:
                messages.add_system_message(Variable(name="system", type="string", value=self.data["prompt"].get_system()))
                human_message = ArrayVariable(name="human", type="array[any]")
                human_message.add_value(Variable(name="text", type="string", value=self.data["prompt"].get_user()))
                if file_list:
                    for file_var in file_list:
                        human_message.add_value(file_var)
                messages.add_human_message(human_message)
        
        if retrieval_chain:
            def format_docs(segments: List[Document]) -> str:
                document_names = {}
                formatted_docs_list = []
                for segment_obj in segments:
                    index_id = str(segment_obj.metadata['index_id'])
                    segment = document_segments.get_segment_by_index_id(index_id)
                    document_id = segment['document_id']
                    if document_id in document_names:
                        document_name = document_names[document_id]
                    else:
                        document = documents.get_document_by_id(document_id)
                        document_name = document['name']
                        document_names[document_id] = document_name
                    formatted_docs_list.append(
                        {'content': segment_obj.page_content, 'source': document_name}
                    )
                return json.dumps(formatted_docs_list, ensure_ascii=False)
            
            user_prompt = input['user_prompt'] if override_rag_input is None else override_rag_input
            rag_result = retrieval_chain.invoke(user_prompt)
            formatted_docs = format_docs(rag_result)
            input['formatted_docs'] = formatted_docs
        if new_user_prompt is not None:
            input["user_prompt"] = new_user_prompt

        return messages, input
        
    def invoke(
        self,
        app_run_id: int, 
        edge_id: str,
        context: Context,
        retrieval_chain: Optional[Runnable[Input, Output]] = None,
        input: Dict[str, Any] = {},
        file_list: Optional[List[Variable]] = None,
        return_json: bool = False,
        correct_llm_output: bool = False,
        override_rag_input: Optional[str] = None,
        is_chat: bool = False,
        user_id: int = 0,
        agent_id: int = 0,
        mcp_tool_list: Optional[List[Dict[str, Any]]] = None,
        chatroom_prompt_args: Optional[Dict[str, Any]] = None,
        group_messages: bool = False
    ) -> Tuple[Dict[str, Any], str, int, int, int]:
        """
        Workflow node invokes the LLM model to generate text using the language model.
        
        Args:
            app_run_id (int): The ID of the app run.
            edge_id (str): The UUID of the edge.
            context (Context): The context object containing all variables.
            retrieval_chain (Optional[Runnable[Input, Output]]): The retrieval chain to be used for the model.
            input (Dict[str, Any]): The input data to be passed to the model.
            file_list (Optional[List[Variable]]): The list of files to be uploaded to the model.
            return_json (bool): Indicates whether to return the output in JSON format.
            correct_llm_output (bool): Indicates whether to correct the LLM output using the correct prompt.
            override_rag_input (Optional[str]): The input to be used for the retrieval chain.
            is_chat (bool): Is it an intelligent agent chat.
            user_id (int): user id.
            agent_id (int): agent id.
            
        Returns:
            Dict[str, Any]: A dictionary containing the model data, content, prompt tokens, completion tokens, and total tokens.
        """
        model_info = Models().get_model_by_config_id(self.data["model_config_id"])
        if not model_info:
            raise Exception("Model configuration not found.")
        
        llm_config = {**model_info["supplier_config"], **model_info["model_config"]}
        if return_json and not (model_info["supplier_name"] == "OpenAI" and model_info["model_name"] in ["o1-preview", "o1-mini"]):
            llm_config["model_kwargs"] = {"response_format": {"type": "json_object"}}
        llm_pipeline = LLMPipeline(supplier=model_info["supplier_name"], config=llm_config, schema_key=self.schema_key)

        messages, input = self._prepare_messages_and_input(
            app_run_id=app_run_id,
            edge_id=edge_id,
            context=context,
            retrieval_chain=retrieval_chain,
            input=input,
            file_list=file_list,
            correct_llm_output=correct_llm_output,
            override_rag_input=override_rag_input,
            is_chat=is_chat,
            user_id=user_id,
            agent_id=agent_id
        )
        
        if model_info["supplier_name"] in ["Anthropic", "Google"]:
            messages.reorganize_messages()

        if chatroom_prompt_args:
            input = self._truncate_chatroom_messages_by_token_limit(
                messages, chatroom_prompt_args, mcp_tool_list, group_messages,
                model_info, not is_chat, input
            )
        messages_as_langchain_format = messages.to_langchain_format(
            model_info["model_name"],
            model_info["supplier_name"],
            not is_chat,
            input_variables=input
        )
        if mcp_tool_list:
            llm_pipeline.llm = llm_pipeline.llm.bind_tools([{
                'name': tool['name'],
                'description': tool['description'],
                'input_schema': tool['inputSchema']
            } for tool in mcp_tool_list])
        ai_message = llm_pipeline.invoke_llm(messages_as_langchain_format)
        content = ai_message.content
        if return_json:
            try:
                content = self.extract_json_from_string(content)
            except Exception:
                raise Exception(f"AI response format error.\nAI message: {ai_message}")
        token_usage = ai_message.response_metadata["token_usage"]
        prompt_tokens = token_usage["prompt_tokens"]
        completion_tokens = token_usage["completion_tokens"]
        total_tokens = token_usage["total_tokens"]
        
        messages.replace_variables(input)
        model_data = {
            'model': llm_config,
            'messages': messages.serialize(),
            'raw_output': ai_message.content
        }
        
        return model_data, content, prompt_tokens, completion_tokens, total_tokens
    
    def get_ainvoke_func(
        self,
        app_run_id: int, 
        edge_id: str,
        context: Context,
        retrieval_chain: Optional[Runnable[Input, Output]] = None,
        input: Union[str, Dict[str, Any]] = {},
        file_list: Optional[ArrayVariable] = None,
        return_json: bool = False,
        correct_llm_output: bool = False,
        override_rag_input: Optional[str] = None,
        mcp_tool_list: Optional[List[Dict[str, Any]]] = None,
        chatroom_prompt_args: Optional[Dict[str, Any]] = None,
        group_messages: bool = False
    ) -> Tuple[Dict[str, Any], Callable[[], AsyncIterator[AIMessageChunk]]]:
        """
        This function is used to get the model data and the async AI invoke function.
        
        Args:
            app_run_id (int): The ID of the app run.
            edge_id (str): The UUID of the edge.
            context (Context): The context object containing all variables.
            retrieval_chain (Optional[Runnable[Input, Output]]): The retrieval chain to be used for the model.
            input (Dict[str, Any]): The input data to be passed to the model.
            file_list (Optional[ArrayVariable]): The list of files to be uploaded to the model.
            return_json (bool): Indicates whether to return the output in JSON format.
            correct_llm_output (bool): Indicates whether to correct the LLM output using the correct prompt.
            override_rag_input (Optional[str]): The input to be used for the retrieval chain, if provided.

        Returns:
            Dict[str, Any]: A dictionary containing the model data, content, prompt tokens, completion tokens, and total tokens.
        """
        model_info = Models().get_model_by_config_id(self.data["model_config_id"])
        if not model_info:
            raise Exception("Model configuration not found.")
        
        llm_config = {**model_info["supplier_config"], **model_info["model_config"]}
        if return_json and not (model_info["supplier_name"] == "OpenAI" and model_info["model_name"] in ["o1-preview", "o1-mini"]):
            llm_config["model_kwargs"] = {"response_format": {"type": "json_object"}}
        llm_pipeline = LLMPipeline(supplier=model_info["supplier_name"], config=llm_config, schema_key=self.schema_key)
        messages, input = self._prepare_messages_and_input(
            app_run_id=app_run_id,
            edge_id=edge_id,
            context=context,
            retrieval_chain=retrieval_chain,
            input=input,
            file_list=file_list,
            correct_llm_output=correct_llm_output,
            override_rag_input=override_rag_input
        )
        
        if model_info["supplier_name"] in ["Anthropic", "Google"]:
            messages.reorganize_messages()

        if chatroom_prompt_args:
            input = self._truncate_chatroom_messages_by_token_limit(
                messages, chatroom_prompt_args, mcp_tool_list, group_messages,
                model_info, True, input
            )

        async def ainvoke():
            llm_input = messages.to_langchain_format(
                model_info["model_name"],
                model_info["supplier_name"],
                False, input
            )
            if mcp_tool_list:
                llm_pipeline.llm = llm_pipeline.llm.bind_tools([{
                    'name': tool['name'],
                    'description': tool['description'],
                    'input_schema': tool['inputSchema']
                } for tool in mcp_tool_list])
            for _ in range(5):
                try:
                    if model_info["supplier_name"] in ["Anthropic", "Google"]:
                        llm_aiter = llm_pipeline.astream_llm(llm_input)
                    else:
                        llm_aiter = llm_pipeline.astream_llm(llm_input, stream_usage=True)
                    while True:
                        try:
                            yield await asyncio.wait_for(anext(llm_aiter), timeout=120)
                        except StopAsyncIteration:
                            break
                    break
                except asyncio.TimeoutError:
                    pass
            else:
                raise Exception('Cannot connect to LLM after trying 5 times. Please check the network connection.')
        
        messages_copy = deepcopy(messages)
        messages_copy.replace_variables(input)
        model_data = {
            'model': llm_config,
            'messages': messages_copy.serialize(),
        }
        return model_data, ainvoke
    
    def extract_json_from_string(self, text: str) -> dict:
        """
        Extracts JSON content from a string, filtering out any extraneous content.

        Args:
            text (str): The string containing JSON content.

        Returns:
            dict: The extracted JSON content as a dictionary.
        """
        try:
            json_str = re.search(r'\{.*\}', text, re.DOTALL).group()
            return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            raise ValueError(f"No valid JSON content found in the string:\n{text}")

    def extract_uuid_from_string(self, text: str) -> str:
        """
        Extracts a UUID from a string, filtering out any extraneous content.

        Args:
            text (str): The string containing a UUID.

        Returns:
            str: The extracted UUID.
        """
        try:
            return re.search(r'[0-9a-fA-F\-]+', text).group()
        except AttributeError:
            raise ValueError("No valid UUID found in the string.")