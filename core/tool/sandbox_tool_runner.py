"""
Sandbox Tool Runner Module
独立的工具运行器，通过sandbox API执行工具
"""

import os
import ast
import json
import uuid
from typing import Any
from core.workflow.nodes.base.sandbox_base import SandboxBaseNode
from core.workflow.variables import ObjectVariable, Variable
from datetime import datetime

class SandboxToolRunner(SandboxBaseNode):
    """
    Tool runner that inherits from SandboxBaseNode to execute tools through sandbox API.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the SandboxToolRunner.
        """
        # Provide default type and title if not provided
        if 'type' not in kwargs:
            kwargs['type'] = 'sandbox_tool_runner'
        if 'title' not in kwargs:
            kwargs['title'] = 'Sandbox Tool Runner'
        
        super().__init__(**kwargs)
    
    def load_requirements_from_file(self, tool_path: str) -> list[str]:
        """
        Load pip packages from requirements.txt file if it exists.
        
        Args:
            tool_path (str): Path to the tool directory
            
        Returns:
            list[str]: List of pip packages
        """
        requirements_file = os.path.join(tool_path, 'requirements.txt')
        packages = []
        
        if os.path.exists(requirements_file):
            try:
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            packages.append(line)
            except Exception as e:
                print(f"Error reading requirements.txt: {e}")
        
        return packages
    
    def _find_tool_class_in_file(self, tool_file_path: str, tool_name: str = None) -> str:
        """
        Find the Tool class name in a Python file that matches the tool_name.
        
        Args:
            tool_file_path (str): Path to the tool Python file
            tool_name (str): Expected tool name to match against
            
        Returns:
            str: Name of the Tool class
        """
        try:
            with open(tool_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST to find classes that inherit from Tool
            tree = ast.parse(content)
            
            # If tool_name is provided, try to find matching YAML config first
            if tool_name:
                yaml_file_path = tool_file_path.replace('.py', '.yaml')
                if os.path.exists(yaml_file_path):
                    try:
                        import yaml
                        with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
                            yaml_config = yaml.safe_load(yaml_file)
                            yaml_tool_name = yaml_config.get('identity', {}).get('name', '')
                            
                            # If YAML tool name matches the expected tool_name, find the Tool class
                            if yaml_tool_name == tool_name:
                                for node in ast.walk(tree):
                                    if isinstance(node, ast.ClassDef):
                                        # Check if the class inherits from Tool
                                        for base in node.bases:
                                            if isinstance(base, ast.Name) and base.id == 'Tool':
                                                return node.name
                                            elif isinstance(base, ast.Attribute) and base.attr == 'Tool':
                                                return node.name
                                
                                raise ValueError(f"No Tool class found in {tool_file_path} for tool_name: {tool_name}")
                            else:
                                # Tool name doesn't match, skip this file
                                raise ValueError(f"Tool name mismatch. Expected: {tool_name}, Found: {yaml_tool_name}")
                    except Exception as yaml_error:
                        # If YAML parsing fails, fall back to original behavior
                        print(f"Warning: Could not parse YAML config for {tool_file_path}: {yaml_error}")
            
            # Fallback: find any Tool class if no tool_name provided or YAML parsing failed
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if the class inherits from Tool
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'Tool':
                            return node.name
                        elif isinstance(base, ast.Attribute) and base.attr == 'Tool':
                            return node.name
            
            raise ValueError(f"No Tool class found in {tool_file_path}")
        
        except Exception as e:
            raise ValueError(f"Error parsing tool file {tool_file_path}: {e}")
    
    def _generate_tool_invocation_code(self, category: str, provider: str, 
                                     tool_name: str, credentials: dict, 
                                     parameters) -> str:
        """
        Generate Python code to invoke a specific tool.
        
        Args:
            category (str): Tool category (e.g., 't1')
            provider (str): Provider name
            tool_name (str): Tool name
            credentials (dict): Tool credentials
            parameters: Tool parameters (can be dict or ObjectVariable)
            
        Returns:
            str: Generated Python code
        """
        # Import flatten_variable_with_values if parameters is not a dict
        from core.workflow.variables import flatten_variable_with_values
        
        # Convert parameters to dict if it's an ObjectVariable
        if not isinstance(parameters, dict):
            parameters = flatten_variable_with_values(parameters)
        
        # Find tool directory - get project root correctly
        current_file = os.path.realpath(__file__)
        # Go up from core/tool/sandbox_tool_runner.py to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        sandbox_path = os.path.join(project_root, 'docker', 'sandbox')
        tool_dir = os.path.join(sandbox_path, 'tools', category, provider)
        
        if not os.path.exists(tool_dir):
            raise FileNotFoundError(f"Tool directory not found: {tool_dir}")
        
        # Find tool Python file
        tools_dir = os.path.join(tool_dir, 'tools')
        tool_file = None
        
        if os.path.exists(tools_dir):
            # First try to find file with matching tool_name in YAML config
            for file in os.listdir(tools_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    tool_file_path = os.path.join(tools_dir, file)
                    yaml_file_path = tool_file_path.replace('.py', '.yaml')
                    
                    # Check if corresponding YAML file exists and matches tool_name
                    if os.path.exists(yaml_file_path):
                        try:
                            import yaml
                            with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
                                yaml_config = yaml.safe_load(yaml_file)
                                yaml_tool_name = yaml_config.get('identity', {}).get('name', '')
                                
                                if yaml_tool_name == tool_name:
                                    # Found matching tool, verify it has a Tool class
                                    try:
                                        tool_class_name = self._find_tool_class_in_file(tool_file_path, tool_name)
                                        tool_file = file
                                        break
                                    except ValueError:
                                        continue
                        except Exception as yaml_error:
                            # If YAML parsing fails, skip this file
                            continue
            
            # If not found by tool_name, try to find any file with Tool class (fallback)
            if not tool_file:
                for file in os.listdir(tools_dir):
                    if file.endswith('.py') and not file.startswith('__'):
                        tool_file_path = os.path.join(tools_dir, file)
                        try:
                            tool_class_name = self._find_tool_class_in_file(tool_file_path)
                            # If we found a tool class, we'll use this file
                            tool_file = file
                            break
                        except ValueError:
                            continue
        
        if not tool_file:
            raise FileNotFoundError(f"No valid tool file found in {tools_dir}")
        
        # Get tool class name
        tool_file_path = os.path.join(tools_dir, tool_file)
        tool_class_name = self._find_tool_class_in_file(tool_file_path, tool_name)
        
        # Generate import and execution code
        import_module = tool_file.replace('.py', '')
        
        # Generate credentials assignment
        credentials_code = ""
        for key, value in credentials.items():
            credentials_code += f'    "{key}": {repr(value)},\n'
        
        # Generate parameters assignment
        parameters_code = ""
        for key, value in parameters.items():
            parameters_code += f'    "{key}": {repr(value)},\n'
        
        code = f'''
def run_tool():
    """
    Execute tool through sandbox API.
    """
    from gevent import monkey
    monkey.patch_all(sys=True)

    # Import the tool class
    from tools.{import_module} import {tool_class_name}
    
    # Initialize tool with credentials
    tool = {tool_class_name}.from_credentials(
        credentials={{
{credentials_code}        }},
        user_id="{provider}_user"
    )

    # Invoke tool with parameters
    results = list(tool.invoke({{
{parameters_code}    }}))

    # Process and return results
    for result in results:
        if result.message:
            if hasattr(result.message, 'text'):
                return result.message.text
            else:
                return result.message
        else:
            return result

# Execute the tool
run_tool()
'''
        
        return code
    
    def run_sandbox_tool(self, category: str, provider: str, tool_name: str, 
                        credentials: dict, parameters) -> Variable:
        """
        Run a tool through the sandbox API using inherited run_custom_code method.
        
        Args:
            category (str): Tool category (e.g., 't1')
            provider (str): Provider name
            tool_name (str): Tool name
            credentials (dict): Tool credentials
            parameters: Tool parameters (can be dict or ObjectVariable)
            
        Returns:
            Variable: Tool execution result as Variable object
        """
        start_time = datetime.now()
        # Find tool directory - get project root correctly
        current_file = os.path.realpath(__file__)
        # Go up from core/tool/sandbox_tool_runner.py to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        sandbox_path = os.path.join(project_root, 'docker', 'sandbox')
        tool_dir = os.path.join(sandbox_path, 'tools', category, provider)
        
        # Load pip packages from requirements.txt
        pip_packages = self.load_requirements_from_file(tool_dir)
        
        # Generate tool invocation code
        code = self._generate_tool_invocation_code(category, provider, 
                                                    tool_name, credentials, parameters)
        
        # Set up data for sandbox API using inherited method
        self.data = {
            'custom_code': {'python3': code},
            'code_dependencies': {'python3': pip_packages},
            'input': ObjectVariable(name='input'),
            'output': ObjectVariable(name='output'),
            'tool_type': category,  # Add tool_type parameter
            'tool_name': provider   # Add tool_name parameter
        }
        
        # Use inherited run_custom_code method
        response = self.run_custom_code()
        
        if 'status' in response:
            status = response['status']
            if status == 0:
                # Parse stdout if available
                stdout_text = response['data']['stdout']
                if stdout_text:
                    try:
                        return Variable(name='text', type="string", value=stdout_text, display_name='Output text')
                    except json.JSONDecodeError as e:
                        raise Exception(f"Failed to parse stdout as JSON: {e}")
                else:
                    raise Exception(response['data']['stderr'])
            else:
                raise Exception(response['data']['stderr'])
        else:
            raise Exception(response['detail'])

def use_sandbox_tool(category: str, provider: str, tool_name: str, 
                    credentials: dict, parameters) -> Variable:
    """
    Use a tool through the sandbox API.
    
    Args:
        category (str): Tool category (e.g., 't1')
        provider (str): Provider name
        tool_name (str): Tool name
        credentials (dict): Tool credentials
        parameters: Tool parameters (can be dict or ObjectVariable)
        
    Returns:
        Variable: Tool execution result as Variable object
    """
    runner = SandboxToolRunner()
    return runner.run_sandbox_tool(category, provider, tool_name, credentials, parameters) 