from pydantic import BaseModel
from typing import Optional, List,Any,Dict
from datetime import datetime




class WorkflowProcessLog(BaseModel):
    app_run_id: Optional[int] = None
    apps_name: Optional[str] = None
    app_runs_name: Optional[str] = None
    workflow_id: Optional[int] = None
    created_time: Optional[datetime] = None
    elapsed_time: Optional[float] = None
    status: Optional[int] = None
    show_status: Optional[int] = None
    completed_steps: Optional[int] = None
    total_steps: Optional[int] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None
    chat_room_name: Optional[str] = None
    nickname: Optional[str] = None
    file_list: Optional[List[Dict[str, Any]]] = None
    driver_id: Optional[int] = None
    mode: Optional[int] = None
    associated_chat_room_name: Optional[str] = None
    
class WorkspaceWorkflowProcessLogResponseData(BaseModel):
    list: Optional[List[WorkflowProcessLog]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

class ResWorkspaceWorkflowProcessLogSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkspaceWorkflowProcessLogResponseData] = None


class WorkspaceList(BaseModel):
    app_id: Optional[int] = None
    name: Optional[str] = None
    process_name: Optional[str] = None
    type: Optional[int] = None
    chatroom_id: Optional[int] = None
    workflow_id: Optional[int] = None
    agent_id: Optional[int] = None
    last_agent_name: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
class WorkspaceListResponseData(BaseModel):
    list: Optional[List[WorkspaceList]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

class ResWorkspaceListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkspaceListResponseData] = None
class AppRunsLog(BaseModel):
    app_id: Optional[int] = None
    workflow_id: Optional[int] = None
    app_run_id: Optional[int] = None
    type: Optional[int] = None
    level: Optional[int] = None
    status: Optional[int] = None
    error: Optional[str] = None
    completed_steps: Optional[int] = None
    actual_completed_steps: Optional[int] = None
    need_human_confirm: Optional[int] = None
    elapsed_time: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    embedding_tokens: Optional[int] = None
    reranking_tokens: Optional[int] = None
    total_steps: Optional[int] = None
    finished_time: Optional[datetime] = None
    created_time: Optional[datetime] = None

class HumanConfirmInfo(BaseModel):
    user_id: Optional[int] = None
    nickname: Optional[str] = None

class WorkflowLogInfo(BaseModel):
    id: Optional[int] = None
    node_id: Optional[str] = None
    node_name: Optional[str] = None
    node_type: Optional[str] = None
    node_graph: Optional[Dict[str, Any]] = None
    inputs: Optional[Dict[str, Any]] = None
    prompt_data: Optional[list] = None
    status: Optional[int] = None
    error: Optional[str] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None
    outputs_md: Optional[str] = None
    elapsed_time: Optional[float] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None
    child_executions: Optional[List['WorkflowLogInfo']] = None
    need_human_confirm: Optional[int] = None
    human_confirm_info: Optional[List[HumanConfirmInfo]] = None
    file_list: Optional[List[Dict[str, Any]]] = None

class WorkspaceWorkflowLogInfoResponseData(BaseModel):
    list: Optional[List[WorkflowLogInfo]] = None
    app_run_data: Optional[List[AppRunsLog]] = None

class ResWorkspaceWorkflowLogInfoSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkspaceWorkflowLogInfoResponseData] = None


class WorkspacWorkflowLogAppNodeListData(BaseModel):
    node_id: Optional[int] = None
    node_name: Optional[str] = None
    node_graph: Optional[Dict[str, Any]] = None
    inputs: Optional[Dict[str, Any]] = None
    mod_data: Optional[Dict[str, Any]] = None
    status: Optional[int] = None
    error: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None
    elapsed_time: Optional[float] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None

class WorkspacWorkflowLogListData(BaseModel):
    workflow_id: Optional[int] = None
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    app_runs_id: Optional[int] = None
    app_runs_name: Optional[str] = None
    nickname: Optional[str] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None
    total_tokens: Optional[int] = None
    app_runs_type: Optional[int] = None
    app_runs_level: Optional[int] = None
    elapsed_time: Optional[float] = None
    app_runs_status: Optional[int] = None
    completed_steps: Optional[int] = None
    total_steps: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None
    # app_node_list: Optional[List[WorkspacWorkflowLogAppNodeListData]] = None

class WorkspacWorkflowLogListResponseData(BaseModel):
    list: Optional[List[WorkspacWorkflowLogListData]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

class ResWorkspacWorkflowLogListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkspacWorkflowLogListResponseData] = None

class ReqWorkSpaceList(BaseModel):
    page: int = 1
    page_size: int = 10

class ReqWorkspaceWorkflowLogList(BaseModel):
    page: int = 1
    page_size: int = 10
    app_id: int
    app_runs_name: str = ''
    app_runs_status: int = 0

class ReqWorkspaceWorkflowLogInfo(BaseModel):
    workflows_id: int
    app_runs_id: int
class ResWorkspaceWorkflowProcessLog(BaseModel):
    page: int = 1
    page_size: int = 10
