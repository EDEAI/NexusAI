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
    
    def _discover_tool_and_generate_code(self, category: str, provider: str, 
                                       tool_name: str, credentials: dict, 
                                       parameters) -> tuple[str, str]:
        """
        Discover tool configuration and generate Python code to invoke the tool.
        
        This method follows a step-by-step process:
        1. Locate the category directory
        2. Locate the provider directory within the category
        3. Find the provider's YAML configuration file
        4. Traverse through the tools directory
        5. Search for tool YAML files and match by identity.name
        6. Extract the Python source file from extra.python.source
        7. Find the Tool class that inherits from Tool base class
        
        Args:
            category (str): Tool category (e.g., 't1')
            provider (str): Provider name
            tool_name (str): Tool name to search for
            credentials (dict): Tool credentials
            parameters: Tool parameters (can be dict or ObjectVariable)
            
        Returns:
            tuple[str, str]: (tool_class_name, generated_code)
        """
        from core.workflow.variables import flatten_variable_with_values
        
        # Convert parameters to dict if it's an ObjectVariable
        if not isinstance(parameters, dict):
            parameters = flatten_variable_with_values(parameters)
        
        # Step 1: Locate the category directory
        current_file = os.path.realpath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        sandbox_path = os.path.join(project_root, 'docker', 'sandbox')
        category_dir = os.path.join(sandbox_path, 'tools', category)
        
        if not os.path.exists(category_dir):
            raise FileNotFoundError(f"Category directory not found: {category_dir}")
        
        # Step 2: Locate the provider directory within the category
        provider_dir = os.path.join(category_dir, provider)
        if not os.path.exists(provider_dir):
            raise FileNotFoundError(f"Provider directory not found: {provider_dir}")
        
        # Step 3: Find the provider's YAML configuration file and read tools paths
        provider_yaml_path = os.path.join(provider_dir, 'provider', f'{provider}.yaml')
        if not os.path.exists(provider_yaml_path):
            raise FileNotFoundError(f"Provider YAML file not found: {provider_yaml_path}")
        
        # Read the provider YAML file to get tools configuration
        try:
            import yaml
            with open(provider_yaml_path, 'r', encoding='utf-8') as provider_yaml_file:
                provider_config = yaml.safe_load(provider_yaml_file)
        except Exception as e:
            raise ValueError(f"Failed to parse provider YAML file {provider_yaml_path}: {e}")
        
        # Step 4: Get tools paths from provider YAML configuration
        tools_config = provider_config.get('tools', [])
        if not tools_config:
            raise ValueError(f"No tools configuration found in provider YAML: {provider_yaml_path}")
        
        # Step 5: Search for tool YAML files and match by identity.name
        tool_yaml_path = None
        tool_config = None
        
        # Iterate through tools list in provider YAML to find matching tool_name
        for tool_yaml_relative_path in tools_config:
            if not tool_yaml_relative_path:
                continue
            
            # Construct full path to tool YAML file
            tool_yaml_full_path = os.path.join(provider_dir, tool_yaml_relative_path)
            
            if not os.path.exists(tool_yaml_full_path):
                print(f"Warning: Tool YAML file not found: {tool_yaml_full_path}")
                continue
            
            try:
                with open(tool_yaml_full_path, 'r', encoding='utf-8') as tool_yaml_file:
                    config = yaml.safe_load(tool_yaml_file)
                    # Check if identity.name matches the tool_name
                    identity_name = config.get('identity', {}).get('name', '')
                    
                    if identity_name == tool_name:
                        tool_yaml_path = tool_yaml_full_path
                        tool_config = config
                        break
            except Exception as e:
                print(f"Warning: Could not parse tool YAML config {tool_yaml_full_path}: {e}")
                continue
        
        if not tool_yaml_path:
            raise ValueError(f"No tool found with identity.name matching tool_name: {tool_name}")
        
        # Step 6: Extract the Python source file from extra.python.source
        python_source = tool_config.get('extra', {}).get('python', {}).get('source', '')
        if not python_source:
            raise ValueError(f"No python.source specified in YAML config: {tool_yaml_path}")
        
        # Determine the Python file path relative to the provider directory
        # The python source path should be relative to the provider directory, not the tool YAML directory
        if python_source.endswith('.py'):
            python_file_path = os.path.join(provider_dir, python_source)
        else:
            python_file_path = os.path.join(provider_dir, f"{python_source}.py")
        
        if not os.path.exists(python_file_path):
            raise FileNotFoundError(f"Python file not found: {python_file_path}")
        # Step 7: Find the Tool class that inherits from Tool base class
        tool_class_name = self._find_tool_class_in_file(python_file_path, tool_name)
        import_module = python_source.replace('.py', '').replace('/','.')
        
        # Generate credentials code for the tool invocation
        credentials_code = ""
        for key, value in credentials.items():
            credentials_code += f'    "{key}": {repr(value)},\n'
        
        # Generate parameters code for the tool invocation
        parameters_code = ""
        for key, value in parameters.items():
            parameters_code += f'    "{key}": {repr(value)},\n'
        
        # Generate the complete Python code for tool execution
        code = '''
import os
import uuid
import sys
import base64


def run_tool():
    """
    Execute tool through sandbox API.
    """
    from gevent import monkey
    monkey.patch_all(sys=True)

    from ''' + import_module + ''' import ''' + tool_class_name + '''
    
    def detect_file_type_from_binary(binary_data):
        """
        Detect file type from binary data header.
        
        Args:
            binary_data (bytes): Binary data to analyze
            
        Returns:
            str: File extension based on binary header
        """
        if not binary_data:
            return '.bin'
        
        header = binary_data[:32]
        
        # Image formats
        # PNG signature: 0x89 + "PNG" + CR + LF + 0x1a + LF
        png_signature = bytes([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
        if header.startswith(png_signature):
            return '.png'
        
        # JPEG signature: 0xff 0xd8 0xff
        elif header.startswith(bytes([0xff, 0xd8, 0xff])):
            return '.jpg'
        
        # GIF signature: "GIF8"
        elif header.startswith(b'GIF8'):
            return '.gif'
        
        # WebP signature: "RIFF" + 4 bytes + "WEBP"
        elif header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WEBP':
            return '.webp'
        
        # BMP signature: "BM"
        elif header.startswith(b'BM'):
            return '.bmp'
        
        # TIFF signature: "II" (little endian) or "MM" (big endian) + 0x2a
        elif (header.startswith(b'II') and len(header) >= 4 and header[2:4] == bytes([0x2a, 0x00])) or \\
            (header.startswith(b'MM') and len(header) >= 4 and header[2:4] == bytes([0x00, 0x2a])):
            return '.tiff'
        
        # ICO signature: 0x00 0x00 0x01 0x00
        elif header.startswith(bytes([0x00, 0x00, 0x01, 0x00])):
            return '.ico'
        
        # SVG (text-based, check for XML declaration)
        elif header.startswith(b'<?xml') or header.startswith(b'<svg'):
            return '.svg'
        
        # Document formats
        # PDF signature: "%PDF"
        elif header.startswith(b'%PDF'):
            return '.pdf'
        
        # Microsoft Office formats
        # DOC/XLS/PPT: D0 CF 11 E0 A1 B1 1A E1
        elif header.startswith(bytes([0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1, 0x1a, 0xe1])):
            return '.doc'  # Could be .doc, .xls, .ppt - default to .doc
        
        # DOCX/XLSX/PPTX: PK\\x03\\x04 (ZIP format)
        elif header.startswith(b'PK\\x03\\x04'):
            return '.docx'  # Could be .docx, .xlsx, .pptx - default to .docx
        
        
        # Text formats
        # UTF-8 BOM: EF BB BF
        elif header.startswith(bytes([0xef, 0xbb, 0xbf])):
            return '.txt'
        
        # UTF-16 LE BOM: FF FE
        elif header.startswith(bytes([0xff, 0xfe])):
            return '.txt'
        
        # UTF-16 BE BOM: FE FF
        elif header.startswith(bytes([0xfe, 0xff])):
            return '.txt'
        
        # Audio formats
        # MP3: ID3v2 or MPEG sync
        elif header.startswith(b'ID3') or \\
            (len(header) >= 3 and header[0] == 0xff and (header[1] & 0xe0) == 0xe0):
            return '.mp3'
        
        # WAV signature: "RIFF" + 4 bytes + "WAVE"
        elif header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WAVE':
            return '.wav'
        
        # FLAC signature: "fLaC"
        elif header.startswith(b'fLaC'):
            return '.flac'
        
        # OGG signature: "OggS"
        elif header.startswith(b'OggS'):
            return '.ogg'
        
        # Video formats
        # MP4: ftyp box
        elif len(header) >= 8 and header[4:8] == b'ftyp':
            return '.mp4'
        
        # AVI signature: "RIFF" + 4 bytes + "AVI "
        elif header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'AVI ':
            return '.avi'
        
        # MOV signature: "ftyp" at offset 4
        elif len(header) >= 12 and header[4:8] == b'ftyp':
            return '.mov'
        
        # MKV signature: 1A 45 DF A3
        elif header.startswith(bytes([0x1a, 0x45, 0xdf, 0xa3])):
            return '.mkv'
        
        # WebM signature: 1A 45 DF A3 (same as MKV, but check for webm in ftyp)
        elif header.startswith(bytes([0x1a, 0x45, 0xdf, 0xa3])) and len(header) >= 12:
            if b'webm' in header[4:12]:
                return '.webm'
            else:
                return '.mkv'
        
        # Archive formats
        # ZIP signature: PK\\x03\\x04
        elif header.startswith(b'PK\\x03\\x04'):
            return '.zip'
        
        # RAR signature: Rar!\\x1A\\x07
        elif header.startswith(b'Rar!\\x1a\\x07'):
            return '.rar'
        
        # 7Z signature: 7z\\xBC\\xAF\\x27\\x1C
        elif header.startswith(bytes([0x37, 0x7a, 0xbc, 0xaf, 0x27, 0x1c])):
            return '.7z'
        
        # GZIP signature: 1F 8B 08
        elif header.startswith(bytes([0x1f, 0x8b, 0x08])):
            return '.gz'
        
        # TAR signature: ustar
        elif len(header) >= 262 and header[257:262] == b'ustar':
            return '.tar'
        
        # Executable formats
        # PE (Windows executable): MZ
        elif header.startswith(b'MZ'):
            return '.exe'
        
        # ELF (Linux executable): 7F 45 4C 46
        elif header.startswith(bytes([0x7f, 0x45, 0x4c, 0x46])):
            return '.elf'
        
        # Mach-O (macOS executable): FE ED FA CE or CE FA ED FE
        elif header.startswith(bytes([0xfe, 0xed, 0xfa, 0xce])) or \\
            header.startswith(bytes([0xce, 0xfa, 0xed, 0xfe])):
            return '.macho'
        
        # Alternative PNG detection for partial signatures
        elif header.startswith(bytes([0x89, 0x50, 0x4e, 0x47])) and len(header) >= 8:
            # Check if bytes 4-7 contain typical PNG continuation
            cr_lf = bytes([0x0d, 0x0a])
            sub1_lf = bytes([0x1a, 0x0a])
            if header[4:6] == cr_lf and header[6:8] == sub1_lf:
                return '.png'
        
        return '.bin'
    
    def save_binary_to_storage(binary_data, filename):
        """
        Save binary data to storage directory.
        
        Args:
            binary_data (bytes): Binary data to save
            filename (str): Name of the file to save
            
        Returns:
            str: Path to the saved file
        """
        storage_dir = '/storage'
        os.makedirs(storage_dir, exist_ok=True)
        
        file_path = os.path.join(storage_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(binary_data)
        
        return file_path
    
    # Initialize tool with credentials
    tool = ''' + tool_class_name + '''.from_credentials(
        credentials={
''' + credentials_code + '''        },
        user_id="''' + provider + '''_user"
    )

    # Invoke tool with parameters
    results = list(tool.invoke({
''' + parameters_code + '''    }))

    # Process and return results
    for result in results:
        if result.message:
            # Check if it's a blob message (binary data)
            if hasattr(result.message, 'blob') and result.message.blob:
                binary_data = result.message.blob
                
                # Detect file type
                file_extension = detect_file_type_from_binary(binary_data)
                
                # Generate unique filename
                unique_id = str(uuid.uuid4())
                filename = unique_id + file_extension
                
                # Save to storage
                saved_path = save_binary_to_storage(binary_data, filename)
                return {"nexus_ai_file_path":"file://"+ saved_path}
                
            elif hasattr(result.message, 'text'):
                return result.message.text
            else:
                return result.message
        else:
            return result

run_tool()
'''
        return tool_class_name, code
    
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
            
            tree = ast.parse(content)
            
            if tool_name:
                yaml_file_path = tool_file_path.replace('.py', '.yaml')
                if os.path.exists(yaml_file_path):
                    try:
                        import yaml
                        with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
                            yaml_config = yaml.safe_load(yaml_file)
                            yaml_tool_name = yaml_config.get('identity', {}).get('name', '')
                            
                            if yaml_tool_name == tool_name:
                                for node in ast.walk(tree):
                                    if isinstance(node, ast.ClassDef):
                                        for base in node.bases:
                                            if isinstance(base, ast.Name) and base.id == 'Tool':
                                                return node.name
                                            elif isinstance(base, ast.Attribute) and base.attr == 'Tool':
                                                return node.name
                                
                                raise ValueError(f"No Tool class found in {tool_file_path} for tool_name: {tool_name}")
                            else:
                                raise ValueError(f"Tool name mismatch. Expected: {tool_name}, Found: {yaml_tool_name}")
                    except Exception as yaml_error:
                        print(f"Warning: Could not parse YAML config for {tool_file_path}: {yaml_error}")
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
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
        _, code = self._discover_tool_and_generate_code(category, provider, tool_name, credentials, parameters)
        return code
    
    def run_sandbox_tool(self, category: str, provider: str, tool_name: str, 
                        credentials: dict, parameters, app_run_id: int = 0, workflow_id: int = 0) -> dict:
        """
        Run a tool through the sandbox API using inherited run_custom_code method.
        
        Args:
            category (str): Tool category (e.g., 't1')
            provider (str): Provider name
            tool_name (str): Tool name
            credentials (dict): Tool credentials
            parameters: Tool parameters (can be dict or ObjectVariable)
            
        Returns:
            dict: Raw response from sandbox API
        """
        current_file = os.path.realpath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        sandbox_path = os.path.join(project_root, 'docker', 'sandbox')
        tool_dir = os.path.join(sandbox_path, 'tools', category, provider)
        
        pip_packages = self.load_requirements_from_file(tool_dir)
        
        _, code = self._discover_tool_and_generate_code(category, provider, 
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
        
        # Use inherited run_custom_code method and return raw response
        return self.run_custom_code()