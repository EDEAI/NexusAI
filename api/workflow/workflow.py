import json
import os
import traceback
import random
import yaml

from fastapi import APIRouter, File, Request, Response, UploadFile, WebSocket, WebSocketDisconnect
from api.utils.common import *
from api.utils.connection import ConnectionManager
from api.utils.jwt import *
from api.schema.workflows import *
from api.schema.base import *
from core.database.models import Workflows, AgentDatasetRelation, Apps
from celery_app import run_node
from pprint import pp

from core.database.models.app_node_user_relation import AppNodeUserRelation
from core.workflow import *
from pydantic import BaseModel, Field
from core.database import redis
from core.workflow.nodes import create_node_from_dict
from fastapi.responses import HTMLResponse

from languages import get_language_content

router = APIRouter()


@router.get("/workflows_list", response_model=ResWorkflowsListSchema)
async def workflows_list(page: int = 1, page_size: int = 10, workflows_search_type: int = 1, name: str = "",
                         userinfo: TokenData = Depends(get_current_user)):
    """


    page: int, page number.
    page_size: int, quantity per page.
    workflows_search_type: int, workflows search type 1: my workflows 2: team workflows 3: my workflows.
    name: app and workflows name.
    """
    workflows_model = Workflows()
    result = workflows_model.get_workflows_list(page, page_size, userinfo.uid, userinfo.team_id, workflows_search_type,
                                                name)
    return response_success(result)


@router.get("/workflows_info/{app_id}", response_model=ResWorkflowsInfoSchema)
async def workflows_info(app_id: int, publish_status: int, userinfo: TokenData = Depends(get_current_user)):
    """
    workflows info

    app_id: int, App id
    publish_status: int, Workflow publish status 0: Draft 1: Published
    """
    if app_id <= 0:
        return response_error("app_id is required")
    if publish_status not in [0, 1]:
        return response_error("publish_status can only input 0 or 1")

    workflows_model = Workflows()
    result = workflows_model.workflows_info(app_id, publish_status, userinfo.uid, userinfo.team_id)
    if result["status"] != 1:
        return response_error(result["message"])
    return response_success(result["data"])


