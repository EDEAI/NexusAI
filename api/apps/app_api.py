import asyncio
import json
import sys
import re

from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

from datetime import datetime
from hashlib import md5
from typing import Annotated, Dict, Optional

from fastapi import APIRouter, FastAPI, Header
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from api.utils.common import *
from core.helper import decrypt_id
from celery_app import run_app
from config import settings
from core.database import redis
from core.database.models import AppRuns, Apps, Agents, Workflows
from core.llm import Prompt
from core.workflow import (
    create_variable_from_dict,
    create_graph_from_dict,
    convert_to_fastapi_model,
    flatten_variable_with_values,
    unflatten_dict_with_values,
    validate_required_variable
)

router = APIRouter()


@router.post('/{encrypted_id}/run')
async def run(
    authorization: Annotated[str, Header(description='API key')],
    encrypted_id: str,
    input_: Any
):  # type: ignore
    """
    Run the app with the given input.
    """
    try:
        app_id = decrypt_id(encrypted_id)
    except:
        return response_error('Invalid URL')
    # Get app info
    api_token_match = re.fullmatch(r'Bearer (.+)', authorization)
    if not api_token_match:
        return response_error('Invalid authorization header')
    api_token = api_token_match.group(1)
    app = Apps().select_one(
        columns=['id', 'mode'],
        conditions=[
            {'column': 'api_token', 'value': api_token},
            {'column': 'mode', 'op': 'in', 'value': [1, 2]},
            {'column': 'status', 'value': 1},
            {'column': 'publish_status', 'value': 1},
            {'column': 'enable_api', 'value': 1}
        ]
    )
    if app is None:
        return response_error('Invalid app API token, or the app is not published or enabled for API.')
    if not app['id'] == app_id:
        return response_error('Incorrect API URL for this app')

    # Run app
    match app['mode']:
        case 1:  # Agent
            # Get agent info
            agent = Agents().select_one(
                columns=['id', 'input_variables'],
                conditions=[
                    {'column': 'app_id', 'value': app_id},
                    {'column': 'status', 'value': 1},
                    {'column': 'publish_status', 'value': 1}
                ]
            )
            if not agent:
                return response_error('No available agent, or the agent is not published.')
            
            # Get agent input and prompt
            input_obj = create_variable_from_dict(agent['input_variables'])
            prompt = Prompt(user=input_.prompt)
            
            # Run agent
            task = run_app.delay(
                app_type='agent',
                id_=agent['id'],
                user_id=0,
                input_dict=input_obj.to_dict(),
                ability_id=0,
                prompt=prompt.to_dict()
            )
            while not task.ready():
                await asyncio.sleep(0.1)
            result = task.get(timeout=settings.APP_API_TIMEOUT)
            if result['status'] != 'success':
                return response_error(result['message'])
            return response_success(result['data']['outputs'])
        case 2:  # Workflow
            # Get workflow info
            workflow = Workflows().select_one(
                columns=['id', 'user_id', 'graph'],
                conditions=[
                    {'column': 'app_id', 'value': app_id},
                    {'column': 'status', 'value': 1},
                    {'column': 'publish_status', 'value': 1}
                ]
            )
            if not workflow:
                return response_error('No available workflow, or the workflow is not published.')
            
            # Get workflow input
            input_data: Dict[str, Union[int | float | str]] = input_.input_data.dict()
            input_obj = unflatten_dict_with_values(input_data, 'input_var')
            validate_required_variable(input_obj)

            # Check the input
            graph = create_graph_from_dict(workflow['graph'])
            graph.validate()
            
            # Create app run record
            start_datetime_str = datetime.now().replace(microsecond=0).isoformat(sep='_')
            app_run_data = {
                'user_id': workflow['user_id'],
                'app_id': app_id,
                'workflow_id': workflow['id'],
                'type': 2,
                'name': f'Workflow_Run_{workflow["id"]}_{start_datetime_str}',
                'graph': graph.to_dict(),
                'inputs': input_obj.to_dict(),
                'status': 1,
                'total_steps': graph.get_total_steps()
            }
            app_run_id = AppRuns().insert(app_run_data)
            Apps().increment_execution_times(app_id)

            # Run workflow
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                redis.blpop,
                (f'app_run_{app_run_id}_result', settings.APP_API_TIMEOUT)
            )
            if result is None:
                return response_error('Timeout waiting for the workflow to complete')
            result = json.loads(result[1])
            if result['status'] != 'success':
                return response_error(result['message'])
            outputs = create_variable_from_dict(result['data'])
            return response_success(flatten_variable_with_values(outputs))
        case _:
            # This should never happen
            return response_error('Invalid app mode')
    
@router.get('/{encrypted_id}/run-openapi')
async def run_openapi(encrypted_id: str):
    """
    Get the OpenAPI schema for the app.
    """
    try:
        app_id = decrypt_id(encrypted_id)
    except:
        return response_error('Invalid URL')
    app = Apps().select_one(
        columns=['name', 'description', 'mode', 'api_token'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'mode', 'op': 'in', 'value': [1, 2]},
            {'column': 'status', 'value': 1},
            {'column': 'publish_status', 'value': 1},
            {'column': 'enable_api', 'value': 1}
        ]
    )
    if app is None:
        return response_error('App is not published or enabled for API.')
    
    # Get the input model
    match app['mode']:
        case 1:
            agent = Agents().select_one(
                columns=['input_variables'],
                conditions=[
                    {'column': 'app_id', 'value': app_id},
                    {'column': 'status', 'value': 1},
                    {'column': 'publish_status', 'value': 1}
                ]
            )
            if agent is None:
                return
            class InputModel(BaseModel):
                prompt: str
            class OutputModel(BaseModel):
                text: str
        case 2:
            workflow = Workflows().select_one(
                columns=['graph'],
                conditions=[
                    {'column': 'app_id', 'value': app_id},
                    {'column': 'status', 'value': 1},
                    {'column': 'publish_status', 'value': 1}
                ]
            )
            if workflow is None:
                return
            graph = create_graph_from_dict(workflow['graph'])
            InputModel = convert_to_fastapi_model(f'App{app_id}', graph.nodes.nodes[0].data['input'])
            OutputModel = Dict[str, str]
        case _:
            # This should never happen
            raise ValueError('Invalid app mode')
    
    class ResponseModel(BaseModel):
        code: Optional[int] = None
        detail: Optional[str] = None
        data: Optional[OutputModel] = None
    
    # Generate dummy router
    dummy_router = APIRouter()
    @dummy_router.post(f'/v1/app-api/{encrypted_id}/run', response_model=ResponseModel)
    async def run(
        authorization: Annotated[
            str, Header(description=f'API key, which should be "Bearer {app["api_token"]}" for this APP')
        ], input_: InputModel):  # type: ignore
        pass

    openapi_schema = get_openapi(
        title=app['name'],
        version='1.0.0',
        description=app['description'],
        routes=dummy_router.routes
    )
    return openapi_schema

@router.get('/{encrypted_id}/run-docs')
async def run_docs(encrypted_id: str):
    """
    Get the documentation for the app.
    """
    try:
        app_id = decrypt_id(encrypted_id)
    except:
        return response_error('Invalid URL')
    app = Apps().select_one(
        columns=['name'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'mode', 'op': 'in', 'value': [1, 2]},
            {'column': 'status', 'value': 1},
            {'column': 'publish_status', 'value': 1},
            {'column': 'enable_api', 'value': 1}
        ]
    )
    if app is None:
        return response_error('App is not published or enabled for API.')
    return get_redoc_html(openapi_url=f'/v1/app-api/{encrypted_id}/run-openapi', title=app['name'])
