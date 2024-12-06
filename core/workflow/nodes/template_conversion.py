from . import SandboxBaseNode
from typing import Dict, Optional, Any
from datetime import datetime
from ..context import Context, replace_variable_value_with_context
from ..variables import Variable, ObjectVariable, validate_required_variable
from log import Logger


logger = Logger.get_logger('celery-app')

class TemplateConversionNode(SandboxBaseNode):
    """
    This node is responsible for converting data into a fixed string format using Jinja2 template code.
    """

    def __init__(
        self,
        title: str = "",
        desc: str = "",
        input: Optional[ObjectVariable] = None,
        custom_code: Dict[str, str] = {},
        wait_for_all_predecessors: bool = False,
        manual_confirmation: bool = False,
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a TemplateConversionNode object.
        """
        init_kwargs = {
            "type": "template_conversion",
            "title": title,
            "desc": desc,
            "input": input,
            "custom_code": custom_code,
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

        :param context: The context within which the node is executed.
        :param kwargs: Additional arguments.
        :return: A dictionary containing the status and results of the node execution.
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
                # Parse stdout if available
                stdout_text = response['data']['stdout']
                if stdout_text:
                    output=Variable(name="output", value=stdout_text, type="string")
                else:
                    stderr_text = response['data']['stderr']
                    if stderr_text:
                        raise ValueError(stderr_text)
                    else:
                        output=Variable(name="output", value="", type="string")
            else:
                raise ValueError(response['msg'])

            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Template conversion node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input.to_dict(),
                    'output_type': 2,
                    'outputs': output.to_dict()
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }