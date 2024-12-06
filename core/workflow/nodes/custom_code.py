from . import SandboxBaseNode
from typing import Dict, Optional, Any, List
from datetime import datetime
from ..context import Context, replace_variable_value_with_context
import json
from ..variables import Variable, ObjectVariable, validate_required_variable
from log import Logger


logger = Logger.get_logger('celery-app')

class CustomCodeNode(SandboxBaseNode):
    """
    A node representing custom python3 code execution in a workflow.
    """

    def __init__(
        self,
        title: str = "",
        desc: str = "",
        input: Optional[ObjectVariable] = None,
        code_dependencies: Dict[str, List[str]] = {},
        custom_code: Dict[str, str] = {},
        output: Optional[ObjectVariable] = None,
        wait_for_all_predecessors: bool = False,
        manual_confirmation: bool = False,
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a CustomCodeNode object.
        """
        init_kwargs = {
            "type": "custom_code",
            "title": title,
            "desc": desc,
            "input": input,
            "code_dependencies": code_dependencies,
            "custom_code": custom_code,
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
        Executes the custom node.
        """
        try:
            start_time = datetime.now()
            
            input = self.data['input']
            replace_variable_value_with_context(input, context)
            validate_required_variable(input)
            
            response = self.run_custom_code()

            # Validate the response status
            status = response['status']
            if status == 0:
                output = ObjectVariable(name='output')

                # Parse stdout if available
                stdout_text = response['data']['stdout']
                if stdout_text:
                    try:
                        stdout_dict = json.loads(stdout_text)
                        self.output_check(self.data['output'], stdout_dict)
                        for key, value in stdout_dict.items():
                            type_map = {
                                str: 'string',
                                int: 'number',
                                float: 'number'
                            }
                            var_type = type_map.get(type(value), 'json')
                            if var_type == 'json':
                                value = json.dumps(value, ensure_ascii=False)
                            output.add_property(key=key, value=Variable(name=key, value=value, type=var_type))
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
                    'message': response['msg']
                }

            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'custom_code node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input.to_dict(),
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
