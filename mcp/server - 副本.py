from pathlib import Path
from typing import AsyncGenerator
import sys
sys.path.append(str(Path(__file__).absolute().parent.parent))
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from core.database.models import CustomTools, Apps
from core.workflow.variables import create_variable_from_dict
from languages import get_language_content
import asyncio
from celery_app import run_app
from api.utils.common import *

# Initialize database models and FastMCP server
tools_db = CustomTools()
apps_db = Apps()
mcp = FastMCP("skill_runner")

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
        print(f"Debug - Variable Creation Error: {str(e)}")
        raise ValueError(get_language_content("input_dict_format_error"))

    # Get skill information
    skill = tools_db.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": skill_id},
            {"column": "team_id", "value": team_id},
            {"column": "status", "op": "in", "value": [1, 2]}
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
            {"column": "status", "op": "in", "value": [1, 2]}
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
    mcp.run(transport='stdio')