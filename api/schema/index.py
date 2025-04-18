from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class BackLogsData(BaseModel):
    app_run_id: Optional[int] = None
    app_run_name: Optional[str] = None
    app_id: Optional[int] = None
    app_name: Optional[str] = None
    mode: Optional[int] = None
    node_execution_id: Optional[int] = None
    node_name: Optional[str] = None
    exec_id: Optional[int] = None
    need_human_confirm: Optional[int] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None
    avatar: Optional[str] = None


class MyAgentData(BaseModel):
    agent_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None


class MoreAgentData(BaseModel):
    agent_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None


class MyWorkflowData(BaseModel):
    workflows_id: Optional[int] = None
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    publish_status: Optional[int] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None
    workflow_published_time: Optional[str] = None


class MoreWorkflowData(BaseModel):
    workflows_id: Optional[int] = None
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None


class WorkflowLogData(BaseModel):
    app_run_id: Optional[int] = None
    app_runs_name: Optional[str] = None
    apps_name: Optional[str] = None
    workflow_id: Optional[int] = None
    created_time: Optional[datetime] = None
    elapsed_time: Optional[Decimal] = None
    status: Optional[int] = None
    completed_steps: Optional[int] = None
    total_steps: Optional[int] = None
    need_human_confirm: Optional[int] = None
    percentage: Optional[int] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None


class ListResponseData(BaseModel):
    backlogs: Optional[List[BackLogsData]] = None
    my_agent: Optional[List[MyAgentData]] = None
    more_agent: Optional[List[MoreAgentData]] = None
    my_workflow: Optional[List[MyWorkflowData]] = None
    more_workflow: Optional[List[MoreWorkflowData]] = None
    workflow_log: Optional[List[WorkflowLogData]] = None


class ResIndexSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ListResponseData] = None