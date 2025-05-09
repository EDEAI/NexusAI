from pathlib import Path
from typing import AsyncGenerator
import sys
sys.path.append(str(Path(__file__).absolute().parent.parent))
from typing import Any, Dict, Optional, List
from mcp.server.fastmcp import FastMCP
from core.database.models import CustomTools, Apps, Workflows, AppRuns, AppNodeUserRelation
from core.workflow.variables import create_variable_from_dict, validate_required_variable
from core.database.models.chatroom_driven_records import ChatroomDrivenRecords
from core.workflow.graph import create_graph_from_dict
from languages import get_language_content
import asyncio
from celery_app import run_app
from api.utils.common import *
from datetime import datetime
from copy import deepcopy
import json
import redis
from config import settings

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
    port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
    db=settings.REDIS_DB if hasattr(settings, 'REDIS_DB') else 0,
    password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
    decode_responses=True
)

# Initialize database models and FastMCP server
tools_db = CustomTools()
apps_db = Apps()
workflows_db = Workflows()
appRuns_db = AppRuns()
appNodeUserRelation_db = AppNodeUserRelation()
chatroomDrivenRecords_db = ChatroomDrivenRecords()
mcp = FastMCP("skill_runner",port = settings.MCP_SERVER_PORT)

@mcp.tool()
async def workflow_run(
    workflow_id: int, 
    input_data: Dict[str, Any], 
    user_id: int, 
    team_id: int,
    knowledge_base_mapping: Optional[Dict[str, Any]] = None,
    node_confirm_users: Optional[Dict[str, List[int]]] = None,
    data_source_run_id: Optional[int] = 0
) -> Dict[str, Any]:
    """Run the specified workflow"""
    try:
        # Parameter type conversion
        workflow_id = int(workflow_id) if not isinstance(workflow_id, int) else workflow_id
        user_id = int(user_id) if not isinstance(user_id, int) else user_id
        team_id = int(team_id) if not isinstance(team_id, int) else team_id
        data_source_run_id = int(data_source_run_id) if data_source_run_id and not isinstance(data_source_run_id, int) else data_source_run_id or 0

        # Input validation
        if not isinstance(input_data, dict):
            raise ValueError("input_data must be a dictionary")

        # Parameter validation
        if workflow_id <= 0:
            raise ValueError(get_language_content("app_id_required"))

        if not input_data:
            raise ValueError(get_language_content("input_data_required"))

        # Get workflow with all conditions
        workflow = workflows_db.select_one(
            columns=['id', 'user_id', 'graph', 'app_id'],
            conditions=[
                {'column': 'id', 'value': workflow_id},
                {'column': 'status', 'value': 1},
                {'column': 'publish_status', 'value': 1}
            ]
        )

        if not workflow:
            raise ValueError(f"No workflow found for workflow_id={workflow_id}")

        # Validate graph and prepare input
        graph = create_graph_from_dict(workflow['graph'])
        graph.validate()

        input_of_start_node = graph.nodes.nodes[0].data['input']
        input_obj = deepcopy(input_of_start_node)

        # Process input data
        if not isinstance(input_data, Dict):
            raise ValueError(get_language_content("input_data_format_error"))
        
        for k, v in input_data.items():
            if var := input_obj.properties.get(k):
                var.value = v
        
        validate_required_variable(input_obj)

        # Create app run record
        start_datetime_str = datetime.now().replace(microsecond=0).isoformat(sep='_')
        app_run_data = {
            'user_id': workflow['user_id'],
            'app_id': workflow['app_id'],
            'workflow_id': workflow['id'],
            'type': 2,
            'name': f'Workflow_Run_{workflow["id"]}_{start_datetime_str}',
            'graph': graph.to_dict(),
            'inputs': input_obj.to_dict(),
            'status': 1,
            'total_steps': graph.get_total_steps()
        }
        
        if knowledge_base_mapping is not None:
            app_run_data['knowledge_base_mapping'] = knowledge_base_mapping

        app_run_id = appRuns_db.insert(app_run_data)

        if data_source_run_id > 0:
            chatroomdriven_info = appNodeUserRelation_db.get_data_by_data_source_run_id(data_source_run_id)
            if chatroomdriven_info:
                appNodeUserRelation_db.update_data_driven_run_id(chatroomdriven_info['id'], data_source_run_id, app_run_id)

        if node_confirm_users:
            appNodeUserRelation_db.create_data(app_run_id, node_confirm_users)

        apps_db.increment_execution_times(workflow['app_id'])
        apps_db.commit()

        # Run workflow and wait for result
        # loop = asyncio.get_running_loop()
        # result = await loop.run_in_executor(
        #     None,
        #     redis_client.blpop,
        #     [f'app_run_{app_run_id}_result'],
        #     settings.APP_API_TIMEOUT
        # )
        
        # if result is None:
        #     raise ValueError('Timeout waiting for the workflow to complete')
            
        # result = json.loads(result[1])
        # if result['status'] != 'success':
        #     raise ValueError(result['message'])
            
        # outputs = create_variable_from_dict(result['data'])
        
        # return {
        #     "outputs": flatten_variable_with_values(outputs)
        # }
        return {'app_id': app_id, 'workflow_id': workflow['id'], 'app_run_id': app_run_id}
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise ValueError(f"Workflow execution failed: {str(e)}")

@mcp.tool()
async def skill_run(skill_id: int, input_dict: Dict[str, Any], user_id: int, team_id: int) -> Dict[str, Any]:
    """Run the specified skill
    
    Args:
        skill_id: Skill ID
        input_dict: Input parameters dictionary
        user_id: User ID
        team_id: Team ID
        
    Returns:
        Dict containing execution results
    """
    # Parameter validation
    if skill_id <= 0:
        raise ValueError(get_language_content("skill_id_required"))

    if not input_dict:
        raise ValueError(get_language_content("input_dict_required"))
        
    try:
        create_variable_from_dict(input_dict)
    except Exception as e:
        raise ValueError(get_language_content("input_dict_format_error"))

    # Get skill information
    skill = tools_db.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": skill_id},
            {"column": "team_id", "value": team_id},
            {"column": "status", "value": 1}
        ])
    if not skill:
        raise ValueError(get_language_content("skill_error"))

    # Validate user permissions
    if skill["user_id"] != user_id:
        if skill["status"] != 1:
            raise ValueError(get_language_content("skill_status_not_normal"))
        if skill["publish_status"] != 1:
            raise ValueError(get_language_content("skill_draft_creators_only"))

    # Validate application information
    app = apps_db.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": skill["app_id"]},
            {"column": "team_id", "value": team_id},
            {"column": "mode", "value": 4},
            {"column": "status", "value": 1}
        ]
    )

    if not app:
        raise ValueError(get_language_content("app_error"))
    if app["user_id"] != user_id:
        if app["is_public"] == 0:
            raise ValueError(get_language_content("team_members_not_open"))
        if app["status"] != 1:
            raise ValueError(get_language_content("app_status_not_normal"))

    # Execute skill
    task = run_app.delay(app_type="skill", id_=skill_id, user_id=user_id, input_dict=input_dict)
    while not task.ready():
        await asyncio.sleep(0.1)
    
    result = task.get()
    if result["status"] != "success":
        return {"outputs": {
            'error': result["message"]
        }}

    outputs = result["data"]["outputs"]
    file_list = []

    if skill and skill.get("output_variables"):
        file_list = extract_file_list_from_skill_output(outputs, skill["output_variables"])
    
    return {
        "outputs": outputs,
        "file_list": file_list
    }

if __name__ == "__main__":
    # Initialize and run server
    print("Server starting...")
    mcp.run(transport='sse')