import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from uuid import uuid4
from fastapi import HTTPException

import math
import os
from config import settings
from core.database import SQLDatabase
from core.database.models import UploadFiles
from core.workflow.variables import *

project_root = Path(__file__).absolute().parent.parent.parent


SKILL_PATH_PATTERN = r'^/skill/sk\d+/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-zA-Z0-9]+$'
WORKFLOW_PATH_PATTERN = r'^/workflow/wf\d+/[^/]+/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-zA-Z0-9]+$'
COMBINED_PATH_PATTERN = rf'^({SKILL_PATH_PATTERN[1:-1]}|{WORKFLOW_PATH_PATTERN[1:-1]})$'


def get_new_collection_name() -> str:
    """
    Get a new vector database collection name.
    """
    return f'Collection_{uuid4().hex}'

def convert_to_type_and_config(config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Convert the config to type and config.
    """
    type_ = config.pop('type', None)
    return type_, config

def get_vdb_type_and_config() -> Tuple[str, Dict[str, Any]]:
    """
    Get the vector database type and config.
    """
    return (
        settings.VDB_TYPE,
        {
            'host': settings.VDB_HOST,
            'port': settings.VDB_PORT,
            'user': settings.VDB_USER,
            'password': settings.VDB_PASSWORD
        }
    )

def response_success(data:Dict[str, Any] = {},detail:str = 'success',code:int = 0):
    """
    Return a success response.
    """
    SQLDatabase.commit()
    SQLDatabase.close()
    return {'code': code,'detail': detail,'data': data}

def response_error(msg:str = 'failed',status:int = 402):
    """
    Return an error response.
    """
    SQLDatabase.close()
    raise HTTPException(
            status_code=status,
            detail=msg
        )
    # return {'status': status,'msg': msg,'data': data}

def paging_result(page:int=1,page_size:int=10,total_count:int=0):
    """
    Get the paging result.
    """
    total_pages = math.ceil(total_count / page_size)
    if page == 1:
        return {'limit':page_size,'offset':0,'total_pages':total_pages}
    else:
        return {'limit':page_size,'offset':(page-1)*page_size,'total_pages':total_pages}
    
def extract_file_list_from_skill_output(outputs: dict, node_data_dict: dict) -> List[Dict[str, Any]]:
    """
    Extract the file list from the skill output.
    """
    file_list = []
    # outputs = result['data']['outputs']
    storage_url = f"{settings.STORAGE_URL}/file"
    output_vars = create_variable_from_dict(node_data_dict)
    for key, value in outputs.items():
        # Ensure path starts with /
        if not value.startswith('/'):
            value = '/' + value
        
        # Check if it's a skill path
        if re.match(SKILL_PATH_PATTERN, value):
            output_vars.properties[key].type = 'file'
        
        # Check if it's a workflow path
        if re.match(WORKFLOW_PATH_PATTERN, value):
            output_vars.properties[key].type = 'file'
    file_vars = output_vars.extract_file_variables()
    
    
    for var in file_vars.properties.values():
        if var.name in outputs:
            file_path = outputs[var.name]
            if file_path:
                if not file_path.startswith('/'):
                    file_path = '/' + file_path
                file_name = file_path.split('/')[-1]
                full_path = f"{storage_url}{file_path}"
                file_list.append({
                    "file_name": file_name,
                    "file_path": full_path,
                    "variable_name": var.display_name if hasattr(var, 'display_name') and var.display_name else var.name
                })
    return file_list
