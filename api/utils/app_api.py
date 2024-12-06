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


app_api_routers: Dict[int, APIRouter] = {}


def get_api_app_ids() -> List[int]:
    """
    Gets a list of IDs of apps that are available for use with the Open API.
    """
    apps = Apps().select(
        columns=['id', 'mode'],
        conditions=[
            {'column': 'mode', 'op': 'in', 'value': [1, 2]},
            {'column': 'status', 'value': 1},
            {'column': 'publish_status', 'value': 1},
            {'column': 'enable_api', 'value': 1},
        ]
    )
    if not apps:
        return []
    
    agent_app_ids = []
    workflow_app_ids = []
    for app in apps:
        if app['mode'] == 1:
            agent_app_ids.append(app['id'])
        else:
            workflow_app_ids.append(app['id'])
    
    all_app_ids = []
    
    agents = Agents().select(
        columns=['app_id'],
        conditions=[
            {'column': 'app_id', 'op': 'in', 'value': agent_app_ids},
            {'column': 'status', 'value': 1},
            {'column': 'publish_status', 'value': 1}
        ]
    )
    all_app_ids.extend([agent['app_id'] for agent in agents])
    
    workflows = Workflows().select(
        columns=['app_id'],
        conditions=[
            {'column': 'app_id', 'op': 'in', 'value': workflow_app_ids},
            {'column': 'status', 'value': 1},
            {'column': 'publish_status', 'value': 1}
        ]
    )
    all_app_ids.extend([workflow['app_id'] for workflow in workflows])
    
    return all_app_ids


def get_app_api_router(app_id: int) -> Optional[APIRouter]:
    """
    Generate an API router for the given app ID.
    """
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
        return
    
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
        
    m = md5()
    m.update(f'APP-{app_id}'.encode())
    app_hash = m.hexdigest()
    
    # Generate APIs
    router = APIRouter()
    
    @router.post(f'/v1/app-api/{app_hash}/run', response_model=ResponseModel)
    async def run(
        authorization: Annotated[
            str, Header(description=f'API key, which should be "Bearer {app["api_token"]}" for this APP')
        ], input_: InputModel):  # type: ignore
        """
        Run the app with the given input.
        """
        # Get app info
        api_token_match = re.fullmatch(r'Bearer (.+)', authorization)
        assert api_token_match, 'Invalid authorization header'
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
        assert app, 'Invalid app API token, or the app is not published or enabled for API.'
        assert app['id'] == app_id, 'Incorrect API URL for this app'
        
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
                assert agent, 'No available agent, or the agent is not published.'
                
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
                assert workflow, 'No available workflow, or the workflow is not published.'
                
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
    
    @router.get(f'/v1/app-api/{app_hash}/run-openapi')
    async def run_openapi():
        """
        Get the OpenAPI schema for the app.
        """
        openapi_schema = get_openapi(
            title=app['name'],
            version='1.0.0',
            description=app['description'],
            routes=[route for route in router.routes if route.path == f'/v1/app-api/{app_hash}/run']
        )
        return openapi_schema
    
    @router.get(f'/v1/app-api/{app_hash}/run-docs')
    async def run_docs():
        """
        Get the documentation for the app.
        """
        return get_redoc_html(openapi_url=f'/v1/app-api/{app_hash}/run-openapi', title=app['name'])
    
    return router

def add_app_api(fastapi_app: FastAPI, app_id: int):
    """
    Add an API router for the given app ID.
    """
    if app_id in app_api_routers:
        app_api_router = app_api_routers.pop(app_id)
        for route in app_api_router.routes:
            fastapi_app.routes.remove(route)
    app_api_router = get_app_api_router(app_id)
    if app_api_router:
        fastapi_app.include_router(app_api_router, include_in_schema=False)
        app_api_routers[app_id] = app_api_router
    
def remove_app_api(fastapi_app: FastAPI, app_id: int):
    """
    Remove an API router for the given app ID.
    """
    app_api_router = app_api_routers.pop(app_id, None)
    if app_api_router:
        for route in app_api_router.routes:
            fastapi_app.routes.remove(route)
