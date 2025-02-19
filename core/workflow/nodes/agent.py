import asyncio
import json

from copy import deepcopy
from datetime import datetime
from time import monotonic
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple, Union
from langchain_core.documents import Document
from langchain_core.messages import AIMessageChunk

from .base import CURRENT_NODE_ID, ImportToKBBaseNode, LLMBaseNode
from ..context import Context, replace_variable_value_with_context
from ..variables import ObjectVariable, Variable
from ..recursive_task import RecursiveTaskCategory
from core.database.models.chatroom_driven_records import ChatroomDrivenRecords
from core.database.models.agent_chat_messages import AgentChatMessages
from core.database.models import Apps, AgentAbilities, AgentDatasetRelation, Agents, Workflows, AppRuns, AppNodeExecutions, Models
from core.dataset import DatasetRetrieval
from core.llm.messages import Messages
from core.llm.models import LLMPipeline
from core.llm.prompt import Prompt, replace_prompt_with_context
from languages import get_language_content
from log import Logger
from core.helper import push_to_websocket_queue


logger = Logger.get_logger('celery-app')
logger_chat = Logger.get_logger('agent-chat-llm-return')


class AgentNode(ImportToKBBaseNode, LLMBaseNode):
    """
    An AgentNode object is used to integrate external agents into the workflow.
    """
    
    def __init__(
        self,
        title: str,
        desc: str = "",
        input: Optional[ObjectVariable] = None,
        agent_id: int = 0,
        ability_id: int = 0,
        prompt: Optional[Prompt] = None,
        retrieval_task_datasets: List[int] = [],
        wait_for_all_predecessors: bool = False,
        task_splitting: bool = False,
        manual_confirmation: bool = False,
        import_to_knowledge_base: Dict[str, bool] = {},
        knowledge_base_mapping: Dict[str, Dict[str, Union[int, Dict[str, int]]]] = {},
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None,
        data_source_run_id : Optional[int] = 0
    ):
        """
        Initializes an AgentNode object with the ability to track the original node ID.
        """
        init_kwargs = {
            "type": "agent",
            "title": title,
            "desc": desc,
            "input": input,
            "agent_id": agent_id,
            "ability_id": ability_id,
            "prompt": prompt,
            "retrieval_task_datasets": retrieval_task_datasets,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "task_splitting": task_splitting,
            "manual_confirmation": manual_confirmation,
            "import_to_knowledge_base": import_to_knowledge_base,
            "knowledge_base_mapping": knowledge_base_mapping,
            "flow_data": flow_data,
            "data_source_run_id": data_source_run_id
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)

    def validate(self):
        agent_id = self.data['agent_id']
        agent = Agents().get_agent_by_id(agent_id)
        assert agent['obligations'], get_language_content('agent_empty_obligation')
        assert agent['model_config_id'], get_language_content('agent_empty_llm_model')
        abilities = AgentAbilities().get_abilities_by_agent_id(agent_id)
        for ability in abilities:
            assert ability['content'], get_language_content('agent_empty_ability')

    def _prepare_prompt(
        self,
        agent: Dict[str, Any],
        workflow_id: int,
        user_id: int,
        type: int,
        node_exec_id: int,
        task: Optional[Dict[str, RecursiveTaskCategory]],
        retrieve: bool,
        direct_output: bool = False
    ) -> Tuple[Optional[int], Dict[str, Any]]:
        agent_id = agent['id']
        input_ = {
            'id_': agent_id,
            'name': agent['name'],
            'description': agent['description'],
            'obligations': agent['obligations'],
            'retrieved_docs_format': '',
            'reply_requirement': '',
        }
        
        # Generate the system prompt based on the agent's abilities and output format
        ability_id = self.data['ability_id']
        default_output_format = agent['default_output_format']
        if ability_id == 0:
            abilities = AgentAbilities().get_abilities_by_agent_id(agent_id)
            if abilities:
                if agent['auto_match_ability']:
                    output_format = None
                    abilities_content_and_output_format = [
                        (
                            ability['id'],
                            ability['content'],
                            get_language_content(
                                'agent_output_format_'
                                f'{default_output_format if ability["output_format"] == 0 else ability["output_format"]}',
                                append_ret_lang_prompt=False
                            )
                        )
                        for ability in abilities
                    ]
                    system_prompt = get_language_content(
                        (
                            'agent_system_prompt_with_auto_match_ability_direct_output'
                            if direct_output
                            else 'agent_system_prompt_with_auto_match_ability'
                        ),
                        uid=user_id
                    )
                    input_['abilities_content_and_output_format'] = abilities_content_and_output_format
                    if self.data['task_splitting']:
                        input_['reply_requirement'] = get_language_content(
                            'agent_reply_requirement_with_task_splitting_and_auto_match_ability',
                            append_ret_lang_prompt=False
                        )
                    else:
                        input_['reply_requirement'] = get_language_content(
                            'agent_reply_requirement_with_auto_match_ability',
                            append_ret_lang_prompt=False
                        )
                else:
                    output_format = default_output_format
                    abilities_content = '\n'.join(ability['content'] for ability in abilities)
                    system_prompt = get_language_content(
                        'agent_system_prompt_with_abilities',
                        uid=user_id
                    )
                    input_['abilities_content'] = abilities_content
                    input_['output_format'] = get_language_content(
                        f'agent_output_format_{output_format}',
                        append_ret_lang_prompt=False
                    )
                    if self.data['task_splitting']:
                        input_['reply_requirement'] = get_language_content(
                            'agent_reply_requirement_with_task_splitting_and_abilities',
                            append_ret_lang_prompt=False
                        )
            else:
                output_format = default_output_format
                system_prompt = get_language_content(
                    'agent_system_prompt_with_no_ability',
                    uid=user_id
                )
                input_['output_format'] = get_language_content(
                    f'agent_output_format_{output_format}',
                    append_ret_lang_prompt=False
                )
                if self.data['task_splitting']:
                    input_['reply_requirement'] = get_language_content(
                        'agent_reply_requirement_with_task_splitting_and_no_ability',
                        append_ret_lang_prompt=False
                    )
        else:
            ability = AgentAbilities().get_ability_by_id(ability_id)
            output_format = ability['output_format']
            if output_format == 0:
                output_format = default_output_format
            system_prompt = get_language_content(
                'agent_system_prompt_with_abilities',
                uid=user_id
            )
            input_['abilities_content'] = ability['content']
            input_['output_format'] = get_language_content(
                f'agent_output_format_{output_format}',
                append_ret_lang_prompt=False
            )
            if self.data['task_splitting']:
                input_['reply_requirement'] = get_language_content(
                    'agent_reply_requirement_with_task_splitting_and_abilities',
                    append_ret_lang_prompt=False
                )
        if direct_output:
            output_format = 1
            
        user_prompt = self.data['prompt'].get_user()
        
                
        # Create and invoke the LLM pipeline
        if retrieve:
            input_['retrieved_docs_format'] = get_language_content(
                'agent_retrieved_docs_format',
                append_ret_lang_prompt=False
            )
            self.data['prompt'] = Prompt(
                system=system_prompt,
                user=get_language_content(
                    'agent_user_prompt_with_retrieved_docs',
                    append_ret_lang_prompt=False
                )
            )
        else:
            self.data['prompt'] = Prompt(
                system=system_prompt,
                user=get_language_content(
                    'agent_user_prompt',
                    append_ret_lang_prompt=False
                )
            )
        
        if task:
            current_task_dict = task['current'].to_dict(first_level_only=True)
            child_task_dict = current_task_dict.pop('subcategories', [])
            child_task_names = [task['name'] for task in child_task_dict]
            
            user_subprompt_kwargs = {
                'requirements_and_goals': user_prompt,
                'current_task': json.dumps(current_task_dict, ensure_ascii=False),
                'parent_task': json.dumps(task['parent'].to_dict(exclude_subcategories=True) if task['parent'] else "", ensure_ascii=False),
                'child_tasks': json.dumps(child_task_names, ensure_ascii=False),
                'related_content': ''
            }
            if self.data['retrieval_task_datasets']:
                workflow = Workflows().get_workflow_app(workflow_id)
                if not workflow:
                    raise Exception('Workflow not found.')
                source_node_execution, previous_executions = AppNodeExecutions().get_previous_task_executions(node_exec_id)
                previous_documents = []
                if source_node_execution:
                    previous_documents.append(f"{workflow['name']}-{source_node_execution['node_name']}-output-{source_node_execution['id']}")
                for task_execution in previous_executions:
                    previous_documents.append(f"{workflow['name']}-{task_execution['node_name']}-{task_execution['task_id']}-{task_execution['id']}")
                if len(self.data['retrieval_task_datasets']) == 1:
                    retrieval, _, _ = DatasetRetrieval.single_retrieve(self.data['retrieval_task_datasets'][0], 0, workflow_id, user_id, type, previous_documents)
                else:
                    retrieval, _, _ = DatasetRetrieval.multiple_retrieve(self.data['retrieval_task_datasets'], 0, workflow_id, user_id, type, previous_documents)
                retrieval_result: List[Document] = retrieval.invoke(current_task_dict['keywords'])
                if retrieval_result:
                    previous_documents_results = DatasetRetrieval.get_full_documents(retrieval_result)
                    if previous_documents_results:
                        user_subprompt_kwargs['related_content'] = json.dumps(previous_documents_results, ensure_ascii=False)
            user_prompt = get_language_content(
                "recursive_task_execute_agent_user_subprompt",
                user_id,
                append_ret_lang_prompt=False
            ).format(**user_subprompt_kwargs)

        input_['user_prompt'] = user_prompt

        return output_format, input_
        
    def run(
        self,
        context: Context,
        workflow_id: int = 0,
        user_id: int = 0,
        app_id: int = 0,
        app_run_id: int = 0,
        type: int = 0,
        node_exec_id: int = 0,
        edge_id: str = '',
        level: int = 0,
        task: Optional[Dict[str, RecursiveTaskCategory]] = None,
        correct_llm_output: bool = False,
        data_source_run_id : Optional[int] = 0,
        is_chat: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes the agent node.
        """
        try:
            start_time = monotonic()
            now = datetime.now().replace(microsecond=0).isoformat(sep='_')
            agent_id = self.data['agent_id']
            agent = Agents().get_agent_by_id(agent_id)
            agent_run_id = AppRuns().insert(
                {
                    # the local variable `app_id` is the APP ID of the workflow when `node_exec_id` is not 0
                    # and is the APP ID of the agent when `node_exec_id` is 0
                    'app_id': agent['app_id'],
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'type': type,
                    'name': f'Agent-{agent_id}_{now}',
                    'inputs': self.data['input'].to_dict(),
                    'status': 2
                }
            )
            replace_variable_value_with_context(self.data['input'], context)

            # Temporarily disable variable validation of Agent node in current version. 2024-10-22
            # validate_required_variable(self.data['input'])

            assert self.data['prompt'].get_user(), get_language_content('agent_empty_prompt')

            # Task splitting is disabled in current version. 2024-10-22
            self.data['task_splitting'] = False
            
            file_list = self.import_inputs_to_knowledge_base_and_get_file_list(
                app_run_id, node_exec_id, agent['allow_upload_file'],
                (
                    not correct_llm_output
                    # NOT running the app separately
                    # and NOT running the node separately,
                    # which means running in the execution of the workflow
                    and node_exec_id != 0
                    and app_run_id != 0
                    and self.data['import_to_knowledge_base'].get('input', False)
                )
            )
            
            # Get the agent and app information
            self.data['model_config_id'] = agent['model_config_id']
            Apps().increment_execution_times(agent['app_id'])
                    
            current_node = deepcopy(self)
            current_node.id = CURRENT_NODE_ID
            context.add_node(level, current_node)
            
            replace_prompt_with_context(self.data['prompt'], context)
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'raw_user_prompt': self.data['prompt'].get_user()}
            )
            
            # RAG chain generation
            datasets = [
                relation['dataset_id']
                for relation in AgentDatasetRelation().get_relations_by_agent_id(agent_id)
            ]
            match len(datasets):
                case 0:
                    retrieval_chain, retrieval_token_counter = None, None
                case 1:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.single_retrieve(
                        datasets[0], agent_id, workflow_id, user_id, type
                    )
                case _:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.multiple_retrieve(
                        datasets, agent_id, workflow_id, user_id, type
                    )
            
            direct_output = bool(task)  # Content output only (ability ID is omitted) for auto match ability & Force plain text output
            output_format, input_ = self._prepare_prompt(
                agent, workflow_id, user_id, type, node_exec_id, task, bool(datasets), direct_output
            )
            override_rag_input = kwargs.get('override_rag_input')
            return_json = output_format in [None, 2]  # Auto match ability or force JSON output
            model_data, ai_output, prompt_tokens, completion_tokens, total_tokens = self.invoke(
                app_run_id=app_run_id, 
                edge_id=edge_id,
                context=context,
                retrieval_chain=retrieval_chain,
                input=input_,
                file_list=file_list,
                return_json=return_json,
                correct_llm_output=correct_llm_output,
                override_rag_input=override_rag_input,
                is_chat=is_chat,
                user_id=user_id,
                agent_id=agent_id
            )
            print(model_data)
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'model_data': model_data}
            )
            # Process the AI message
            default_output_format = agent['default_output_format']
            if output_format is None:  # Auto match ability
                ability_id = ai_output['ability_id']
                ai_output = ai_output['output']
                if ability_id:
                    ability = AgentAbilities().get_ability_by_id(ability_id)
                    output_format = ability['output_format']
                    if output_format == 0:
                        output_format = default_output_format
                else:
                    output_format = default_output_format
                    
            if output_format == 2:
                if isinstance(ai_output, str):
                    # Check if AI output is a JSON string
                    try:
                        json.loads(ai_output)
                    except json.JSONDecodeError:
                        raise Exception(f'AI output is not a valid JSON string:\n{ai_output}')
                else:
                    ai_output = json.dumps(ai_output, ensure_ascii=False)
                
            if retrieval_token_counter:
                embedding_tokens = retrieval_token_counter['embedding']
                reranking_tokens = retrieval_token_counter['reranking']
            else:
                embedding_tokens, reranking_tokens = 0, 0
            if is_chat:
                chat_message_id = AgentChatMessages().insert({
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'message': ai_output,
                    'agent_run_id': agent_run_id,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                })
                chat_message_llm_return = 'chat_message_llm_return'
                datetime_now = datetime.now()
                json_data = json.dumps(ai_output, ensure_ascii=False)
                data = {
                    'user_id': user_id,
                    'type': chat_message_llm_return,
                    'data': {
                        'message_id': chat_message_id,
                        'status': 1,
                        'error': "",
                        'prompt_tokens': prompt_tokens,
                        'completion_tokens': completion_tokens,
                        'total_tokens': total_tokens,
                        'created_time': datetime_now,
                        'finished_time': datetime_now,
                        'user_id': user_id,
                        'agent_id': agent_id,
                        'message': json_data
                    }
                }
                push_to_websocket_queue(data)
                logger_chat.info(f"Push results generated through AI:{user_id} agent_id:{agent_id} chat_message_id：{chat_message_id} message:{ai_output} status:{1} data:{data}")
            outputs = Variable(
                name="text",
                type="json" if output_format == 2 else "string",
                value=ai_output
            )
            if (
                not self.data['manual_confirmation']
                # NOT running the app separately
                # and NOT running the node separately,
                # which means running in the execution of the workflow
                and node_exec_id != 0 and app_run_id != 0
                and self.data['import_to_knowledge_base'].get('output', False)
            ):
                self.import_variables_to_knowledge_base(
                    outputs, self.data['knowledge_base_mapping'].get('output', {}),
                    app_run_id, node_exec_id, False, task['current'].id if task else None
                )
            elapsed_time = monotonic() - start_time
            outputs = outputs.to_dict()
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {
                    'status': 3,
                    'outputs': outputs,
                    'elapsed_time': elapsed_time,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'embedding_tokens': embedding_tokens,
                    'reranking_tokens': reranking_tokens,
                    'finished_time': datetime.now()
                }
            )
            if data_source_run_id > 0:
                chatroomdriven_info = ChatroomDrivenRecords().get_data_by_data_source_run_id(data_source_run_id)
                if chatroomdriven_info:
                    ChatroomDrivenRecords().update_data_driven_run_id(chatroomdriven_info['id'],data_source_run_id, agent_run_id)
            return {
                'status': 'success',
                'message': 'Agent node executed successfully.',
                'data': {
                    'elapsed_time': elapsed_time,
                    'model_data': model_data,
                    'task_id': task['current'].id if task else None,
                    'inputs':self.data['input'].to_dict(),
                    'output_type': 2,
                    'outputs': outputs,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'embedding_tokens': embedding_tokens,
                    'reranking_tokens': reranking_tokens
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            if 'agent_run_id' in locals():
                AppRuns().update(
                    {'column': 'id', 'value': agent_run_id},
                    {
                        'status': 4,
                        'error': str(e)
                    }
                )
            self.delete_documents_by_node_exec_id(node_exec_id)

            if is_chat:
                chat_message_llm_return = 'chat_message_llm_return'
                message_error = str(e)
                datetime_now = datetime.now()
                data = {
                    'user_id': user_id,
                    'type': chat_message_llm_return,
                    'data': {
                        'message_id': '',
                        'status': 0,
                        'error': message_error,
                        'prompt_tokens': '',
                        'completion_tokens': '',
                        'total_tokens': '',
                        'created_time': datetime_now,
                        'finished_time': datetime_now
                    }
                }
                push_to_websocket_queue(data)
                logger_chat.info("----------------------------------------------------------------------------")
                logger_chat.exception(f"Push results generated through AI ERROR:{user_id} error:{str(e)} status:{4} data:{data}")
                logger_chat.info("----------------------------------------------------------------------------")

            return {
                'status': 'failed',
                'message': str(e)
            }
    
    async def run_in_chatroom(
        self,
        context: Context,
        workflow_id: int = 0,
        user_id: int = 0,
        app_id: int = 0,
        app_run_id: int = 0,
        type: int = 0,
        node_exec_id: int = 0,
        edge_id: str = '',
        level: int = 0,
        task: Optional[Dict[str, RecursiveTaskCategory]] = None,
        correct_llm_output: bool = False,
        data_source_run_id : Optional[int] = 0,
        **kwargs
    ) -> AsyncIterator[AIMessageChunk]:
        try:
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

            start_time = monotonic()
            now = datetime.now().replace(microsecond=0).isoformat(sep='_')
            agent_id = self.data['agent_id']
            agent = Agents().get_agent_by_id(agent_id)
            agent_run_id = AppRuns().insert(
                {
                    # the local variable `app_id` is the APP ID of the workflow when `node_exec_id` is not 0
                    # and is the APP ID of the agent when `node_exec_id` is 0
                    'app_id': agent['app_id'],
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'type': type,
                    'name': f'Agent-{agent_id}_{now}',
                    'inputs': self.data['input'].to_dict(),
                    'status': 2
                }
            )
            replace_variable_value_with_context(self.data['input'], context)

            # Temporarily disable variable validation of Agent node in current version. 2024-10-22
            # validate_required_variable(self.data['input'])

            assert self.data['prompt'].get_user(), get_language_content('agent_empty_prompt')

            # Task splitting is disabled in current version. 2024-10-22
            self.data['task_splitting'] = False
            
            file_list = self.import_inputs_to_knowledge_base_and_get_file_list(
                app_run_id, node_exec_id, agent['allow_upload_file'],
                (
                    not correct_llm_output
                    # NOT running the app separately
                    # and NOT running the node separately,
                    # which means running in the execution of the workflow
                    and node_exec_id != 0
                    and app_run_id != 0
                    and self.data['import_to_knowledge_base'].get('input', False)
                )
            )
            
            # Get the agent and app information
            self.data['model_config_id'] = agent['model_config_id']
            Apps().increment_execution_times(agent['app_id'])
                    
            current_node = deepcopy(self)
            current_node.id = CURRENT_NODE_ID
            context.add_node(level, current_node)
            
            replace_prompt_with_context(self.data['prompt'], context)
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'raw_user_prompt': self.data['prompt'].get_user()}
            )
            
            # RAG chain generation
            datasets = [
                relation['dataset_id']
                for relation in AgentDatasetRelation().get_relations_by_agent_id(agent_id)
            ]
            match len(datasets):
                case 0:
                    retrieval_chain, retrieval_token_counter = None, None
                case 1:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.single_retrieve(
                        datasets[0], agent_id, workflow_id, user_id, type
                    )
                case _:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.multiple_retrieve(
                        datasets, agent_id, workflow_id, user_id, type
                    )
            
            _, input_ = self._prepare_prompt(
                agent, workflow_id, user_id, type, node_exec_id, task, bool(datasets), True
            )
            override_rag_input = kwargs.get('override_rag_input')
            model_data, ainvoke = self.get_ainvoke_func(
                app_run_id=app_run_id, 
                edge_id=edge_id,
                context=context,
                retrieval_chain=retrieval_chain,
                input=input_,
                file_list=file_list,
                return_json=False,
                correct_llm_output=correct_llm_output,
                override_rag_input=override_rag_input
            )

            full_chunk: Optional[AIMessageChunk] = None
            async for chunk in ainvoke():
                full_chunk = chunk if full_chunk is None else full_chunk + chunk
                # Get token usage
                if usage_metadata := chunk.usage_metadata:
                    prompt_tokens = usage_metadata['input_tokens']
                    completion_tokens = usage_metadata['output_tokens']
                    total_tokens = usage_metadata['total_tokens']
                yield chunk
                
            if retrieval_token_counter:
                embedding_tokens = retrieval_token_counter['embedding']
                reranking_tokens = retrieval_token_counter['reranking']
            else:
                embedding_tokens, reranking_tokens = 0, 0

            model_data['raw_output'] = full_chunk.content
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'model_data': model_data}
            )

            outputs = Variable(
                name="text",
                type="string",
                value=full_chunk.content
            )
            if (
                not self.data['manual_confirmation']
                # NOT running the app separately
                # and NOT running the node separately,
                # which means running in the execution of the workflow
                and node_exec_id != 0 and app_run_id != 0
                and self.data['import_to_knowledge_base'].get('output', False)
            ):
                self.import_variables_to_knowledge_base(
                    outputs, self.data['knowledge_base_mapping'].get('output', {}),
                    app_run_id, node_exec_id, False, task['current'].id if task else None
                )
            elapsed_time = monotonic() - start_time
            outputs = outputs.to_dict()
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {
                    'status': 3,
                    'outputs': outputs,
                    'elapsed_time': elapsed_time,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'embedding_tokens': embedding_tokens,
                    'reranking_tokens': reranking_tokens,
                    'finished_time': datetime.now()
                }
            )
            if data_source_run_id > 0:
                chatroomdriven_info = ChatroomDrivenRecords().get_data_by_data_source_run_id(data_source_run_id)
                if chatroomdriven_info:
                    ChatroomDrivenRecords().update_data_driven_run_id(chatroomdriven_info['id'],data_source_run_id, agent_run_id)
        except Exception as e:
            logger.exception('ERROR!!')
            if 'agent_run_id' in locals():
                AppRuns().update(
                    {'column': 'id', 'value': agent_run_id},
                    {
                        'status': 4,
                        'error': str(e)
                    }
                )
            self.delete_documents_by_node_exec_id(node_exec_id)
            raise
        