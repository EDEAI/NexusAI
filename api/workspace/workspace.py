from fastapi import APIRouter
from api.utils.common import *
from api.utils.jwt import *
from api.schema.workspace import *
from core.database.models import (Workspaces,Workflows,AppRuns,Apps)


router = APIRouter()
@router.post("/workspace_list", response_model = ResWorkspaceListSchema)

async def workspace_list(tool: ReqWorkSpaceList, userinfo: TokenData = Depends(get_current_user)):
    """
    workspace list

    page: int, page number.
    page_size: int, quantity per page.
    """
    tool_data = tool.dict(exclude_unset=True)

    result = Workspaces().get_workspace_list(tool_data['page'],tool_data['page_size'], userinfo.uid, userinfo.team_id)

    return response_success(result)


@router.post("/workspace_workflow_log_list", response_model=ResWorkspacWorkflowLogListSchema)
async def workspace_workflow_log_list(tool: ReqWorkspaceWorkflowLogList, userinfo: TokenData = Depends(get_current_user)):
    """
    workspace workflow log list

    app_id: int, apps id
    page: int, page number.
    page_size: int, quantity per page.
    app_runs_name: string,app_runs name
    app_runs_status: int,app_runs status
    """
    tool_data = tool.dict(exclude_unset=True)

    if tool_data['app_id'] <= 0:
        return response_error("app_id is required")

    apps_info = Apps().select_one(columns=['id'], conditions=[{'column': 'id', 'value': tool_data['app_id']}])

    if not apps_info:
        return response_error("apps not found")

    result_workflow_log = Workspaces().get_workspace_workflow_log_list(tool_data['page'],tool_data['page_size'], tool_data['app_id'], tool_data['app_runs_name'], tool_data['app_runs_status'], userinfo.uid)

    return response_success(result_workflow_log)



@router.post("/workspace_workflow_log_info", response_model = ResWorkspaceWorkflowLogInfoSchema)

async def workspace_workflow_log_info(tool: ReqWorkspaceWorkflowLogInfo, userinfo: TokenData = Depends(get_current_user)):
    """
    workspace workflow log info

    workflows_id: int, workflows id
    app_runs_id: int, app_runs id.
    """
    tool_data = tool.dict(exclude_unset=True)

    if tool_data['workflows_id'] <= 0:
        return response_error("workflows_id is required")

    if tool_data['app_runs_id'] <= 0:
        return response_error("app_runs_id is required")

    workflow_info = Workflows().select_one(columns='*', conditions=[{'column': 'id', 'value': tool_data['workflows_id']}])

    if not workflow_info:
        return response_error("workflows not found")

    apprun_info = AppRuns().select_one(columns=['id'], conditions=[{'column': 'id', 'value': tool_data['app_runs_id']}])

    if apprun_info is None:
        return response_error("appruns not found")

    result = Workspaces().get_workflow_log_info(tool_data['workflows_id'],tool_data['app_runs_id'])

    return response_success(result)


@router.post("/workspace_workflow_process_log", response_model = ResWorkspaceWorkflowProcessLogSchema)

async def workspace_workflow_process_log( tool: ResWorkspaceWorkflowProcessLog,userinfo: TokenData = Depends(get_current_user)):
    """
    workspace workflow log info

    page: int, page number.
    page_size: int, quantity per page.
    """
    tool_data = tool.dict(exclude_unset=True)

    result = Workspaces().get_workflow_process_log(tool_data['page'],tool_data['page_size'],tool_data['show_status'], userinfo.uid)

    return response_success(result)




