import re
from datetime import datetime
from typing import Dict, Any, Optional
from copy import deepcopy
from . import Node
from ..variables import VariableTypes, validate_required_variable
from ..context import Context, replace_variable_value_with_context
from log import Logger


logger = Logger.get_logger('celery-app')

class VariableAggregationNode(Node):
    """
    A VariableAggregationNode object is used to aggregate variables from multiple sources.
    """
    
    def __init__(
        self, 
        title: str, 
        desc: str = "", 
        input: Optional[VariableTypes] = None, 
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a VariableAggregationNode object with typing enhancements and the ability to track the original node ID.
        """
        init_kwargs = {
            "type": "variable_aggregation",
            "title": title,
            "desc": desc,
            "input": input,
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
            
            input = self.data["input"]
            replace_variable_value_with_context(input, context)
            validate_required_variable(input)
            
            output = None
            for var in input.properties.values():
                if not re.match(r'<<([0-9a-fA-F\-]+)\.(inputs|outputs)\.([^>]+)>>', str(var.value)):
                    input = var
                    output = deepcopy(var)
                    output.name = "output"
                    break
            if not output:
                raise Exception("No output variable found.")
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Variable aggregation node completed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input.to_dict(),
                    'output_type': 1,
                    'outputs': output.to_dict(),
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }