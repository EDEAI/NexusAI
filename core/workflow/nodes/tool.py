from typing import Any, Dict, Optional
from datetime import datetime
from . import Node
from ..context import Context, replace_variable_value_with_context
from ..variables import Variable, ObjectVariable, validate_required_variable
from core.database.models import ToolAuthorizations, Workflows
from core.tool.provider.builtin_tool_provider import use_tool,validate_credentials, BuiltinTool
from log import Logger


logger = Logger.get_logger('celery-app')


class ToolNode(Node):
    """
    A ToolNode object is used to integrate external tool into the workflow.
    """
    
    def __init__(
        self,
        title: str,
        desc: str = "",
        input: Optional[ObjectVariable] = None,
        tool: Dict[str, str] = {},
        wait_for_all_predecessors: bool = False,
        manual_confirmation: bool = False,
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a ToolNode object.
        """
        init_kwargs = {
            "type": "tool",
            "title": title,
            "desc": desc,
            "input": input,
            "tool": tool,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "manual_confirmation": manual_confirmation,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(
        self,
        context: Context,
        workflow_id: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes the tool node.
        """
        try:
            start_time = datetime.now()
            
            input = self.data['input']  
            replace_variable_value_with_context(input, context,partial_replacement=True)
            validate_required_variable(input)
            
            workflow = Workflows().select_one(
                columns=['team_id'],
                conditions=[{'column': 'id', 'value': workflow_id}]
            )
            assert workflow, 'Invalid workflow ID!'
            provider = self.data['tool']['provider']
            tool_name = self.data['tool']['tool_name']
            credentials = {}
            tool = ToolAuthorizations().select_one(
                columns=['encrypted_credentials'],
                conditions=[
                    {'column': 'team_id', 'value': workflow['team_id']},
                    {'column': 'provider', 'value': provider}
                ]
            )
            if tool:
                credentials = tool['encrypted_credentials']
            if validate_credentials(provider=provider,credentials=credentials):
                output: Variable = use_tool(
                    provider=provider,
                    tool_name=tool_name,
                    parent_type=BuiltinTool,
                    credentials=credentials,
                    parameters=input
                )
            else:
                raise Exception("Invalid credentials")
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Tool node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs':input.to_dict(),
                    'output_type': 1,
                    'outputs': output.to_dict()
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }
    