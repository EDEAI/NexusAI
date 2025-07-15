import sys, json
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from datetime import datetime
from typing import Dict, Optional, Union, Any

from .base import ImportToKBBaseNode, LLMBaseNode
from ..recursive_task import create_recursive_task_category_from_dict
from ..variables import Variable, ArrayVariable, ObjectVariable, get_first_variable_value
from ..context import Context, replace_variable_value_with_context
from core.llm.prompt import Prompt
from languages import get_language_content
from log import Logger


logger = Logger.get_logger('celery-app')

class RecursiveTaskGenerationNode(ImportToKBBaseNode, LLMBaseNode):
    """
    A RecursiveTaskGenerationNode object is used to generate recursive tasks in a workflow.
    """
    
    def __init__(
        self,
        title: str,
        desc: str = "",
        input: Optional[Union[Variable, ArrayVariable, ObjectVariable]] = None,
        model_config_id: int = 0, 
        prompt: Optional[Prompt] = None,
        requires_upload: bool = False, 
        manual_confirmation: bool = False, 
        import_to_knowledge_base: Dict[str, bool] = {},
        knowledge_base_mapping: Dict[str, Dict[str, int]] = {},
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None,
        split_task_by_line: bool = False
    ):
        """
        Initializes a RecursiveTaskGenerationNode object with typing enhancements and the ability to track the original node ID.
        """
        init_kwargs = {
            "type": "recursive_task_generation",
            "title": title,
            "desc": desc,
            "input": input,
            "model_config_id": model_config_id,
            "prompt": prompt,
            "manual_confirmation": manual_confirmation,
            "import_to_knowledge_base": import_to_knowledge_base,
            "knowledge_base_mapping": knowledge_base_mapping,
            "flow_data": flow_data,
            "split_task_by_line": True  # Currently, only split by line is supported
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(
        self,
        context: Context,
        user_id: int = 0,
        app_run_id: int = 0,
        node_exec_id: int = 0,
        edge_id: str = '',
        level: int = 0,
        correct_llm_output: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = datetime.now()
            
            input = self.data['input']
            replace_variable_value_with_context(input, context)
            
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
            
            if self.data['split_task_by_line']:
                requirement_str: str = get_first_variable_value(input)
                requirement_list = []
                for requirement in requirement_str.split('\n'):
                    requirement = requirement.strip()
                    if requirement:
                        requirement_list.append(requirement)
                
                subcategories = []
                for index, requirement in enumerate(requirement_list):
                    subcategories.append({
                        'id': f'task-sub-{index}',
                        'name': f'{get_language_content("recursive_task_sub_task", user_id=user_id, append_ret_lang_prompt=False)} {index + 1}',
                        'description': '',
                        'task': requirement
                    })
                tasks = {
                    'id': 'task-root',
                    'name': get_language_content("recursive_task_root_task", user_id=user_id, append_ret_lang_prompt=False),
                    'description': '',
                    'keywords': '',
                    'task': get_language_content("recursive_task_root_task", user_id=user_id, append_ret_lang_prompt=False),
                    'subcategories': subcategories
                }
                
                model_data = None
                prompt_tokens = completion_tokens = total_tokens = 0
            else:
                invoke_input = {'requirement': get_first_variable_value(input)}
                if self.data["prompt"]:
                    invoke_input["task_generation_goals"] = self.duplicate_braces(self.data["prompt"].get_system())
                    
                prompt_config = get_language_content("recursive_task_generation")
                self.schema_key = "recursive_task_generation"
                self.data["prompt"] = Prompt(system=prompt_config["system"], user=prompt_config["user"])
                
                model_data, tasks, prompt_tokens, completion_tokens, total_tokens = self.invoke(
                    app_run_id=app_run_id, 
                    edge_id=edge_id,
                    context=context, 
                    input=invoke_input,
                    return_json=True,
                    correct_llm_output=correct_llm_output
                )
            
            recursive_task = create_recursive_task_category_from_dict(tasks)
            outputs = Variable(name="output", type="json", value=json.dumps(recursive_task.to_dict(), ensure_ascii=False))
            
            if (
                not self.data['manual_confirmation']
                # NOT running the node separately,
                # which means running in the execution of the workflow
                and app_run_id != 0
                and self.data['import_to_knowledge_base'].get('output', False)
            ):
                self.import_variables_to_knowledge_base(
                    outputs, self.data['knowledge_base_mapping'].get('output', {}),
                    app_run_id, node_exec_id, False
                )
            
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Recursive task generation node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input.to_dict(),
                    'model_data': model_data,
                    'output_type': 2,
                    'outputs': outputs.to_dict(),
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            self.delete_documents_by_node_exec_id(node_exec_id)
            return {
                'status': 'failed',
                'message': str(e)
            }