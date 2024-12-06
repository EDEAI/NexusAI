from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from uuid import uuid4
from fastapi import HTTPException

import math

from config import settings
from core.database import SQLDatabase

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
