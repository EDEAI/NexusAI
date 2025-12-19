import asyncio
import json

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parent.parent))
from typing import Any, Dict, List


async def _run_code(code_dependencies: List[str], custom_code: str, output_variable_descriptions: List[Dict[str, str]]) -> str:
    from core.workflow.nodes.base import SandboxBaseNode
    node = SandboxBaseNode(
        type='custom_code',
        title='Run Code',
        code_dependencies={'python3': code_dependencies},
        custom_code={'python3': custom_code}
    )
    result = await asyncio.to_thread(
        node.run_custom_code,
        is_tool=True
    )
    if result['status'] == 0:
        result = {
            'status': 'success',
            'outputs': {
                'result': result['data']['stdout'],
                'output_variable_descriptions': output_variable_descriptions
            },
            'file_list': []
        }
    else:
        result = {
            'status': 'failed',
            'message': result['data']['stderr'],
        }
    return result

async def run_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    if tool_name == 'run_code':
        return await _run_code(tool_args.get('code_dependencies', []), tool_args['custom_code'], tool_args.get('output_variable_descriptions', []))
    else:
        raise ValueError(f'Unknown tool: {tool_name}')

def get_builtin_tool_list() -> List[Dict[str, Any]]:
    run_code = {
        "name": 'nexusai__builtin-run_code',
        "description": 'Execute custom code in a secure sandbox environment. Supports Python3 code execution with optional package dependencies.',
        "inputSchema": {
            "type": "object",
            "properties": {
                "code_dependencies": {
                    "type": "array",
                    "description": "List of Python package dependencies required for the code execution",
                    "items": {
                        "type": "string"
                    },
                    "default": []
                },
                "custom_code": {
                    "type": "string",
                    "description": "The Python3 code to execute in the sandbox environment"
                },
                "output_variable_descriptions": {
                    "type": "array",
                    "description": "List of output variables with their descriptions",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the output variable"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of what the output variable represents"
                            }
                        },
                        "required": ["name", "description"]
                    },
                    "default": []
                }
            },
            "required": ["custom_code"]
        }
    }
    
    return [run_code]
