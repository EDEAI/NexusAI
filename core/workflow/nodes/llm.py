import sys, json
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from typing import Any, Dict, List, Optional
from datetime import datetime
from langchain_core.documents import Document

from .base import ImportToKBBaseNode, LLMBaseNode
from ..variables import ObjectVariable, Variable
from ..context import Context
from ..recursive_task import RecursiveTaskCategory
from core.llm.prompt import Prompt, replace_prompt_with_context
from core.dataset import DatasetRetrieval
from core.database.models import Workflows, AppNodeExecutions
from languages import get_language_content
from log import Logger


logger = Logger.get_logger('celery-app')

class LLMNode(ImportToKBBaseNode, LLMBaseNode):
    """
    An LLMNode object is used to generate text using a language model.
    """
    
    def __init__(
        self,
        title: str,
        desc: str = "",
        input: Optional[ObjectVariable] = None,
        model_config_id: int = 0,
        prompt: Optional[Prompt] = None,
        retrieval_task_datasets: List[int] = [],
        requires_upload: bool = False,
        wait_for_all_predecessors: bool = False,
        task_splitting: bool = False,
        manual_confirmation: bool = False,
        import_to_knowledge_base: Dict[str, bool] = {},
        knowledge_base_mapping: Dict[str, Dict[str, int]] = {},
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None
    ):
        """
        Initializes an LLMNode object with typing enhancements and the ability to track the original node ID.
        """
        init_kwargs = {
            "type": "llm",
            "title": title,
            "desc": desc,
            "input": input,
            "model_config_id": model_config_id,
            "prompt": prompt,
            "retrieval_task_datasets": retrieval_task_datasets,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "task_splitting": task_splitting,
            "manual_confirmation": manual_confirmation,
            "import_to_knowledge_base": import_to_knowledge_base,
            "knowledge_base_mapping": knowledge_base_mapping,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(
        self,
        context: Context = None,
        workflow_id: int = 0,
        user_id: int = 0,
        type: int = 0,
        app_run_id: int = 0,
        node_exec_id: int = 0,
        edge_id: str = '',
        level: int = 0,
        task: Optional[Dict[str, RecursiveTaskCategory]] = None,
        correct_llm_output: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Runs the LLM node to generate text using the language model.
        """
        try:
            start_time = datetime.now()
                
            # Task splitting is disabled in current version. 2024-10-22
            self.data['task_splitting'] = False

            self.import_inputs_to_knowledge_base(
                app_run_id, node_exec_id,
                (
                    not correct_llm_output
                    # NOT running the node separately,
                    # which means running in the execution of the workflow
                    and app_run_id != 0
                    and self.data['import_to_knowledge_base'].get('input', False)
                )
            )
            
            prompt: Prompt = self.data["prompt"]
            file_list = None
            if context:
                file_list = replace_prompt_with_context(prompt, context)
            
            # Escape braces in the prompt
            if system_prompt := prompt.get_system():
                prompt.system.value = self.duplicate_braces(system_prompt)
            if user_prompt := prompt.get_user():
                prompt.user.value = self.duplicate_braces(user_prompt)
            if assistant_prompt := prompt.get_assistant():
                prompt.assistant.value = self.duplicate_braces(assistant_prompt)
                
            if self.data['task_splitting']:
                reply_requirement = get_language_content(
                    'llm_reply_requirement_with_task_splitting'
                )
                prompt.system.value = f'{prompt.system.value}\n{reply_requirement}'
            
            invoke_input = {'obligations': '', 'related_content': ''}
            if task:
                prompt_config = get_language_content("recursive_task_execute")
                task_prompt = Prompt(system=prompt_config["system"], user=prompt_config["user"])
                invoke_input['requirements_and_goals'] = prompt.get_system() + '\n' + prompt.get_user()
                invoke_input['parent_task'] = json.dumps(task['parent'].to_dict(exclude_subcategories=True) if task['parent'] else "", ensure_ascii=False)
                current_task_dict = task['current'].to_dict(first_level_only=True)
                child_task_dict = current_task_dict.pop('subcategories', [])
                child_task_names = [task['name'] for task in child_task_dict]
                
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
                        retrieval, _, _ = DatasetRetrieval.single_retrieve(self.data['retrieval_task_datasets'][0], 0, 0, workflow_id, app_run_id, user_id, type, previous_documents)
                    else:
                        retrieval, _, _ = DatasetRetrieval.multiple_retrieve(self.data['retrieval_task_datasets'], 0, 0, workflow_id, app_run_id, user_id, type, previous_documents)
                    retrieval_result: List[Document] = retrieval.invoke(current_task_dict['keywords'])
                    if retrieval_result:
                        previous_documents_results = DatasetRetrieval.get_full_documents(retrieval_result)
                        if previous_documents_results:
                            invoke_input['related_content'] = json.dumps(previous_documents_results, ensure_ascii=False)
                invoke_input['current_task'] = json.dumps(current_task_dict, ensure_ascii=False)
                invoke_input['child_tasks'] = json.dumps(child_task_names, ensure_ascii=False)
                self.data["prompt"] = task_prompt
            
            model_data, content, prompt_tokens, completion_tokens, total_tokens = self.invoke(
                app_run_id=app_run_id,
                edge_id=edge_id,
                context=context,
                input=invoke_input,
                file_list=file_list,
                correct_llm_output=correct_llm_output,
                return_json=kwargs.get('return_json', False)
            )
            if isinstance(content, (dict, list)):
                outputs = Variable(name="text", type="json", value=json.dumps(content, ensure_ascii=False))
            else:
                outputs = Variable(name="text", type="string", value=content)
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
            end_time = datetime.now()
            return_data = {
                'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                'model_data': model_data,
                'task_id': task['current'].id if task else None,
                'output_type' : 2,
                'outputs': outputs.to_dict(),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            }
            if self.data['input']:
                return_data['inputs'] = self.data['input'].to_dict()
            return {
                'status': 'success',
                'message': 'LLM node executed successfully.',
                'data': return_data
            }
        except Exception as e:
            logger.exception('ERROR!!')
            self.delete_documents_by_node_exec_id(node_exec_id)
            return {
                'status': 'failed',
                'message': str(e)
            }