@router.put("/publish/{app_id}", response_model=ResWorkflowsPublish)
async def publish(request: Request, app_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    workflow publish

    app_id: int, App id

    """
    try:
        workflows_model = Workflows()
        apps = Apps()
        
        draft_info = workflows_model.get_draft_workflow(app_id, userinfo.uid, userinfo.team_id)
        if not draft_info:
            return response_error(get_language_content("no_available_workflows"))
        create_graph_from_dict(draft_info['graph']).validate()
        
        result = workflows_model.publish_workflows(app_id, userinfo.uid, userinfo.team_id)
        if result:
            # get apps info
            apps_info = apps.get_app_find(app_id, userinfo.uid, userinfo.team_id)
            return response_success({
                'result': get_language_content("publish_success")
            })
        else:
            return response_error(get_language_content("publish_failed"))
    except Exception as e:
        return response_error(str(e))


@router.get("/workflow_log/{app_id}", response_model=ResWorkflowLogListSchema)
async def workflow_log(page: int = 1, page_size: int = 10, app_id: int = 0, app_runs_name: str = "", app_runs_status: int = 0,
                       userinfo: TokenData = Depends(get_current_user)):
    """
    workflow log
    
    app_id: int, App id
    """
    workflows_model = Workflows()
    result = workflows_model.get_workflow_log(page, page_size, app_id, app_runs_name, app_runs_status, userinfo.uid)
    return response_success(result)


@router.post("/node_run", response_model=ResWorkflowsNodeRun)
async def node_run(data: WorkflowsNodeRunSchema,
                   userinfo: TokenData = Depends(get_current_user)):
    """
        workflow node run

        app_id: int, App id
        node_id: int, Node id
        """
    try:
        app_id = data.app_id
        child_node_id = None
        if data.parent_node_id:
            node_id, child_node_id = data.parent_node_id, data.node_id
        else:
            node_id = data.node_id
        node_data = {}
        workflows_model = Workflows()
        draft_info = workflows_model.node_run_info(app_id, node_id, userinfo.uid, userinfo.team_id)
        graph = create_graph_from_dict(draft_info['graph'])
        nodes = graph.nodes.to_dict()
        for node_item in nodes:
            if node_id == node_item['id']:
                node_data = node_item
        if not node_data:
            raise ValueError(get_language_content('node_id_is_not_exist'))
        if child_node_id:
            if not (executor_list := node_data['data'].get('executor_list')):
                raise ValueError(get_language_content('parent_node_is_not_rte_node'))
            node_data = {}
            for node_item in executor_list:
                if child_node_id == node_item['id']:
                    node_data = node_item
            if not node_data:
                raise ValueError(get_language_content('executor_not_exist'))
        context = create_context_from_dict(data.context)
        inputs = data.inputs
        if inputs:
            inputs = create_variable_from_dict(inputs)
        node_data = create_node_from_dict(node_data)
        task = run_node.delay(
            node_data.to_dict(),
            inputs.to_dict() if inputs else None,
            userinfo.uid,
            draft_info['id'],
            context.to_dict()
        )
        result = task.get(timeout=100)
        return response_success(result)
    except Exception as e:
        return response_error(str(e))


@router.post("/run", response_model=ResWorkflowsNodeRun)
async def run(data: WorkflowsRunSchema,
              userinfo: TokenData = Depends(get_current_user)):
    """
    workflow run

    app_id: int, App id
    run_type：int, run type 0: draft 1: published
    run_name: str, run name
    inputs: user inputs
    node_confirm_users: user node confirm
    """
    try:
        app_id = data.app_id
        run_type = data.run_type
        run_name = data.run_name
        inputs = data.inputs
        knowledge_base_mapping = data.knowledge_base_mapping
        node_confirm_users = data.node_confirm_users
        return response_success(
            start_workflow(userinfo.team_id, userinfo.uid, app_id, run_type, run_name, inputs, knowledge_base_mapping, node_confirm_users))
    except Exception as e:
        return response_error(str(e))


@router.put("/workflow_app_update/{app_id}", response_model=RespBaseSchema)
async def workflow_app_update(request: Request, app_id: int, data: ReqWorkflowsAppUpdateSchema,
                              userinfo: TokenData = Depends(get_current_user)):
    """
    Updates an existing workflow associated with the workflow.

    :param app_id: An integer representing the app ID.
    :return: A dictionary representing the result record.

    """
    is_public = data.is_public
    enable_api = data.enable_api
    graph = data.graph
    # features = data.features

    # verify params
    
    if is_public not in [0, 1]:
        return response_error(get_language_content("is_public can only input 0 or 1"))
    if enable_api not in [0, 1]:
        return response_error(get_language_content("enable_api can only input 0 or 1"))
    if graph:

        try:
            graph_res = create_graph_from_dict(graph)
            if graph_res:
                graph = graph_res.to_dict()

        except:
            return response_error(get_language_content("graph data in wrong format"))

    workflows_model = Workflows()
    result = workflows_model.workflow_app_update(app_id, userinfo.uid, is_public, enable_api, graph)

    if result['status'] == 1:
        return response_success(result['data'])

    elif result['status'] == 2:
        return response_error(get_language_content(result['message']))


@router.delete("/workflow_app_delete/{app_id}", response_model=RespBaseSchema)
async def workflow_app_delete(request: Request, app_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Deletes an existing workflow associated with the workflow.

    :param app_id: An integer representing the app ID.
    :return: A dictionary representing the result record.

    """

    workflows_model = Workflows()
    result = workflows_model.workflow_app_delete(app_id, userinfo.uid)

    if result['status'] == 1:
        return response_success(result['data'])

    elif result['status'] == 2:
        return response_error(get_language_content(result['message']))

@router.get("/workflow_start_condition/{app_id}", response_model=ResWorkflowStartConditionSchema)
async def workflow_start_condition(app_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Get the start condition of a workflow.

    Params:
        app_id: int, App ID
        
    Returns:
        app_id: int, App ID
        workflow_id: int, Workflow ID
        publish_status: int, Publish status
        start_node: dict, Start node info
        need_confirm_nodes: list, List of nodes that need manual confirmation
    """
    workflow_model = Workflows()
    workflow_info = workflow_model.get_published_workflow(app_id)
    if not workflow_info:
        return response_error("Workflow not found")
    
    graph_data = workflow_info["graph"]
    graph = create_graph_from_dict(graph_data)
    
    need_confirm_nodes = []
    for node in graph.nodes.nodes:
        if node.data['type'] == 'human' or node.data.get("manual_confirmation", False):
            node_name = node.data.get("title", "")
            need_confirm_nodes.append({'node_id': node.id, 'node_name': node_name})
            if node.data['type'] == 'recursive_task_execution' and node.data.get('executor_list', None):
                for child_node in node.data['executor_list'].nodes:
                    need_confirm_nodes.append({'node_id': child_node.id, 'node_name': f"{node_name}.{child_node.data.get('title', '')}"})
    
    return response_success({
        "app_id": app_id,
        "workflow_id": workflow_info["workflow_id"],
        "publish_status": workflow_info["publish_status"],
        "start_node": graph.nodes.nodes[0].to_dict(),
        "need_confirm_nodes": need_confirm_nodes
    })

@router.get("/export/{app_id}")
async def export(app_id: int, publish_status: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Export the workflow as a YAML file.

    This endpoint allows authenticated users to export a specific workflow
    identified by its app_id. The workflow data is converted to YAML format
    and returned as a downloadable file.

    Parameters:
    - app_id (int): The unique identifier of the app/workflow to be exported.
    - publish_status (int): Workflow publish status 0: Draft 1: Published

    Returns:
    - Response: A FastAPI Response object containing the YAML content of the workflow.
                The response is set up to be downloaded as a file by the client.
    """
    if app_id <= 0:
        return response_error("app_id is required")
    if publish_status not in [0, 1]:
        return response_error("publish_status can only input 0 or 1")

    workflows_model = Workflows()
    result = workflows_model.workflows_info(app_id, publish_status, userinfo.uid, userinfo.team_id)
    if result["status"] != 1:
        return response_error(result["message"])
    app_info = result["data"]["app"]
    workflow_info = result["data"]["workflow"]
    yaml_content = yaml.dump(
        {
            "app": {
                "name": app_info["name"],
                "description": app_info["description"],
                "icon": app_info["icon"],
                "icon_background": app_info["icon_background"],
                "mode": app_info["mode"]
            },
            "workflow": {
                "graph": workflow_info["graph"],
                "features": workflow_info["features"]
            }
        },
        allow_unicode=True
    )
    return Response(
        content=yaml_content,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": f"attachment; filename=workflow_{app_id}.yml"
        }
    )

@router.post("/import", response_model=ResWorkflowImportSchema)
async def import_(
    file: UploadFile = File(...),
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Import a workflow YAML file.

    This endpoint allows authenticated users to upload and import a workflow YAML file.
    The file content will be parsed and used to create a new workflow.

    Parameters:
    - file (UploadFile): YAML file containing the workflow data.

    Returns:
    - Dict: A dictionary containing information about the newly created workflow.
    """
    try:
        team_id = userinfo.team_id
        uid = userinfo.uid
        app_model = Apps()

        # Read and parse the YAML file
        content = await file.read()
        yaml_data = yaml.safe_load(content)

        # Extract app and workflow information
        try:
            app_info = yaml_data["app"]
            workflow_info = yaml_data["workflow"]
        except KeyError as e:
            return response_error(f'{get_language_content("workflow_import_item_is_required")}{e}')

        try:
            name = app_info["name"]
            mode = app_info["mode"]
            description = app_info["description"]
            icon = app_info["icon"]
            icon_background = app_info["icon_background"]
            graph = workflow_info["graph"]
            features = workflow_info["features"]
        except KeyError as e:
            return response_error(f'{get_language_content("workflow_import_item_is_required")}{e}')

        if not name:
            return response_error(get_language_content("workflow_import_name_is_required"))
        if mode != 2:
            return response_error(get_language_content("workflow_import_mode_error"))
        
        # Check if workflow with same name exists
        copy_str = get_language_content("workflow_import_copy")
        n = 1
        new_name = name
        while True:
            existing_app = app_model.select_one(
                columns=['name'],
                conditions=[
                    {'column': 'name', 'value': new_name},
                    {'column': 'team_id', 'value': team_id},
                    {'column': 'mode', 'value': 2},
                    {'column': 'status', 'op': 'in', 'value': [1, 2]}
                ]
            )
            if not existing_app:
                break
            
            if n == 1:
                new_name = f"{name} - {copy_str}"
            else:
                new_name = f"{name} - {copy_str} {n}"
            n += 1

        try:
            graph_res = create_graph_from_dict(graph)
            graph = graph_res.to_dict()
        except:
            return response_error(get_language_content("workflow_import_graph_error"))

        # create app
        new_name = new_name[:50]
        apps_data = {
            "team_id": team_id,
            "user_id": uid,
            "name": new_name,
            "icon": icon,
            "icon_background": icon_background,
            "description": description,
            "mode": mode,
            "is_public": 0
        }
        app_id = app_model.insert(apps_data)
        if not app_id:
            return response_error(get_language_content("workflow_import_insert_error"))

        # create workflow
        workflow_data = {
            "team_id": team_id,
            "user_id": uid,
            "app_id": app_id,
            "graph": graph,
            "features": features
        }
        workflows_model= Workflows()
        workflow_id = workflows_model.insert(workflow_data)
        if not workflow_id:
            return response_error(get_language_content("workflow_import_insert_error"))

        return response_success({
            "message": "Workflow imported successfully",
            "app_id": app_id
        })
    except yaml.YAMLError:
        return response_error(get_language_content("workflow_import_invalid_format"))
    except Exception as e:
        return response_error(f"Error occurred during import: {str(e)}")
    
@router.post("/copy/{app_id}", response_model=ResWorkflowCopySchema)
async def copy(
    app_id: int,
    publish_status: int,
    new_name: str,
    new_description: str,
    new_icon: str,
    new_icon_background: str,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Copy a workflow

    This endpoint creates a copy of an existing workflow, including its associated app.
    """
    try:
        uid = userinfo.uid
        team_id = userinfo.team_id
        
        if app_id <= 0:
            return response_error("app_id is required")
        if publish_status not in [0, 1]:
            return response_error("publish_status can only input 0 or 1")

        workflows_model = Workflows()
        result = workflows_model.workflows_info(app_id, publish_status, userinfo.uid, userinfo.team_id)
        if result["status"] != 1:
            return response_error(result["message"])
        workflow_info = result["data"]["workflow"]

        # Create a copy of the app
        new_app_data = {
            "team_id": team_id,
            "user_id": uid,
            "name": new_name,
            "icon": new_icon,
            "icon_background": new_icon_background,
            "description": new_description,
            "mode": 2,
            "is_public": 0
        }
        app_model = Apps()
        new_app_id = app_model.insert(new_app_data)
        if not new_app_id:
            return response_error("Failed to create copy of app")

        # Create a copy of the workflow
        new_workflow_data = {
            "team_id": team_id,
            "user_id": uid,
            "app_id": new_app_id,
            "graph": workflow_info['graph'],
            "features": workflow_info['features']
        }
        new_workflow_id = workflows_model.insert(new_workflow_data)
        if not new_workflow_id:
            return response_error("Failed to create copy of workflow")

        return response_success({
            "message": "Workflow copied successfully",
            "new_app_id": new_app_id
        })
    except Exception as e:
        return response_error(f"Error occurred during workflow copy: {str(e)}")
