from typing import Any, Dict, Optional
from datetime import datetime
import json
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
        output: Optional[ObjectVariable] = None,
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
            "flow_data": flow_data,
            "output": output
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(
        self,
        context: Context,
        app_run_id: int = 0,
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
            if 'tool_category' in self.data['tool']:
                tool_category = self.data['tool']['tool_category']
            else:
                tool_category = 't1'
            credentials = {}
            tool = ToolAuthorizations().select_one(
                columns=['encrypted_credentials'],
                conditions=[
                    {'column': 'team_id', 'value': workflow['team_id']},
                    {'column': 'provider', 'value': provider},
                    {'column': 'tool_category', 'value': tool_category}
                ]
            )
            if tool:
                credentials = tool['encrypted_credentials']
            # if validate_credentials(provider=provider,credentials=credentials):
            from core.tool.sandbox_tool_runner import SandboxToolRunner
            runner = SandboxToolRunner()
            response = runner.run_sandbox_tool(
                category=tool_category,
                provider=provider,
                tool_name=tool_name,
                credentials=credentials,
                parameters=input,
                app_run_id=app_run_id,
                workflow_id=workflow_id
            )
            
            # Handle response and create output Variable
            if 'status' in response:
                status = response['status']
                if status == 0:
                    # Parse stdout if available
                    stdout_text = response['data']['stdout']
                    if stdout_text:
                        try:
                            if 'nexus_ai_file_path' in stdout_text:
                                stdout_dict = runner.skill_file_handler(json.loads(stdout_text), app_run_id=app_run_id, workflow_id=workflow_id)
                                self.data['output'] = ObjectVariable(name='output')
                                self.data['output'].add_property('output', value=Variable(name='output',display_name='Nexus AI File Path',type='file',value=stdout_dict['nexus_ai_file_path']))
                            else:
                                self.data['output'] = ObjectVariable(name='output')
                                self.data['output'].add_property('output', value=Variable(name='output',display_name='Content',type='string',value=stdout_text))
                        except json.JSONDecodeError as e:
                            return {
                                'status': 'failed',
                                'message': f"Failed to parse stdout as JSON: {e}"
                            }
                    else:
                        return {
                            'status': 'failed',
                            'message': response['data']['stderr']
                        }
                else:
                    return {
                        'status': 'failed',
                        'message': str(response['data']['stderr'])
                    }
            else:
                return {
                    'status': 'failed',
                    'message': response['detail']
                }
            # else:
            #     raise Exception("Invalid credentials")
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Tool node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs':input.to_dict(),
                    'output_type': 1,
                    'outputs': self.data['output'].to_dict()
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }
    