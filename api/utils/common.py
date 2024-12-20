from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from uuid import uuid4
from fastapi import HTTPException
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration

import math

from config import settings
from core.database import SQLDatabase
from core.database.models import AIToolLLMRecords, AppRuns, Models
from core.llm import LLMPipeline, Messages

project_root = Path(__file__).absolute().parent.parent.parent
ai_tool_llm_records = AIToolLLMRecords()
app_runs = AppRuns()

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

async def call_llm_for_ai_tool(
    team_id: int,
    user_id: int,
    app_run_id: int,
    input_messages: Messages,
    return_json: bool = False
) -> str:
    model_info = Models().get_model_by_type(1, team_id, uid=user_id)
    llm_config = {**model_info['supplier_config'], **model_info['model_config']}
    if return_json:
        llm_config['model_kwargs'] = {'response_format': {'type': 'json_object'}}
    llm_pipeline = LLMPipeline(supplier=model_info['supplier_name'], config=llm_config)
    input_ = [(role, message.value) for role, message in input_messages.messages]

    # Request LLM
    result = await llm_pipeline.llm.agenerate([input_])
    result: ChatGeneration = result.generations[0][0]
    output_message: AIMessage = result.message

    # LLM output & token usage recording
    if usage_metadata := output_message.usage_metadata:
        prompt_tokens = usage_metadata['input_tokens']
        completion_tokens = usage_metadata['output_tokens']
        total_tokens = usage_metadata['total_tokens']
    ai_tool_llm_records.insert(
        {
            'app_run_id': app_run_id,
            'llm_input': input_,
            'message': output_message.content,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }
    )
    app_runs.increment_token_usage(
        app_run_id,
        prompt_tokens, completion_tokens, total_tokens
    )
    return output_message.content

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
