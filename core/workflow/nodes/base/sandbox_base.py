import sys
from pathlib import Path
import json
import os
import uuid
import shutil
from typing import Optional, List

sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent.parent))
import traceback
import ast
import httpx
from . import Node
from ... import Variable, ObjectVariable
from config import settings
from log import Logger
import hashlib

project_root = Path(__file__).absolute().parent.parent.parent.parent.parent
logger = Logger.get_logger('celery-app')


class SandboxBaseNode(Node):
    """
    Base class for all sandbox nodes.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the SandboxBaseNode class.
        """
        super().__init__(**kwargs)

    def check_code(self, input: ObjectVariable, output: ObjectVariable, code: str):
        """
        Validates and checks the user-provided code to ensure it meets specific criteria.
        """

        # Helper function to get the type annotation of a function parameter
        def get_annotation_type(annotation):
            print(annotation)
            if annotation is None:
                return None
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation.value, ast.Name):
                return annotation.value.id
            return None

        # Helper function to parse the code and retrieve the function definition from the AST
        def parse_code_and_get_function(code):
            try:
                code_ast = ast.parse(code)  # Parse the code into an AST
                # Extract the first function definition from the AST
                func_def = next(node for node in code_ast.body if isinstance(
                    node, ast.FunctionDef))
                return code_ast, func_def
            except SyntaxError as e:
                raise ValueError(f"Syntax error in the provided code: {e}")

        # Helper function to validate the input parameters of the function against the expected input parameters
        def validate_input_params(func_params, input_params):
            type_map = {
                'string': str,
                'number': (int, float),  # Support both int and float for 'number' type
                'json': (list, dict),  # Both list and dict are valid for 'json' type
                'file': (str, int)  # File type's value is actually a str or int
            }
            for param_name, param_props in input_params.items():
                if param_name not in func_params:
                    continue

                raw_value = param_props.value
                # Treat missing / empty string values as "not provided" so optional number fields don't break validation
                if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == ''):
                    continue

                expected_type_name = param_props.type
                expected_type = type_map[expected_type_name]
                if expected_type_name == 'json':
                    # Allow both serialized JSON strings and already parsed dict/list values
                    params_value = raw_value
                    if isinstance(raw_value, str):
                        try:
                            params_value = json.loads(raw_value)
                        except json.JSONDecodeError:
                            raise ValueError(f"Invalid JSON format for parameter '{param_name}': {raw_value}")
                else:
                    params_value = raw_value
                if not isinstance(params_value, expected_type):
                    raise TypeError(
                        f"Parameter '{param_name}' is expected to be of type '{expected_type_name}' "
                        f"but got '{type(params_value).__name__}'.")

                print(f"Parameter '{param_name}' is of the correct type '{expected_type_name}' ({expected_type}).")

        # Helper function to generate code for assigning input parameters
        def generate_input_assignments(input_params):
            from core.database.models import UploadFiles
            kv = []
            for key, val in input_params.items():
                var_value = val.value
                if val.type == 'number':
                    # Default empty/None number inputs to 0 so downstream code doesn't break
                    if var_value is None or (isinstance(var_value, str) and var_value.strip() == ''):
                        var_value = 0
                if val.type == 'file':
                    # Get file path
                    if isinstance(var_value, int):
                        # Upload file ID
                        file_data = UploadFiles().get_file_by_id(var_value)
                        file_path = '/' + file_data['path']
                    elif isinstance(var_value, str):
                        if var_value[0] == '/':
                            var_value = var_value[1:]
                        file_path = '/storage/' + var_value
                    else:
                        # This should never happen
                        raise Exception('Unsupported value type!')
                    var_value = file_path
                elif val.type == 'json':
                    # Parse JSON string to Python object
                    try:
                        parsed_value = json.loads(var_value)
                        kv.append(f"{key} = {parsed_value}")
                        continue  # Skip the default append
                    except json.JSONDecodeError:
                        raise ValueError(f"Invalid JSON format for parameter '{key}': {var_value}")
                kv.append(f"{key} = {var_value!r}")
            return "\n".join(kv)

        def validate_return_type_and_fields(func_def, expected_output_params):
            return_annotation = func_def.returns

            # Assume 'Dict' type if annotation is missing
            if return_annotation is None:
                return_annotation_type = 'dict'
            else:
                return_annotation_type = get_annotation_type(return_annotation)

            if return_annotation_type.lower() != 'dict':
                raise ValueError(
                    f"Function return type is not 'Dict'. Found: {return_annotation_type}")

            # Boolean dictionary to track found fields in the return statement
            # return_field_found = {
            #     field: False for field in expected_output_params}

            # for node in ast.walk(func_def):
            #     if isinstance(node, ast.Return):
            #         for key in node.value.keys:
            #             if isinstance(key, ast.Constant) and key.value in expected_output_params:
            #                 return_field_found[key.value] = True

            # for field, found in return_field_found.items():
            #     if not found:
            #         raise ValueError(
            #             f"Output field '{field}' not found in function returns.")

        # Parse and validate the user-provided code
        code_ast, func_def = parse_code_and_get_function(code)

        # Validate input parameters
        func_params = {arg.arg: get_annotation_type(
            arg.annotation) for arg in func_def.args.args}
        input_params = input.properties
        validate_input_params(func_params, input_params)

        # Generate input assignments
        input_assignments = generate_input_assignments(input_params)

        # Combine input assignments with the provided code
        complete_code = f"{input_assignments}\n{code}"

        # Identify the function call
        function_name = func_def.name
        input_keys = ", ".join([f"{key} = {key}" for key in input_params.keys()])
        function_call_str = f"{function_name}({input_keys})"

        # Check if function call captures the return value
        if not any(isinstance(node, ast.Assign) and isinstance(node.value,
                                                               ast.Call) and node.value.func.id == function_name for
                   node in code_ast.body):
            complete_code += f"\nresult = {function_call_str}\nprint(result)"

        try:
            code_ast = ast.parse(complete_code)
            compile(code_ast, filename="<string>", mode="exec")
        except SyntaxError as e:
            return f"Syntax error in the provided code: {e}"

        # Validate return type and fields
        output_params = output.properties
        validate_return_type_and_fields(func_def, output_params)
        return complete_code

    def output_check(self, output: ObjectVariable, result: dict):
        # Helper function to get expected type
        def get_expected_type(variable_type):
            type_map = {
                'string': str,
                'number': (int, float),
                'json': (list, dict),
                'file': str
            }
            return type_map.get(variable_type, (list, dict))

        # Extract properties from the output object
        outputObj = output.properties

        # Iterate through each key and its corresponding variable in outputObj
        for key, variable in outputObj.items():
            if key not in result:
                raise ValueError(f"Missing key '{key}' in result")

            expected_type = get_expected_type(variable.type)
            result_value = result[key]

            if isinstance(expected_type, tuple) and 'json' in variable.type:
                # Handle 'json' type
                if isinstance(result_value, str):
                    try:
                        result_value = json.loads(result_value)
                    except json.JSONDecodeError:
                        raise ValueError(f"Key '{key}' contains invalid JSON string: {result_value}")

                if not isinstance(result_value, expected_type):
                    raise ValueError(
                        f"Key '{key}' has incorrect type. Expected JSON object or array, got {type(result_value).__name__} ({result_value})")
            else:
                # Check if the type of the result[key] matches the expected type
                if not isinstance(result_value, expected_type):
                    raise ValueError(
                        f"Key '{key}' has incorrect type. Expected {variable.type}, got {type(result_value).__name__} ({result_value})")
        return True

    def _get_storage_path(self, source_path: str, target_path: str) -> str:
        """
        Copies a file from the source path to the target path.

        Args:
            source_path (str): The path of the source file.
            target_path (str): The path where the file should be copied to.

        Returns:
            str: The full path of the new file, or an error message if the operation failed.
        """
        # Convert source and target paths to absolute paths
        source_path = os.path.abspath(source_path)
        target_path = os.path.abspath(target_path)
        print(f'[[[[[[[[[[[[[[{target_path}]]]]]]]]]]]]]]')
        # Check if the source file exists
        if not os.path.exists(source_path):
            return False, f"Source file does not exist: {source_path}"
        try:
            print(os.path.dirname(target_path))
            # Ensure the target directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Change ownership of the target directory to the current user
            shutil.chown(os.path.dirname(target_path), user=os.getuid(), group=os.getgid())

            # Copy the file
            shutil.copy2(source_path, target_path)

            # Change ownership of the copied file to the current user
            shutil.chown(target_path, user=os.getuid(), group=os.getgid())

            # Delete the old file
            os.remove(source_path)

            # Return the absolute path of the new file
            return True, target_path
        except PermissionError as e:
            return False, f"Permission denied: {str(e)}"
        except Exception as e:
            return False, f"Error occurred while copying the file: {str(e)}"

    def skill_file_handler(self, stdout_dict: dict, workflow_id: int = 0, app_run_id: int = 0, tool_type: str = None, tool_name: str = None) -> dict:
        """
        Handles skill files by copying them to a secure storage path and updating the dictionary with new paths.

        Args:
            stdout_dict (dict): Dictionary containing the standard output data.
            workflow_id (int): Workflow ID (default is 0).
            app_run_id (int): Application run ID (default is 0).
            tool_type (str): Tool type for tool nodes (optional).
            tool_name (str): Tool name for tool nodes (optional).

        Returns:
            dict: Updated dictionary with new file paths.
        """
        try:
            for key, value in stdout_dict.items():
                if isinstance(value, str) and 'file://' in value:
                    fixed_directory = 'storage'
                    original_path = value.split('file:///')[-1]
                    file_suffix = original_path.split('.')[-1]
                    print(f"Found skill file path - Key: {key}, Original path: {original_path}")
                    unique_id = str(uuid.uuid4())
                    if workflow_id > 0:
                        relative_path = f"/workflow/wf{workflow_id}/run{app_run_id}/{self.id}/{unique_id}.{file_suffix}"
                    elif tool_type and tool_name:
                        # Handle tool type nodes
                        relative_path = f"/tool/{tool_type}/{tool_name}/{unique_id}.{file_suffix}"
                    else:
                        # Handle skill type nodes
                        skill_id = self.data.get('skill_id', 0)
                        relative_path = f"/skill/sk{skill_id}/{unique_id}.{file_suffix}"
                    # Get the secure full storage path
                    target_dirstatus, target_dir = self._get_storage_path(original_path,
                                                                          fixed_directory + relative_path)
                    if target_dirstatus:
                        stdout_dict[key] = target_dir.split(fixed_directory)[-1]
                    else:
                        raise ValueError(target_dir)
            return stdout_dict
        except Exception as e:
            logger.exception('ERROR!!')
            raise ValueError(str(e))
    
    # Check if the virtual environment exists in the cache for the given pip packages
    @staticmethod
    def check_venv_exists(pip_packages: Optional[List[str]]) -> bool:
        """
        Check if a virtual environment exists in the cache for the specified pip packages.

        Args:
            pip_packages (Optional[List[str]]): List of pip package names.

        Returns:
            bool: True if the virtual environment exists, False otherwise.
        """
        # Use relative path for local development, absolute path for production
        VENV_CACHE_DIR = os.path.join(os.getcwd(), "docker", "volumes", "venv_cache")
        # If pip_packages is empty, check for the base environment
        if not pip_packages:
            base_venv_path = os.path.join(VENV_CACHE_DIR, 'base')
            # Check if the base venv directory and its python binary exist
            return (os.path.exists(base_venv_path))

        # Sort the package list to ensure consistent hash regardless of order
        sorted_packages = sorted(pip_packages)
        # Join the sorted package names into a single string separated by newlines
        requirements_content = '\n'.join(sorted_packages)

        # Calculate the SHA-256 hash of the requirements content
        hasher = hashlib.sha256()
        hasher.update(requirements_content.encode('utf-8'))
        pip_packages_hash = hasher.hexdigest()
        # Construct the path to the cached virtual environment
        venv_path = os.path.join(VENV_CACHE_DIR, pip_packages_hash)
        # Check if the venv directory and its python binary exist
        return (os.path.exists(venv_path))
        
    def run_custom_code(self):
        """
        Executes the custom code provided by the user, ensuring that necessary validations
        and preparations are made before actually running the code.
        """
        try:
            # Set the Bearer token value you have configured
            bearer_token_value = "Kp7wRJ9LzF3qX2hN"  # REPLACE with your actual bearer token value

            # Define the headers for the HTTP POST request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {bearer_token_value}'
            }

            # Extract necessary information from the node's data
            code_dependencies = self.data['code_dependencies'] if self.data.get('code_dependencies') else {}
            custom_code = self.data['custom_code']
            input = self.data['input']
            output = self.data.get('output')
            tool_type = self.data.get('tool_type')  # Get tool_type if available
            tool_name = self.data.get('tool_name')  # Get tool_name if available

            # Check the language of the provided custom code
            if 'python3' in custom_code:
                code = custom_code['python3']
                packages = code_dependencies.get('python3', [])  # Get the required packages for Python
                # Validate the python code
                verify_code = self.check_code(input, output, code)
                print(verify_code)
                # Create the data payload with custom_unique_id instead of flow_id
                data = {
                    "custom_unique_id": str(uuid.uuid4()),
                    "code": verify_code,
                    "language": "python3",
                    "pip_packages": packages  # Ensure required package is installed
                }
                
                # Add tool_type and tool_name if available
                if tool_type:
                    data["tool_type"] = tool_type
                if tool_name:
                    data["tool_name"] = tool_name
            elif 'jinja2' in custom_code:
                code = custom_code['jinja2']
                # Prepare the input parameters for the Jinja2 template
                input_params = {}
                if hasattr(input, 'properties') and input.properties:
                    for key, value in input.properties.items():
                        input_params[key] = value.value
                data = {
                    "custom_unique_id": str(uuid.uuid4()),
                    "code": code,
                    "language": "jinja2",
                    "template_params": input_params  # Pass template parameters to the API
                }
            else:
                raise NotImplementedError('Other languages are not supported at this time')

            # Send the POST request to the API endpoint
            print(data)
            response = httpx.post(
                url=f"http://{settings.SANDBOX_HOST}:{settings.SANDBOX_PORT}/run_code", headers=headers, json=data, timeout=600)

            # Check if the response content is empty
            if not response.content:
                raise ValueError("Empty response from the server")

            print(response.json())
            return response.json()

        except Exception as e:
            logger.exception('ERROR!!')
            raise ValueError(str(e))  # Raise the exception to be handled by the caller or to see the error message
