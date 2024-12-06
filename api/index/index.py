import json
from fastapi import APIRouter
from api.utils.common import *
from api.utils.jwt import *
from api.schema.index import *

from core.database.models import (
    AppRuns,
    Agents,
    Workflows
)

router = APIRouter()


@router.get("/",response_model=ResIndexSchema)
async def index(userinfo: TokenData = Depends(get_current_user)):
    user_id = userinfo.uid
    team_id = userinfo.team_id

    # BackLogs
    app_runs_model = AppRuns()
    result = app_runs_model.get_backlogs_list({"user_id": user_id, "page_size": 10, "page": 1})
    if result['list']:
        backlogs = result['list']
    else:
        backlogs = []

    # My Agent
    agents_model = Agents()
    my_agent = agents_model.get_agent_list(1, 10, user_id, team_id, 1)
    if my_agent:
        my_agent = my_agent['list']
    else:
        my_agent = []

    # More agents
    agents_model = Agents()
    more_agent = agents_model.get_agent_list(1, 10, user_id, team_id, 2)
    if more_agent:
        more_agent = more_agent['list']
    else:
        more_agent = []

    # My Workflow
    workflows_model = Workflows()
    my_workflow = workflows_model.get_workflows_list(1, 10, user_id, team_id, 1)
    if my_workflow:
        my_workflow = my_workflow['list']
    else:
        my_workflow = []

    # More workflows
    workflows_model = Workflows()
    more_workflow = workflows_model.get_workflows_list(1, 10, user_id, team_id, 2)
    if more_workflow:
        more_workflow = more_workflow['list']
    else:
        more_workflow = []

    # Process Dash Board
    workflow_log = app_runs_model.get_workflow_log({"user_id": user_id,"page_size": 10})
    if workflow_log:
        for item in workflow_log:
            if item['status'] in (1, 2):
                item['status'] = 1
            elif item['status'] == 3:
                item['status'] = 2
            elif item['status'] == 4:
                item['status'] = 3
            if item['completed_steps'] and item['total_steps']:
                item['percentage'] = int((item['completed_steps'] / item['total_steps']) * 100)
            else:
                item['percentage'] = 0
    else:
        workflow_log = []

    return response_success({"backlogs": backlogs, "my_agent": my_agent, "more_agent": more_agent, "my_workflow": my_workflow, "more_workflow": more_workflow, "workflow_log": workflow_log})
