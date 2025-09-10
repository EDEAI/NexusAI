from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"

class RepeatType(str, Enum):
    NONE = "none"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class TaskStatus(int, Enum):
    ENABLED = 1
    DISABLED = 2
    PAUSED = 3
    DELETED = 4

class ExecutionStatus(int, Enum):
    SUCCESS = 1
    FAILED = 2
    RUNNING = 3

# Create scheduled task request model
class CreateScheduledTaskSchema(BaseModel):
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    task_type: TaskType = Field(..., description="Task type")
    app_id: int = Field(..., description="Application ID")
    workflow_id: int = Field(..., description="Workflow ID")
    input: Dict[str, Any] = Field(..., description="Input data")
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    repeat_type: RepeatType = Field(RepeatType.NONE, description="Repeat type")
    repeat_interval: int = Field(1, description="Repeat interval")
    repeat_days: List[int] = Field(default_factory=list, description="Repeat days")
    repeat_day_of_month: Optional[int] = Field(None, description="Day of month for monthly repeat")
    repeat_month: Optional[int] = Field(None, description="Month for yearly repeat")
    repeat_day_of_year: Optional[int] = Field(None, description="Day of year for yearly repeat")
    task_data: Dict[str, Any] = Field(..., description="Task data")
    node_confirm_users: Optional[Dict[str, Any]] = Field(None, description="Node confirmation users mapping")
    max_executions: int = Field(0, description="Maximum execution count")

# Update scheduled task request model
class UpdateScheduledTaskSchema(BaseModel):
    name: Optional[str] = Field(None, description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    task_type: Optional[TaskType] = Field(None, description="Task type")
    input: Optional[Dict[str, Any]] = Field(None, description="Input data")
    start_time: Optional[datetime] = Field(None, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    repeat_type: Optional[RepeatType] = Field(None, description="Repeat type")
    repeat_interval: Optional[int] = Field(None, description="Repeat interval")
    repeat_days: Optional[List[int]] = Field(None, description="Repeat days")
    repeat_day_of_month: Optional[int] = Field(None, description="Day of month for monthly repeat")
    repeat_month: Optional[int] = Field(None, description="Month for yearly repeat")
    repeat_day_of_year: Optional[int] = Field(None, description="Day of year for yearly repeat")
    task_data: Optional[Dict[str, Any]] = Field(None, description="Task data")
    node_confirm_users: Optional[Dict[str, Any]] = Field(None, description="Node confirmation users mapping")
    max_executions: Optional[int] = Field(None, description="Maximum execution count")
    status: Optional[TaskStatus] = Field(None, description="Task status")

# Scheduled task info model
class ScheduledTaskInfo(BaseModel):
    id: int
    name: str
    description: Optional[str]
    task_type: TaskType
    status: TaskStatus
    user_id: int
    app_id: int
    workflow_id: int
    input: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime]
    next_run_time: datetime
    repeat_type: RepeatType
    repeat_interval: int
    repeat_days: Optional[List[int]]
    repeat_day_of_month: Optional[int]
    repeat_month: Optional[int]
    repeat_day_of_year: Optional[int]
    task_data: Dict[str, Any]
    node_confirm_users: Optional[Dict[str, Any]]
    last_run_time: Optional[datetime]
    last_run_status: Optional[ExecutionStatus]
    execution_count: int
    max_executions: int
    created_at: datetime
    updated_at: datetime

# Scheduled task list data model
class ScheduledTaskListData(BaseModel):
    list: List[ScheduledTaskInfo]
    total_count: int
    total_pages: int
    page: int
    page_size: int

# Delete scheduled task request model
class DeleteScheduledTaskSchema(BaseModel):
    task_id: int = Field(..., description="Scheduled task ID")

# Scheduled task list query parameters
class ScheduledTaskListQuery(BaseModel):
    page: int = Field(1, description="Page number")
    page_size: int = Field(10, description="Page size")
    app_id: Optional[int] = Field(None, description="Application ID")
    name: Optional[str] = Field(None, description="Task name")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    task_type: Optional[TaskType] = Field(None, description="Task type")