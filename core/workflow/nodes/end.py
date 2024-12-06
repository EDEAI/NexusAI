from typing import Dict, Any, Optional
from datetime import datetime
from . import Node
from ..variables import VariableTypes
from ..context import Context, replace_variable_value_with_context
from log import Logger


logger = Logger.get_logger('celery-app')

class EndNode(Node):
    """
    An EndNode object is used to mark the end of the workflow.
    """
    
    def __init__(
        self, 
        title: str, 
        desc: str = "", 
        output: Optional[VariableTypes] = None, 
        wait_for_all_predecessors: bool = True,
        manual_confirmation: bool = False, 
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes an EndNode object.
        """
        init_kwargs = {
            "type": "end",
            "title": title,
            "desc": desc,
            "output": output,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "manual_confirmation": manual_confirmation,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
    
    def run(self, context: Context, **kwargs) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = datetime.now()
            replace_variable_value_with_context(self.data['output'], context)
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Workflow execution successfully completed.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'output_type' : 1,
                    'outputs': self.data['output'].to_dict(),
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }