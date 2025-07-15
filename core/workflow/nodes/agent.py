import asyncio
import builtins
import json

from copy import deepcopy
from exceptiongroup import ExceptionGroup
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
from core.database.models import (
    Apps, AppNodeExecutions, AppRuns,
    AgentAbilities, AgentCallableItems, AgentDatasetRelation, Agents,
    Chatrooms, CustomTools, Users, Workflows
)
from core.dataset import DatasetRetrieval
from core.llm.prompt import Prompt, replace_prompt_with_context
from core.mcp.app_converter import convert_callable_items_to_mcp_tools
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

    def _get_agent_run_name(
        self,
        agent_run_type: int,
        user_id: int,
        workflow_id: int,
        chatroom_id: int,
        data_source_run_id: Optional[int]
    ) -> str:
        match agent_run_type:
            case 1:
                return get_language_content('agent_run_type_1', user_id)
            case 2:
                workflow = Workflows().get_workflow_app(workflow_id)
                return get_language_content('agent_run_type_2', user_id).format(app_name=workflow['name'])
            case 3:
                chatroom = Chatrooms().get_chatroom_by_id(chatroom_id)
                return get_language_content('agent_run_type_3', user_id).format(app_name=chatroom['name'])
            case 4:
                record = ChatroomDrivenRecords().get_data_by_data_source_run_id(data_source_run_id)
                chatroom = Chatrooms().get_chatroom_by_id(record['chatroom_id'])
                return get_language_content('agent_run_type_4', user_id).format(app_name=chatroom['name'])
            case _:
                raise Exception(f'Unknown agent run type: {agent_run_type}')

    def _prepare_prompt(
        self,
        agent: Dict[str, Any],
        workflow_id: int,
        workflow_run_id: int,
        user_id: int,
        type: int,
        node_exec_id: int,
        task: Optional[Dict[str, RecursiveTaskCategory]],
        retrieve: bool,
        callable_skills: List[Dict[str, Any]],
        callable_workflows: List[Dict[str, Any]],
        direct_output: bool = False,
        is_chat: bool = False
    ) -> Tuple[Optional[int], Dict[str, Any]]:
        agent_id = agent['id']
        input_ = {
            'id_': agent_id,
            'name': agent['name'],
            'description': agent['description'],
            'obligations': agent['obligations'],
            'team_members': get_language_content(
                'agent_team_members',
                append_ret_lang_prompt=False
            ).format(team_members=(
                json.dumps(self._get_team_members(user_id), ensure_ascii=False)
                if callable_workflows and any(workflow['need_confirm_nodes'] for workflow in callable_workflows) else ''
            )),
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
                    abilities_content_and_output_format = []
                    for ability in abilities:
                        actual_output_format = default_output_format if ability['output_format'] == 0 else ability['output_format']
                        if task:
                            actual_output_format = 2
                        abilities_content_and_output_format.append(
                            (
                                ability['id'],
                                ability['content'],
                                get_language_content(
                                    'agent_output_format_'
                                    f'{actual_output_format}'
                                    f'{"_md" if actual_output_format == 2 and is_chat else ""}',
                                    append_ret_lang_prompt=False
                                )
                            )
                        )
                    if direct_output:
                        system_prompt = get_language_content('agent_system_prompt_with_auto_match_ability_direct_output', uid=user_id)
                    else:
                        self.schema_key = 'agent_system_prompt_with_auto_match_ability'
                        system_prompt = get_language_content('agent_system_prompt_with_auto_match_ability', uid=user_id)
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
                    if task:
                        output_format = 2
                    abilities_content = '\n'.join(ability['content'] for ability in abilities)
                    system_prompt = get_language_content(
                        'agent_system_prompt_with_abilities',
                        uid=user_id
                    )
                    input_['abilities_content'] = abilities_content
                    input_['output_format'] = get_language_content(
                        f'agent_output_format_{output_format}'
                        f'{"_md" if output_format == 2 and is_chat else ""}',
                        append_ret_lang_prompt=False
                    )
                    if self.data['task_splitting']:
                        input_['reply_requirement'] = get_language_content(
                            'agent_reply_requirement_with_task_splitting_and_abilities',
                            append_ret_lang_prompt=False
                        )
            else:
                output_format = default_output_format
                if task:
                    output_format = 2
                system_prompt = get_language_content(
                    'agent_system_prompt_with_no_ability',
                    uid=user_id
                )
                input_['output_format'] = get_language_content(
                    f'agent_output_format_{output_format}'
                    f'{"_md" if output_format == 2 and is_chat else ""}',
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
            if task:
                output_format = 2
            system_prompt = get_language_content(
                'agent_system_prompt_with_abilities',
                uid=user_id
            )
            input_['abilities_content'] = ability['content']
            input_['output_format'] = get_language_content(
                f'agent_output_format_{output_format}'
                f'{"_md" if output_format == 2 and is_chat else ""}',
                append_ret_lang_prompt=False
            )
            if self.data['task_splitting']:
                input_['reply_requirement'] = get_language_content(
                    'agent_reply_requirement_with_task_splitting_and_abilities',
                    append_ret_lang_prompt=False
                )
        if direct_output and not task:
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
                    retrieval, _, _ = DatasetRetrieval.single_retrieve(self.data['retrieval_task_datasets'][0], 0, 0, workflow_id, workflow_run_id, user_id, type, previous_documents)
                else:
                    retrieval, _, _ = DatasetRetrieval.multiple_retrieve(self.data['retrieval_task_datasets'], 0, 0, workflow_id, workflow_run_id, user_id, type, previous_documents)
                retrieval_result: List[Document] = retrieval.invoke(current_task_dict['keywords'] if current_task_dict['keywords'] else current_task_dict['task'])
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
    
    def _get_team_members(self, user_id: int) -> List[Dict[str, Any]]:
        current_user = Users().get_user_by_id(user_id)
        team_members = []
        if current_user['team_id'] == 0:
            return team_members
        user_info_list = Users().select(
            columns=['id', 'nickname', 'email'],
            conditions=[
                {'column': 'team_id', 'value': current_user['team_id']},
                {'column': 'status', 'value': 1}
            ]
        )
        for user in user_info_list:
            if user['email']:
                member_info = {
                    'user_id': user['id'],
                    'nickname': user['nickname'],
                    'email': user['email']
                }
                team_members.append(member_info)
        return team_members
    
    def _get_callable_items(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        from core.workflow.graph import create_graph_from_dict
        
        callable_skills = []
        callable_workflows = []
        for callable_item in AgentCallableItems().get_callable_items_by_agent_id(self.data['agent_id']):
            match callable_item['item_type']:
                case 1:
                    skill = CustomTools().get_skill_by_app_id(callable_item['app_id'])
                    callable_skills.append(skill)
                case 2:
                    workflow = Workflows().get_workflow_by_app_id(callable_item['app_id'])
                    graph = create_graph_from_dict(workflow.pop('graph'))
                    input_variables = graph.nodes.nodes[0].data['input']
                    workflow['input_variables'] = input_variables.to_dict()
                    
                    need_confirm_nodes = []
                    for node in graph.nodes.nodes:
                        if node.data['type'] == 'human' or node.data.get("manual_confirmation", False):
                            node_name = node.data.get("title", "")
                            node_desc = node.data.get("desc", "")
                            need_confirm_nodes.append({'node_id': node.id, 'node_name': node_name, 'node_desc': node_desc})
                            if node.data['type'] == 'recursive_task_execution' and node.data.get('executor_list', None):
                                for child_node in node.data['executor_list'].nodes:
                                    need_confirm_nodes.append({
                                        'node_id': child_node.id,
                                        'node_name': f"{node_name}.{child_node.data.get('title', '')}",
                                        'node_desc': child_node.data.get('desc', '')
                                    })
                    workflow['need_confirm_nodes'] = need_confirm_nodes

                    callable_workflows.append(workflow)
        return callable_skills, callable_workflows
        
    def run(
        self,
        context: Context,
        workflow_id: int = 0,
        user_id: int = 0,
        app_id: int = 0,
        app_run_id: int = 0,
        type: int = 0,
        agent_run_type: int = 2,
        chatroom_id: int = 0,
        node_exec_id: int = 0,
        edge_id: str = '',
        level: int = 0,
        task: Optional[Dict[str, RecursiveTaskCategory]] = None,
        correct_llm_output: bool = False,
        data_source_run_id : Optional[int] = 0,
        override_rag_input: Optional[str] = None,
        override_dataset_id: Optional[int] = None,
        is_chat: bool = False,
        override_file_list: Optional[List[Union[int, str]]] = None,
        mcp_tool_list: Optional[List[Dict[str, Any]]] = None,
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
            agent_run_name = self._get_agent_run_name(
                agent_run_type=agent_run_type,
                user_id=user_id,
                workflow_id=workflow_id,
                chatroom_id=chatroom_id,
                data_source_run_id=data_source_run_id
            )
            agent_run_id = AppRuns().insert(
                {
                    # the local variable `app_id` is the APP ID of the workflow when `node_exec_id` is not 0
                    # and is the APP ID of the agent when `node_exec_id` is 0
                    'app_id': agent['app_id'],
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'type': type,
                    'agent_run_type': agent_run_type,
                    # 'name': f'Agent-{agent_id}_{now}',
                    'name': agent_run_name,
                    'inputs': self.data['input'].to_dict(),
                    'selected_ability_id': self.data['ability_id'],
                    'auto_match_ability': agent['auto_match_ability'],
                    'status': 2
                }
            )
            replace_variable_value_with_context(self.data['input'], context)

            # Temporarily disable variable validation of Agent node in current version. 2024-10-22
            # validate_required_variable(self.data['input'])

            assert self.data['prompt'].get_user(), get_language_content('agent_empty_prompt')

            # Task splitting is disabled in current version. 2024-10-22
            self.data['task_splitting'] = False
            
            self.import_inputs_to_knowledge_base(
                app_run_id, node_exec_id,
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
            
            file_list = replace_prompt_with_context(self.data['prompt'], context)
            if override_file_list:
                file_list = []
                for index, file_var_value in enumerate(override_file_list):
                    file_list.append(Variable(
                        name=f"file_{index}",
                        type="file",
                        sub_type="image",
                        value=file_var_value
                    ))
            
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'raw_user_prompt': self.data['prompt'].get_user()}
            )
            
            # RAG chain generation
            if override_dataset_id:
                datasets = [override_dataset_id]
            else:
                datasets = [
                    relation['dataset_id']
                    for relation in AgentDatasetRelation().get_relations_by_agent_id(agent_id)
                ]
            match len(datasets):
                case 0:
                    retrieval_chain, retrieval_token_counter = None, None
                case 1:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.single_retrieve(
                        datasets[0], agent_id, agent_run_id, workflow_id, app_run_id, user_id, type
                    )
                case _:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.multiple_retrieve(
                        datasets, agent_id, agent_run_id, workflow_id, app_run_id, user_id, type
                    )

            # Temporarily disabled MCP tool feature. 2025-05-13
            # callable_skills, callable_workflows = self._get_callable_items()
            callable_skills, callable_workflows = [], []
            
            # direct_output = bool(task) or is_chat  # Content output only (ability ID is omitted) for auto match ability & Force plain text output
            direct_output = False
            output_format, input_ = self._prepare_prompt(
                agent, workflow_id, app_run_id, user_id, type, node_exec_id, task, bool(datasets),
                callable_skills, callable_workflows,
                direct_output, is_chat
            )
            
            all_mcp_tools = []

            # Auto match ability
            #       -- Force JSON output -- return_json is True
            # Ability output format is JSON
            #       -- In a workflow: Force JSON output -- return_json is True
            #       -- Chat mode: JSON in Markdown format (text output) -- return_json is False
            # Ability output format is not JSON
            #       -- Text output -- return_json is False
            return_json = (output_format is None) or (output_format == 2 and not is_chat)
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
                agent_id=agent_id,
                mcp_tool_list=all_mcp_tools
            )
            model_data['tools'] = all_mcp_tools
            print(model_data)
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'model_data': model_data}
            )
            # Process the AI message
            ability_id = self.data['ability_id']
            default_output_format = agent['default_output_format']
            if output_format is None:  # Auto match ability
                try:
                    ability_id = int(ai_output['ability_id'])
                except:
                    ability_id = 0
                AppRuns().update(
                    {'column': 'id', 'value': agent_run_id},
                    {'matched_ability_id': ability_id}
                )
                if ability_id:
                    ability = AgentAbilities().get_ability_by_id(ability_id)
                    output_format = ability['output_format']
                    if output_format == 0:
                        output_format = default_output_format
                else:
                    output_format = default_output_format
                try:
                    ai_output = ai_output['output']
                except:
                    pass

            if not isinstance(ai_output, str):
                ai_output = json.dumps(ai_output, ensure_ascii=False)
                    
            if output_format == 2 and not is_chat:
                # Check if AI output is a JSON string
                try:
                    json.loads(ai_output)
                except json.JSONDecodeError:
                    raise Exception(f'AI output is not a valid JSON string:\n{ai_output}')
                
            if retrieval_token_counter:
                embedding_tokens = retrieval_token_counter['embedding']
                reranking_tokens = retrieval_token_counter['reranking']
            else:
                embedding_tokens, reranking_tokens = 0, 0
            if is_chat:
                chat_message_id = AgentChatMessages().insert({
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'ability_id': ability_id,
                    'message': ai_output,
                    'agent_run_id': agent_run_id,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                })
                chat_message_llm_return = 'chat_message_llm_return'
                datetime_now = datetime.now()
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
                        'ability_id': ability_id,
                        'message': ai_output
                    }
                }
                push_to_websocket_queue(data)
                logger_chat.info(f"Push results generated through AI:{user_id} agent_id:{agent_id} chat_message_id：{chat_message_id} message:{ai_output} status:{1} data:{data}")
            outputs = Variable(
                name="text",
                type="json" if output_format == 2 and not is_chat else "string",
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
                logger_chat.info(f"Push results generated through AI ERROR:{user_id} error:{str(e)} status:{4} data:{data}")

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
        agent_run_type: int = 2,
        chatroom_id: int = 0,
        node_exec_id: int = 0,
        edge_id: str = '',
        level: int = 0,
        task: Optional[Dict[str, RecursiveTaskCategory]] = None,
        correct_llm_output: bool = False,
        data_source_run_id : Optional[int] = 0,
        override_rag_input: Optional[str] = None,
        override_dataset_id: Optional[int] = None,
        override_file_list: Optional[List[Union[int, str]]] = None,
        mcp_tool_list: Optional[List[Dict[str, Any]]] = None,
        is_desktop: bool = False,
        **kwargs
    ) -> AsyncIterator[Union[AIMessageChunk, int]]:
        try:
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

            start_time = monotonic()
            now = datetime.now().replace(microsecond=0).isoformat(sep='_')
            agent_id = self.data['agent_id']
            agent = Agents().get_agent_by_id(agent_id)
            agent_run_name = self._get_agent_run_name(
                agent_run_type=agent_run_type,
                user_id=user_id,
                workflow_id=workflow_id,
                chatroom_id=chatroom_id,
                data_source_run_id=data_source_run_id
            )
            agent_run_id = AppRuns().insert(
                {
                    # the local variable `app_id` is the APP ID of the workflow when `node_exec_id` is not 0
                    # and is the APP ID of the agent when `node_exec_id` is 0
                    'app_id': agent['app_id'],
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'type': type,
                    'agent_run_type': agent_run_type,
                    # 'name': f'Agent-{agent_id}_{now}',
                    'name': agent_run_name,
                    'inputs': self.data['input'].to_dict(),
                    'selected_ability_id': self.data['ability_id'],
                    'auto_match_ability': agent['auto_match_ability'],
                    'status': 2
                }
            )
            yield agent_run_id
            
            replace_variable_value_with_context(self.data['input'], context)

            # Temporarily disable variable validation of Agent node in current version. 2024-10-22
            # validate_required_variable(self.data['input'])

            assert self.data['prompt'].get_user(), get_language_content('agent_empty_prompt')

            # Task splitting is disabled in current version. 2024-10-22
            self.data['task_splitting'] = False
            
            self.import_inputs_to_knowledge_base(
                app_run_id, node_exec_id,
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
            
            file_list = replace_prompt_with_context(self.data['prompt'], context)
            if override_file_list:
                file_list = []
                for index, file_var_value in enumerate(override_file_list):
                    file_list.append(Variable(
                        name=f"file_{index}",
                        type="file",
                        sub_type="image",
                        value=file_var_value
                    ))
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'raw_user_prompt': self.data['prompt'].get_user()}
            )
            
            # RAG chain generation
            if override_dataset_id:
                datasets = [override_dataset_id]
            else:
                datasets = [
                    relation['dataset_id']
                    for relation in AgentDatasetRelation().get_relations_by_agent_id(agent_id)
                ]
            match len(datasets):
                case 0:
                    retrieval_chain, retrieval_token_counter = None, None
                case 1:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.single_retrieve(
                        datasets[0], agent_id, agent_run_id, workflow_id, app_run_id, user_id, type
                    )
                case _:
                    retrieval_chain, _, retrieval_token_counter = DatasetRetrieval.multiple_retrieve(
                        datasets, agent_id, agent_run_id, workflow_id, app_run_id, user_id, type
                    )

            all_mcp_tools = []
            callable_skills, callable_workflows = self._get_callable_items()
            app_tools = convert_callable_items_to_mcp_tools(callable_skills, callable_workflows)
            all_mcp_tools.extend(app_tools)
            
            if is_desktop and mcp_tool_list:
                all_mcp_tools.extend(mcp_tool_list)
            
            _, input_ = self._prepare_prompt(
                agent, workflow_id, app_run_id, user_id, type, node_exec_id, task, bool(datasets),
                callable_skills, callable_workflows, True, True
            )
            model_data, ainvoke = self.get_ainvoke_func(
                app_run_id=app_run_id, 
                edge_id=edge_id,
                context=context,
                retrieval_chain=retrieval_chain,
                input=input_,
                file_list=file_list,
                return_json=False,
                correct_llm_output=correct_llm_output,
                override_rag_input=override_rag_input,
                mcp_tool_list=all_mcp_tools
            )

            full_chunk: Optional[AIMessageChunk] = None
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            async for chunk in ainvoke():
                full_chunk = chunk if full_chunk is None else full_chunk + chunk
                # Get token usage
                if usage_metadata := chunk.usage_metadata:
                    prompt_tokens += usage_metadata['input_tokens']
                    completion_tokens += usage_metadata['output_tokens']
                    total_tokens += usage_metadata['total_tokens']
                yield chunk
                
            if retrieval_token_counter:
                embedding_tokens = retrieval_token_counter['embedding']
                reranking_tokens = retrieval_token_counter['reranking']
            else:
                embedding_tokens, reranking_tokens = 0, 0

            model_data['tools'] = all_mcp_tools
            model_data['raw_output'] = full_chunk.content
            AppRuns().update(
                {'column': 'id', 'value': agent_run_id},
                {'model_data': model_data}
            )

            outputs = Variable(
                name="text",
                type="string" if builtins.type(full_chunk.content) == str else "json",
                value=(
                    full_chunk.content
                    if builtins.type(full_chunk.content) == str
                    else json.dumps(full_chunk.content, ensure_ascii=False)
                )
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
        