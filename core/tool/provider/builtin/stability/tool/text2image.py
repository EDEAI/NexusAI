import os
import uuid
from httpx import post
from core.tool.provider.builtin_tool_provider import BuiltinTool
from core.tool.provider.builtin.stability.tool.base import BaseAuthorization
from core.workflow.variables import ObjectVariable, Variable

class StableDiffusionTool(BuiltinTool, BaseAuthorization):
    # Mapping of model names to their respective API endpoints
    model_endpoint_map = {
        'sd3': 'https://api.stability.ai/v2beta/stable-image/generate/sd3',
        'sd3-turbo': 'https://api.stability.ai/v2beta/stable-image/generate/sd3',
        'core': 'https://api.stability.ai/v2beta/stable-image/generate/core',
    }

    def _invoke(self, tool_parameters: ObjectVariable) -> Variable:
        # Convert tool parameters to a dictionary, excluding None values
        tool_parameters_dict = {
            key: value.value
            for key, value in tool_parameters.properties.items()
            if value.value is not None
        }
        
        # Prepare the payload for the API request
        payload = {
            'prompt': tool_parameters_dict.get('prompt', ''),
            'aspect_radio': tool_parameters_dict.get('aspect_radio', '16:9'),
            'mode': 'text-to-image',
            'seed': tool_parameters_dict.get('seed', 0),
            'output_format': 'png',
        }

        # Ensure the output file path is provided
        output_file_path = tool_parameters_dict.get('output_file_path')
        if not output_file_path:
            raise ValueError("Output file path is required")

        # Determine the model to use and adjust payload accordingly
        model = tool_parameters_dict.get('model', 'core')
        if model in ['sd3', 'sd3-turbo']:
            payload['model'] = tool_parameters_dict.get('model')
        if model != 'sd3-turbo':
            payload['negative_prompt'] = tool_parameters_dict.get('negative_prompt', '')

        # Make the API request
        response = post(
            self.model_endpoint_map[tool_parameters_dict.get('model', 'core')],
            headers={
                'accept': 'image/*',
                **self.generate_authorization_headers(self.credentials),
            },
            files={key: (None, str(value)) for key, value in payload.items()},
            timeout=(5, 30)
        )

        # Check for successful response
        if response.status_code != 200:
            raise Exception(response.text)

        # Generate a unique file name and save the image
        file_name = output_file_path + '/' + uuid.uuid4().hex
        file_path = os.path.join(f"{file_name}.png")

        with open(file_path, 'wb') as f:
            f.write(response.content)

        # Return the file path as a Variable
        return Variable(name='file_path', type="string", value=file_path, display_name='Output File Path')

    def invoke(self, parameters: ObjectVariable):
        # Public method to invoke the tool
        return self._invoke(parameters)