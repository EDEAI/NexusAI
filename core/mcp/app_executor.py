from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parent.parent))

from typing import Any, Dict, Optional, List
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

tools_db = CustomTools()
apps_db = Apps()
workflows_db = Workflows()
appRuns_db = AppRuns()
appNodeUserRelation_db = AppNodeUserRelation()
chatroomDrivenRecords_db = ChatroomDrivenRecords()


async def skill_run(
    skill_id: int,
    user_id: int,
    team_id: int,
    mcp_tool_args: Dict[str, Any]
) -> Dict[str, Any]:
    """Run the specified skill
    
    Args:
        skill_id: Skill ID
        user_id: User ID
        team_id: Team ID
        mcp_tool_args: MCP tool args
        
    Returns:
        Dict containing execution results
    """
    input_variables: Dict[str, Any] = mcp_tool_args['input_variables']
    # Parameter validation
    if skill_id <= 0:
        raise ValueError(get_language_content("skill_id_required"))

    if not input_variables:
        raise ValueError(get_language_content("input_dict_required"))

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
        
    input_obj = create_variable_from_dict(skill["input_variables"])
    for k, v in input_variables.items():
        if var := input_obj.properties.get(k):
            var.value = v

    # Execute skill
    task = run_app.delay(app_type="skill", id_=skill_id, user_id=user_id, input_dict=input_obj.to_dict())
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

async def workflow_run(
    workflow_id: int, 
    user_id: int, 
    team_id: int,
    mcp_tool_args: Dict[str, Any]
) -> Dict[str, Any]:
    """Run the specified workflow"""
    try:
        # Parameter type conversion
        user_id = int(user_id) if not isinstance(user_id, int) else user_id
        team_id = int(team_id) if not isinstance(team_id, int) else team_id
        node_confirm_users: Optional[Dict[str, List[int]]] = mcp_tool_args.get('node_confirm_users')
        if node_confirm_users:
            node_confirm_users = {
                node_id: [user_id if node_confirm_user_id == 0 else node_confirm_user_id]
                for node_id, node_confirm_user_id in node_confirm_users.items()
            }
        input_variables: Dict[str, Any] = mcp_tool_args['input_variables']

        # Input validation
        if not isinstance(input_variables, dict):
            raise ValueError("input_data must be a dictionary")

        # Parameter validation
        if workflow_id <= 0:
            raise ValueError(get_language_content("app_id_required"))

        if not input_variables:
            raise ValueError(get_language_content("input_data_required"))

        # Get workflow with all conditions
        workflow = workflows_db.select_one(
            columns=['id', 'graph', 'app_id'],
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
        if not isinstance(input_variables, Dict):
            raise ValueError(get_language_content("input_data_format_error"))
        
        for k, v in input_variables.items():
            if var := input_obj.properties.get(k):
                var.value = v
        
        validate_required_variable(input_obj)

        # Create app run record
        start_datetime_str = datetime.now().replace(microsecond=0).isoformat(sep='_')
        app_run_data = {
            'user_id': user_id,
            'app_id': workflow['app_id'],
            'workflow_id': workflow['id'],
            'type': 2,
            'name': f'Workflow_Run_{workflow["id"]}_{start_datetime_str}',
            'graph': graph.to_dict(),
            'inputs': input_obj.to_dict(),
            'status': 1,
            'total_steps': graph.get_total_steps()
        }

        app_run_id = appRuns_db.insert(app_run_data)

        if node_confirm_users:
            AppNodeUserRelation().create_data(app_run_id, node_confirm_users)

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
        return {'workflow_id': workflow['id'], 'app_run_id': app_run_id}
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise ValueError(f"Workflow execution failed: {str(e)}")

    