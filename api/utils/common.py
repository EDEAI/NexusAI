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

from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False)

project_root = Path(__file__).absolute().parent.parent.parent


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
                    "variable_name": var.name
                })
    return file_list

def replace_documents_with_strvars_in_context(outputs_var: Optional[ObjectVariable]) -> ObjectVariable:
    outputs_in_context = deepcopy(outputs_var)
    if outputs_var:
        for var_name, variable in outputs_var.properties.items():
            if variable.type == 'file':
                if var_value := variable.value:
                    file_path = None
                    if not variable.sub_type or variable.sub_type == 'document':
                        # Get file path
                        if isinstance(var_value, int):
                            # Upload file ID
                            file_data = UploadFiles().get_file_by_id(var_value)
                            file_path = project_root.joinpath(file_data['path'])
                        elif isinstance(var_value, str):
                            if var_value[0] == '/':
                                var_value = var_value[1:]
                            file_path = project_root.joinpath('storage').joinpath(var_value)
                        else:
                            # This should never happen
                            raise Exception('Unsupported value type!')
                    if not variable.sub_type:
                        # Tag file type
                        if file_path.suffix in ['.jpg', 'jpeg', '.png', '.gif', '.webp']:
                            variable.sub_type = 'image'
                            outputs_in_context.properties[var_name].sub_type = 'image'
                        else:
                            variable.sub_type = 'document'
                            string_var = Variable(name=var_name, type='string', value=md.convert(file_path).text_content)
                            outputs_in_context.add_property(var_name, string_var)
                    elif variable.sub_type == 'document':
                        string_var = Variable(name=var_name, type='string', value=md.convert(file_path).text_content)
                        outputs_in_context.add_property(var_name, string_var)
                else:
                    # No file
                    string_var = Variable(name=var_name, type='string', value='')
                    outputs_in_context.add_property(var_name, string_var)

    return outputs_in_context