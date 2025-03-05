from datetime import datetime
from typing import Dict, Any, Optional
from copy import deepcopy
from . import Node
from ..variables import VariableTypes, ObjectVariable, validate_required_variable
from log import Logger

logger = Logger.get_logger('celery-app')

class ConstantVariableNode(Node):
    """
    A ConstantVariableNode object is used to define constant variables that can be reused in a workflow.
    This helps avoid the need to repeatedly input the same variables when running a workflow multiple times.
    """
    
    def __init__(
        self, 
        title: str, 
        desc: str = "", 
        input: Optional[VariableTypes] = None, 
        output: Optional[VariableTypes] = None,
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a ConstantVariableNode object.
        
        :param title: str, the title of the node.
        :param desc: str, a description of what the node does.
        :param input: VariableTypes, an instance containing input variables for the node.
        :param output: VariableTypes, an instance containing output constants.
        :param flow_data: Dict[str, Any], data required by the web.
        :param original_node_id: str, the original ID of the node if it's being recreated or duplicated.
        """
        init_kwargs = {
            "type": "constant_variable",
            "title": title,
            "desc": desc,
            "input": input,
            "output": output,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the node task - use input variables as constants in the workflow.
        """
        try:
            start_time = datetime.now()
            
            # Validate required inputs
            validate_required_variable(self.data["input"])
            
            # For constant variable node, the output is the same as the input
            input_data = self.data["input"].to_dict()
            
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Constant variable node completed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input_data,
                    'output_type': 1,
                    'outputs': input_data,  # Output is the same as input for constants
                }
            }
        except Exception as e:
            logger.exception('ERROR in ConstantVariableNode!!')
            return {
                'status': 'failed',
                'message': str(e)
            } 