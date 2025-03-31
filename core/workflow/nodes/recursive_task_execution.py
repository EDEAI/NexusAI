import sys, json
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from .base import Nodes, ImportToKBBaseNode, LLMBaseNode
from ..variables import Variable, ArrayVariable, ObjectVariable, create_variable_from_dict, validate_required_variable, get_first_variable_value
from .agent import AgentNode
from .llm import LLMNode
from core.llm.prompt import Prompt
from ..recursive_task import RecursiveTaskCategory, create_recursive_task_category_from_dict
from ..context import Context, replace_variable_value_with_context
from core.database.models import Agents, AppNodeExecutions
from languages import get_language_content
from log import Logger

logger = Logger.get_logger('celery-app')

class RecursiveTaskExecutionNode(ImportToKBBaseNode, LLMBaseNode):
    """
    A RecursiveTaskExecutionNode object is used to execute recursive tasks in a workflow.
    """

    def __init__(
        self,
        title: str,
        desc: str = "",
        input: Optional[Union[Variable, ArrayVariable, ObjectVariable]] = None,
        model_config_id: int = 0,
        executor_list: Optional[Nodes] = None,
        prompt: Optional[Prompt] = None,
        requires_upload: bool = False, 
        manual_confirmation: bool = False,
        import_to_knowledge_base: Dict[str, bool] = {},
        knowledge_base_mapping: Dict[str, Dict[str, int]] = {},
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a RecursiveTaskExecutionNode object.
        """
        init_kwargs = {
            "type": "recursive_task_execution",
            "title": title,
            "desc": desc,
            "input": input,
            "model_config_id": model_config_id,
            "executor_list": executor_list,
            "prompt": prompt,
            "manual_confirmation": manual_confirmation,
            "import_to_knowledge_base": import_to_knowledge_base,
            "knowledge_base_mapping": knowledge_base_mapping,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def get_executor(self, executor_id: str) -> Optional[Union[AgentNode, LLMNode]]:
        """
        Get executor by ID.
        """
        for executor in self.data['executor_list']:
            if executor.id == executor_id:
                return executor
        return None
    
    def merge_task_data(self, recursive_task: RecursiveTaskCategory, app_run_id: int, level: int) -> List[str]:
        """
        Merge task data with executed task results.
        """
        executed_task_ids = []
        executed_task_results = AppNodeExecutions().get_all_task_execution_results(app_run_id, level, self.id)
        for task_item in executed_task_results:
            executed_task_id = task_item['task_id']
            executed_task_ids.append(executed_task_id)
            recursive_task.update_task(executed_task_id, get_first_variable_value(create_variable_from_dict(task_item['outputs'])))
        return executed_task_ids
        
    def run(
        self, 
        context: Context, 
        app_run_id: int = 0,
        node_exec_id: int = 0,
        edge_id: str = '',
        level: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = datetime.now()
            input = self.data['input']
            replace_variable_value_with_context(input, context)
            validate_required_variable(input)
            recursive_task = create_recursive_task_category_from_dict(json.loads(get_first_variable_value(input)))
            if not recursive_task:
                raise Exception("Task data not found.")
            
            executor_list = self.data['executor_list']
            if not executor_list:
                raise Exception("Executor list not found.")
            
            executed_task_ids = self.merge_task_data(recursive_task, app_run_id, level)
            
            task_data = recursive_task.get_next_task(executed_task_ids)
            
            if task_data:
                task_id = task_data['current'].id
                task_data['current'] = task_data['current'].to_dict(first_level_only=True)
                task_data['parent'] = task_data['parent'].to_dict(exclude_subcategories=True) if task_data['parent'] else None
                
                if len(executor_list.nodes) == 1:
                    executor_node = executor_list.nodes[0]
                    executor_id = executor_node.id
                else:
                    executor_prompt_dict = {}
                    agent_id_dict = {}
                    for executor in executor_list.nodes:
                        if isinstance(executor, AgentNode):
                            agent_id_dict[executor.id] = executor.data['agent_id']
                            executor_prompt_dict[executor.id] = {
                                'id': executor.id,
                                'name': executor.data['title'],
                                'description': executor.data['desc'],
                                'obligations': ""
                            }
                        elif isinstance(executor, LLMNode):
                            executor_prompt_dict[executor.id] = {
                                'id': executor.id,
                                'name': executor.data['title'],
                                'description': executor.data['desc'],
                                'obligations': executor.data['prompt'].get_system() + "\n" + executor.data['prompt'].get_user()
                            }
                    if agent_id_dict:
                        agents = Agents().select(
                            columns=['id', 'obligations'],
                            conditions=[{'column': 'id', 'op': 'in', 'value': list(agent_id_dict.values())}]
                        )
                        agent_obligation_dict = {agent['id']: agent['obligations'] for agent in agents}
                        for execuror_id, agent_id in agent_id_dict.items():
                            if agent_id in agent_obligation_dict:
                                executor_prompt_dict[execuror_id]['obligations'] = agent_obligation_dict[agent_id]
                                
                    invoke_input = {
                        'current_task': json.dumps(task_data['current'], ensure_ascii=False),
                        'parent_task': json.dumps(task_data['parent'], ensure_ascii=False) if task_data['parent'] else "",
                        'executors': json.dumps(list(executor_prompt_dict.values()), ensure_ascii=False)
                    }
                    if self.data["prompt"]:
                        invoke_input["executor_selection_requirements"] = self.duplicate_braces(self.data["prompt"].get_system())
                    
                    prompt_config = get_language_content("recursive_task_assign")
                    self.data["prompt"] = Prompt(system=prompt_config["system"], user=prompt_config["user"])
                    
                    model_data, executor_id, prompt_tokens, completion_tokens, total_tokens = self.invoke(
                        app_run_id=app_run_id, 
                        edge_id=edge_id,
                        context=context, 
                        input=invoke_input
                    )
                    logger.debug(f"""
                        Model data: {model_data}
                        Executor ID: {executor_id}
                        Prompt tokens: {prompt_tokens}
                        Completion tokens: {completion_tokens}
                        Total tokens: {total_tokens}
                    """)
                    executor_id = self.extract_uuid_from_string(executor_id)
                
                    executor_node = executor_list.get_node(executor_id)
                    if not executor_node:
                        raise Exception(f"Executor node with ID:{executor_id} not found. Available executors: {[executor_list.to_dict()]}")
                
                outputs = ObjectVariable(name="output")
                outputs.add_property(key="task", value=Variable(name="task", type="json", value=json.dumps(task_data, ensure_ascii=False)))
                outputs.add_property(key="executor", value=Variable(name="executor", type="string", value=executor_node.data['title']))
                
                return_data = {
                    'task_id': task_id,
                    'condition_id': executor_id
                }
                if len(executor_list.nodes) > 1:
                    return_data.update({
                        'model_data': model_data,
                        'prompt_tokens': prompt_tokens,
                        'completion_tokens': completion_tokens,
                        'total_tokens': total_tokens
                    })
            else:
                self.import_inputs_to_knowledge_base_and_get_file_list(
                    app_run_id, node_exec_id,
                    (
                        # NOT running the node separately,
                        # which means running in the execution of the workflow
                        app_run_id != 0
                        and self.data['import_to_knowledge_base'].get('input', False)
                    )
                )
            
                outputs = Variable(name="output", type="json", value=json.dumps(recursive_task.to_dict(), ensure_ascii=False))
                return_data = {}

                if (
                    # NOT running the node separately,
                    # which means running in the execution of the workflow
                    app_run_id != 0
                    and self.data['import_to_knowledge_base'].get('output', False)
                ):
                    executed_task_results = AppNodeExecutions().get_all_task_execution_results(app_run_id, level, self.id)
                    for task_item in executed_task_results:
                        self.delete_documents_by_node_exec_id(task_item['id'])
                    if not self.data['manual_confirmation']:
                        self.import_variables_to_knowledge_base(
                            outputs, self.data['knowledge_base_mapping'].get('output', {}),
                            app_run_id, node_exec_id, False
                        )
            
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Recursive task execution node executed successfully.',
                'data': {
                    'child_level': task_data['level'] if task_data else 0,
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input.to_dict(),
                    'output_type' : 1,
                    'outputs': outputs.to_dict(),
                    **return_data
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            self.delete_documents_by_node_exec_id(node_exec_id)
            return {
                'status': 'failed',
                'message': str(e)
            }