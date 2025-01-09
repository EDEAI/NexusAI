import json

from copy import deepcopy
from datetime import datetime
from time import monotonic
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from langchain_core.documents import Document
from langchain_core.messages import AIMessageChunk

from .base import CURRENT_NODE_ID, ImportToKBBaseNode, LLMBaseNode
from ..context import Context, replace_variable_value_with_context
from ..variables import ObjectVariable, Variable
from ..recursive_task import RecursiveTaskCategory
from core.database.models.chatroom_driven_records import ChatroomDrivenRecords
from core.database.models import Apps, AgentAbilities, AgentDatasetRelation, Agents, Workflows, AppRuns, AppNodeExecutions, Models
from core.dataset import DatasetRetrieval
from core.llm.messages import Messages
from core.llm.models import LLMPipeline
from core.llm.prompt import Prompt, replace_prompt_with_context
from languages import get_language_content
from log import Logger


logger = Logger.get_logger('celery-app')


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
            
            input_ = {'obligations': agent['obligations']}
            
            # Generate the system prompt based on the agent's abilities and output format
            sys_prompt_append_ret_lang_prompt = not bool(task)
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
                            'agent_system_prompt_with_auto_match_ability',
                            append_ret_lang_prompt=sys_prompt_append_ret_lang_prompt
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
                            append_ret_lang_prompt=sys_prompt_append_ret_lang_prompt
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
                            input_['reply_requirement'] = get_language_content(
                                'agent_reply_requirement_with_abilities',
                                append_ret_lang_prompt=False
                            )
                else:
                    output_format = default_output_format
                    system_prompt = get_language_content(
                        'agent_system_prompt_with_no_ability',
                        append_ret_lang_prompt=sys_prompt_append_ret_lang_prompt
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
                        input_['reply_requirement'] = get_language_content(
                            'agent_reply_requirement_with_no_ability',
                            append_ret_lang_prompt=False
                        )
            else:
                ability = AgentAbilities().get_ability_by_id(ability_id)
                output_format = ability['output_format']
                if output_format == 0:
                    output_format = default_output_format
                system_prompt = get_language_content(
                    'agent_system_prompt_with_abilities',
                    append_ret_lang_prompt=sys_prompt_append_ret_lang_prompt
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
                else:
                    input_['reply_requirement'] = get_language_content(
                        'agent_reply_requirement_with_abilities',
                        append_ret_lang_prompt=False
                    )
                
            replace_prompt_with_context(self.data['prompt'], context)
            user_prompt = self.data['prompt'].get_user()
            
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
                    
            # Create and invoke the LLM pipeline
            if retrieval_chain:
                self.data['prompt'] = Prompt(
                    system=system_prompt,
                    user=get_language_content(
                        'agent_user_prompt_with_retrieved_docs',
                        append_ret_lang_prompt=False
                    )
                )
                input_['user_prompt'] = user_prompt
            else:
                self.data['prompt'] = Prompt(
                    system=system_prompt,
                    user=self.duplicate_braces(user_prompt)
                )
            requirements_and_goals = None
            requirements_and_goals_kwargs = None
            if task:
                prompt_config = get_language_content("recursive_task_execute")
                task_prompt = Prompt(system=prompt_config["system"], user=prompt_config["user"])
                
                current_task_dict = task['current'].to_dict(first_level_only=True)
                child_task_dict = current_task_dict.pop('subcategories', [])
                child_task_names = [task['name'] for task in child_task_dict]
                
                invoke_input = {
                    'obligations': self.data['prompt'].get_system().format(**input_),
                    'current_task': json.dumps(current_task_dict, ensure_ascii=False),
                    'parent_task': json.dumps(task['parent'].to_dict(exclude_subcategories=True) if task['parent'] else "", ensure_ascii=False),
                    'child_tasks': json.dumps(child_task_names, ensure_ascii=False),
                    'related_content': ''
                }
                requirements_and_goals = self.data['prompt'].get_user()
                requirements_and_goals_kwargs = input_
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
                            invoke_input['related_content'] = json.dumps(previous_documents_results, ensure_ascii=False)
                self.data["prompt"] = task_prompt
                input_ = invoke_input
                if retrieval_chain:
                    input_['user_prompt'] = user_prompt
            
            model_data, ai_content, prompt_tokens, completion_tokens, total_tokens = self.invoke(
                app_run_id=app_run_id, 
                edge_id=edge_id,
                context=context,
                retrieval_chain=retrieval_chain,
                input=input_,
                file_list=file_list,
                return_json=True,
                correct_llm_output=correct_llm_output,
                requirements_and_goals=requirements_and_goals,
                requirements_and_goals_kwargs=requirements_and_goals_kwargs
            )
            print(model_data)
            # Process the AI message
            if output_format is None:
                ability_id = ai_content['ability_id']
                if ability_id:
                    ability = AgentAbilities().get_ability_by_id(ability_id)
                    output_format = ability['output_format']
                    if output_format == 0:
                        output_format = default_output_format
                else:
                    output_format = default_output_format
                    
            ai_output = ai_content['output']
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
            return {
                'status': 'failed',
                'message': str(e)
            }
    
    async def run_in_chatroom(self, user_id: int = 0) -> AsyncIterator[AIMessageChunk]:
        agent_id = self.data['agent_id']
        agent = Agents().get_agent_by_id(agent_id)
        model_config_id = agent['model_config_id']
        model_info = Models().get_model_by_config_id(model_config_id)
        llm_config = {**model_info['supplier_config'], **model_info['model_config']}
        llm_pipeline = LLMPipeline(supplier=model_info['supplier_name'], config=llm_config)
        
        input_messages = Messages()
        input_messages.add_prompt(
            Prompt(
                system=get_language_content('chatroom_agent_system', user_id),
                user=self.data['prompt'].get_user()
            )
        )
        input_ = [(role, message.value) for role, message in input_messages.messages]
        
        async for chunk in llm_pipeline.llm.astream(
            input_,
            stream_usage=True
        ):
            yield chunk
        