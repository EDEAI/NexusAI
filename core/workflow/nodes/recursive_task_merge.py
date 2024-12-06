import sys, json
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from datetime import datetime
from typing import Dict, Optional, Any

from .base import ImportToKBBaseNode
from ..recursive_task import merge_recursive_task_categories
from ..variables import ArrayVariable, Variable
from ..context import Context, replace_variable_value_with_context
from log import Logger


logger = Logger.get_logger('celery-app')

class RecursiveTaskMergeNode(ImportToKBBaseNode):
    """
    A RecursiveTaskMergeNode object is used to merge recursive task data from multiple RecursiveTaskGenerationNode nodes.
    """
    
    def __init__(
        self,
        title: str,
        desc: str = "",
        input: Optional[ArrayVariable] = None,
        wait_for_all_predecessors: bool = True,
        manual_confirmation: bool = False, 
        import_to_knowledge_base: Dict[str, bool] = {},
        knowledge_base_mapping: Dict[str, Dict[str, int]] = {},
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a RecursiveTaskMergeNode object with typing enhancements and the ability to track the original node ID.
        """
        init_kwargs = {
            "type": "recursive_task_merge",
            "title": title,
            "desc": desc,
            "input": input,
            "wait_for_all_predecessors": wait_for_all_predecessors,
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
        context: Context,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            if kwargs.get('source_node_type') != 'recursive_task_generation':
                raise Exception('The source node type must be recursive_task_generation.')
            
            start_time = datetime.now()
            
            input = self.data['input']
            replace_variable_value_with_context(input, context)
            
            # Merge the collected task categories
            task_categories = [json.loads(node_output.value) for node_output in input.values]
            merged_category = merge_recursive_task_categories(task_categories)
            merged_category_json = json.dumps(merged_category.to_dict(), ensure_ascii=False)
            
            outputs = Variable(name="output", type="json", value=merged_category_json)
            
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Recursive task merge node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input.to_dict(),
                    'output_type': 2,
                    'outputs': outputs.to_dict()
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }