import asyncio
import json

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parent.parent))
from typing import Any, Dict, List


async def _run_code(code_dependencies: Dict[str, List[str]], custom_code: Dict[str, str], output_variable_descriptions: List[Dict[str, str]]) -> str:
    from core.workflow.nodes.base import SandboxBaseNode
    node = SandboxBaseNode(
        type='custom_code',
        title='Code Runner',
        code_dependencies=code_dependencies,
        custom_code=custom_code
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
        args = json.loads(tool_args['params'])
        return await _run_code(args.get('code_dependencies', []), args['code'], args.get('output_variable_descriptions', []))
    else:
        raise ValueError(f'Unknown tool: {tool_name}')

def get_builtin_tool_list() -> List[Dict[str, Any]]:
    run_code = {
        "name": 'nexusai__builtin-run_code',
        "description": 'Execute custom code in a secure sandbox environment. Supports Python3 code execution with optional package dependencies.',
        "inputSchema": {
            "type": "object",
            "properties": {
                "params": {
                    "type": "string",
                    "description": "A JSON string that includes the Python code to run, any required dependencies, and descriptions of the output variables.",
                }
            },
            "required": ["params"]
        }
    }
    
    return [run_code]

def get_builtin_tool_name(tool: str) -> str:
    return {
        'run_code': 'Code Runner'
    }.get(tool, tool)
