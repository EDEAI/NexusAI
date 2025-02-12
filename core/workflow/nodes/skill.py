from . import SandboxBaseNode
from core.database.models import AppRuns, Apps, CustomTools
from typing import Dict, Optional, Any
from datetime import datetime
from ..context import Context, replace_variable_value_with_context
from ..variables import Variable, ObjectVariable, create_variable_from_dict, validate_required_variable
from languages import get_language_content
import json
import ast
from log import Logger

logger = Logger.get_logger('celery-app')


class SkillNode(SandboxBaseNode):
    """
    A SkillNode object is used to integrate external skills into the workflow.
    """

    def __init__(
            self,
            skill_id: int = 0,
            title: str = "",
            desc: str = "",
            input: Optional[ObjectVariable] = None,
            output: Optional[ObjectVariable] = None,
            wait_for_all_predecessors: bool = False,
            manual_confirmation: bool = False,
            flow_data: Dict[str, Any] = {},
            original_node_id: Optional[str] = None,
            custom_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a SkillNode object.
        """
        init_kwargs = {
            "type": "skill",
            "skill_id": skill_id,
            "title": title,
            "desc": desc,
            "input": input,
            "output": output,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "manual_confirmation": manual_confirmation,
            "flow_data": flow_data,
            "custom_data": custom_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id

        super().__init__(**init_kwargs)

    def validate(self):
        if self.data['skill_id'] > 0:
            skill_id = self.data['skill_id']
            custom_tools = CustomTools()
            custom_data = custom_tools.get_skill_by_id(skill_id)
        assert custom_data, get_language_content('skill_does_not_exist')
        assert custom_data['input_variables'], get_language_content('skill_input_variables_error')
        assert custom_data['output_variables'], get_language_content('skill_output_variables_error')
        assert custom_data['code'], get_language_content('skill_code_error')

    def run(
            self,
            context: Context,
            user_id: int = 0,
            app_id: int = 0,
            app_run_id: int = 0,
            node_type: int = 0,  # Changed from "type" to "node_type"
            **kwargs
    ) -> Dict[str, Any]:
        """
        Executes the skill node.
        """
        try:
            start_time = datetime.now()
            if self.data['skill_id'] > 0:
                skill_id = self.data['skill_id']
                custom_tools = CustomTools()
                custom_data = custom_tools.get_skill_by_id(skill_id)
                if not custom_data:
                    raise ValueError('Skill not found')
            else:
                custom_data = self.data['custom_data']
                custom_data['app_id'] = 0
                skill_id = 0
            start_time_str = start_time.replace(microsecond=0).isoformat(sep='_')
            skill_run_id = AppRuns().insert(
                {
                    'app_id': custom_data['app_id'],
                    'tool_id': skill_id,
                    'user_id': user_id,
                    'type': node_type,  # Use new parameter name
                    'name': f'Skill-{skill_id}_{start_time_str}',
                    'inputs': self.data['input'].to_dict(),
                    'status': 2
                }
            )

            self.data['code_dependencies'] = custom_data['dependencies']
            self.data['custom_code'] = ast.literal_eval(custom_data['code'])
            self.data['output'] = create_variable_from_dict(custom_data['output_variables'])

            input = self.data['input']
            replace_variable_value_with_context(input, context)
            validate_required_variable(input)
            if custom_data['app_id'] > 0:
                Apps().increment_execution_times(custom_data['app_id'])

            response = self.run_custom_code()
            # Validate the response status
            status = response['status']
            if status == 0:
                # Parse stdout if available
                stdout_text = response['data']['stdout']
                if stdout_text:
                    try:
                        output_obj = self.data['output']
                        stdout_dict = json.loads(stdout_text)
                        self.output_check(output_obj, stdout_dict)
                        stdout_dict = self.skill_file_handler(stdout_dict,app_run_id=app_run_id,workflow_id=kwargs.get('workflow_id',0))
                        for key, variable in output_obj.properties.items():
                            variable.value = stdout_dict[key]
                    except json.JSONDecodeError as e:
                        return {
                            'status': 'failed',
                            'message': f"Failed to parse stdout as JSON: {e}"
                        }
                else:
                    stderr_text = response['data']['stderr']
                    return {
                        'status': 'failed',
                        'message': stderr_text
                    }
            else:
                stderr_text = response['data']['stderr']
                return {
                    'status': 'failed',
                    'message': stderr_text
                }
            end_time = datetime.now()
            elapsed_time = end_time.timestamp() - start_time.timestamp()
            outputs = self.data['output'].to_dict()
            AppRuns().update(
                {'column': 'id', 'value': skill_run_id},
                {
                    'status': 3,
                    'outputs': outputs,
                    'elapsed_time': elapsed_time,
                    'finished_time': datetime.now()
                }
            )
            return {
                'status': 'success',
                'message': 'custom_code node executed successfully.',
                'data': {
                    'elapsed_time': elapsed_time,
                    'inputs': input.to_dict(),
                    'output_type': 1,
                    'outputs': outputs
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            if 'skill_run_id' in locals():
                AppRuns().update(
                    {'column': 'id', 'value': skill_run_id},
                    {
                        'status': 4,
                        'error': str(e)
                    }
                )
            return {
                'status': 'failed',
                'message': str(e)
            }