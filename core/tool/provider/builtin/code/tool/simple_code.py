import httpx
import uuid, json
from config import settings
from core.tool.provider.builtin_tool_provider import BuiltinTool
from core.workflow.variables import ObjectVariable, Variable

class SimpleCode(BuiltinTool):
    def _invoke(self, tool_parameters: ObjectVariable) -> Variable:
        """
        Invoke the simple code execution tool.

        Parameters:
        tool_parameters (ObjectVariable): The parameters required for the tool execution.

        Returns:
        Variable: The result of the code execution.
        """
        # Set the Bearer token value you have configured
        bearer_token_value = "Kp7wRJ9LzF3qX2hN"  # REPLACE with your actual bearer token value

        # Define the headers for the HTTP POST request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token_value}'
        }

        # Convert tool parameters to a dictionary
        tool_parameters_dict = {
            key: value.value
            for key, value in tool_parameters.properties.items()
            if value.value is not None
        }

        # Extract language and code from parameters
        language = tool_parameters_dict.get('language', 'python3')
        code = tool_parameters_dict.get('code', '')

        # Validate the language
        if language not in ['python3']:
            raise Exception(f'Only python3 is supported, not {language}')

        # Prepare the data payload for the API request
        data = {
            "custom_unique_id": str(uuid.uuid4()),
            "code": code,
            "language": language,
            "template_params": {}  # Pass template parameters to the API
        }

        # Send the POST request to the API endpoint
        response = httpx.post(
            url=f"http://{settings.SANDBOX_HOST}:{settings.SANDBOX_PORT}/run_code", headers=headers, json=data)
        
        # Parse the JSON response
        response = response.json()

        # Check the response status
        if 'status' in response:
            status = response['status']
            if status == 0:
                # Parse stdout if available
                stdout_text = response['data']['stdout']
                if stdout_text:
                    try:
                        return Variable(name='text', type="json", value=json.dumps(stdout_text), display_name='Output text')
                    except json.JSONDecodeError as e:
                        raise Exception(f"Failed to parse stdout as JSON: {e}")
                else:
                    raise Exception(response['data']['stderr'])
            else:
                raise Exception(response['msg'])
        else:
            raise Exception(response['detail'])