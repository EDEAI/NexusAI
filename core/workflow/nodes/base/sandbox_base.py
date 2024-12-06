import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent.parent))
import traceback
import uuid
import ast
import httpx
from . import Node
from ... import Variable, ObjectVariable
from config import settings
from log import Logger


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
                'json': (list, dict)  # Both list and dict are valid for 'json' type
            }
            for param_name, param_props in input_params.items():
                # Skip validation if the parameter has a default value and no value is provided
                if param_name not in func_params or (func_params[param_name] is not None and param_props.value is None):
                    continue

                expected_type_name = param_props.type
                if expected_type_name not in type_map:
                    expected_type = 'json'
                else:
                    expected_type = type_map[expected_type_name]
                if expected_type_name == 'json':
                    params_value = json.loads(param_props.value)
                else:
                    params_value = param_props.value
                if not isinstance(params_value, expected_type):
                    raise TypeError(
                        f"Parameter '{param_name}' is expected to be of type '{expected_type_name}' "
                        f"but got '{type(params_value).__name__}'.")

                print(f"Parameter '{param_name}' is of the correct type '{expected_type_name}' ({expected_type}).")

        # Helper function to generate code for assigning input parameters
        def generate_input_assignments(input_params):
            return "\n".join(
                [f"{key} = {val.value!r}" for key, val in input_params.items() if val.type != 'json'] +
                [f"{key} = {val.value!r}" for key,
                                              val in input_params.items() if val.type == 'json']
            )

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
                'json': (list, dict)
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
            elif 'jinja2' in custom_code:
                code = custom_code['jinja2']
                # Prepare the input parameters for the Jinja2 template
                input_params = {}
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
                url=f"http://{settings.SANDBOX_HOST}:{settings.SANDBOX_PORT}/run_code", headers=headers, json=data)
            print(response.json())
            return response.json()

        except Exception as e:
            logger.exception('ERROR!!')
            raise ValueError(str(e))  # Raise the exception to be handled by the caller or to see the error message