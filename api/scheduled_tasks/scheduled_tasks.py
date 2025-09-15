from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from core.database.models.scheduled_tasks import ScheduledTasks
from core.database.models.upload_files import UploadFiles
from api.schema.scheduled_tasks import *
from api.schema.base import RespBaseSchema
from api.utils.common import *
from api.utils.jwt import *
import json
import sys
import os
from time import time
from datetime import datetime
from languages import get_language_content

router = APIRouter()


@router.post("/create", response_model=RespBaseSchema)
async def create_scheduled_task(
    data: CreateScheduledTaskSchema,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Create a new scheduled task for workflow execution.
    
    This endpoint allows users to create scheduled tasks that can execute workflows
    at specified intervals or at a specific time. The task can be configured for
    one-time execution or recurring execution with various repeat patterns.
    
    Parameters:
    - name: Task name (required, must be non-empty string)
    - description: Task description (optional, provides context about the task)
    - task_type: Task type - either "one_time" for single execution or "recurring" for repeated execution
    - app_id: Application ID that the task belongs to (required, must exist and be accessible by user)
    - workflow_id: Workflow ID to be executed (required, must exist within the specified app)
    - input: Input data for workflow execution (required, must be valid workflow input format)
    - start_time: When the task should start executing (required, must be future datetime)
    - end_time: When the task should stop executing (optional, if not provided task runs indefinitely)
    - repeat_type: How often to repeat - "none", "minute", "hour", "day", "week", "month", "year"
    - repeat_interval: Number of units between repetitions (e.g., every 5 minutes = interval 5)
    - repeat_days: Array of days for weekly repeat (1-7, where 1=Monday, 7=Sunday)
    - repeat_day_of_month: Day of month for monthly repeat (1-31)
    - repeat_month: Month for yearly repeat (1-12)
    - repeat_day_of_year: Day of year for yearly repeat (1-365/366)
    - task_data: Additional configuration data for task execution
    - max_executions: Maximum number of times to execute (0 = unlimited)
    
    Returns:
        Success response with task_id and success message, or error response with validation details
    
    Raises:
        HTTPException: If validation fails, app/workflow not found, or database operation fails
    """
    # Parameter validation
    if not data.name or not data.name.strip():
        return response_error(get_language_content("scheduled_task_name_required"))
    
    if not data.app_id:
        return response_error(get_language_content("scheduled_task_app_id_required"))
    
    if not data.workflow_id:
        return response_error(get_language_content("scheduled_task_workflow_id_required"))
    
    if not data.input:
        return response_error(get_language_content("scheduled_task_input_required"))
    
    if not data.start_time:
        return response_error(get_language_content("scheduled_task_start_time_required"))
    
    if not data.task_data:
        return response_error(get_language_content("scheduled_task_task_data_required"))
    
    # Validate repeat interval
    if data.repeat_interval <= 0:
        return response_error(get_language_content("scheduled_task_invalid_repeat_interval"))
    
    # Validate maximum execution count
    if data.max_executions < 0:
        return response_error(get_language_content("scheduled_task_invalid_max_executions"))
    
    # Validate end time
    if data.end_time and data.end_time <= data.start_time:
        return response_error(get_language_content("scheduled_task_end_time_before_start_time"))
    
    # Validate repeat days
    if data.repeat_days:
        if not isinstance(data.repeat_days, list) or not all(isinstance(day, int) and 1 <= day <= 7 for day in data.repeat_days):
            return response_error(get_language_content("scheduled_task_repeat_days_invalid"))
    
    # Validate monthly repeat day
    if data.repeat_day_of_month and (data.repeat_day_of_month < 1 or data.repeat_day_of_month > 31):
        return response_error(get_language_content("scheduled_task_repeat_day_of_month_invalid"))
    
    # Validate yearly repeat month
    if data.repeat_month and (data.repeat_month < 1 or data.repeat_month > 12):
        return response_error(get_language_content("scheduled_task_repeat_month_invalid"))
    
    # Validate yearly repeat day
    if data.repeat_day_of_year and (data.repeat_day_of_year < 1 or data.repeat_day_of_year > 365):
        return response_error(get_language_content("scheduled_task_repeat_day_of_year_invalid"))
    
    # Check if application exists and user has permission
    scheduled_tasks_model = ScheduledTasks()
    has_permission, error_message = scheduled_tasks_model.check_app_permission(data.app_id, userinfo.uid)
    if not has_permission:
        return response_error(get_language_content(error_message))
    
    # Check if workflow exists
    if not scheduled_tasks_model.check_workflow_exists(data.workflow_id, data.app_id):
        return response_error(get_language_content("scheduled_task_workflow_not_found"))
    
    # Prepare creation data
    task_data = {
        "name": data.name.strip(),
        "description": data.description,
        "task_type": data.task_type.value,
        "user_id": userinfo.uid,
        "app_id": data.app_id,
        "workflow_id": data.workflow_id,
        "input": data.input,
        "start_time": data.start_time,
        "end_time": data.end_time,
        "repeat_type": data.repeat_type.value,
        "repeat_interval": data.repeat_interval,
        "repeat_days": data.repeat_days,
        "repeat_day_of_month": data.repeat_day_of_month,
        "repeat_month": data.repeat_month,
        "repeat_day_of_year": data.repeat_day_of_year,
        "task_data": data.task_data,
        "node_confirm_users": data.node_confirm_users,
        "max_executions": data.max_executions,
        "status": 1  # ENABLED
    }
    
    # Create scheduled task
    task_id = scheduled_tasks_model.create_scheduled_task(task_data)
    
    if task_id:
        return response_success({
            "task_id": task_id,
            "message": get_language_content("scheduled_task_create_success")
        })
    else:
        return response_error(get_language_content("scheduled_task_create_failed"))


@router.put("/update/{task_id}", response_model=RespBaseSchema)
async def update_scheduled_task(
    task_id: int,
    data: UpdateScheduledTaskSchema,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Update an existing scheduled task.
    
    This endpoint allows users to modify various aspects of a scheduled task including
    its name, description, execution schedule, and configuration. Only fields that
    are provided in the request will be updated; omitted fields remain unchanged.
    
    The task must exist and belong to the authenticated user. If the task is currently
    running, some updates may not take effect until the next execution cycle.
    
    Parameters:
    - task_id: ID of the task to update (required, must exist and belong to user)
    - data: UpdateScheduledTaskSchema containing fields to update (all fields optional)
        - name: New task name (if provided, must be non-empty)
        - description: New task description
        - task_type: New task type ("one_time" or "recurring")
        - input: New input data for workflow execution
        - start_time: New start time (must be future datetime)
        - end_time: New end time (optional, can be null to remove end time)
        - repeat_type: New repeat type
        - repeat_interval: New repeat interval (must be > 0)
        - repeat_days: New repeat days array for weekly tasks
        - repeat_day_of_month: New day of month for monthly tasks
        - repeat_month: New month for yearly tasks
        - repeat_day_of_year: New day of year for yearly tasks
        - task_data: New task configuration data
        - max_executions: New maximum execution count (must be >= 0)
        - status: New task status (1=ENABLED, 2=DISABLED, 3=PAUSED)
    
    Returns:
        Success response with update confirmation, or error response with validation details
    
    Raises:
        HTTPException: If task not found, validation fails, or database operation fails
    """
    scheduled_tasks_model = ScheduledTasks()
    
    # Check if task exists and belongs to current user
    task = scheduled_tasks_model.get_scheduled_task_by_id(task_id, userinfo.uid)
    if not task:
        return response_error(get_language_content("scheduled_task_not_found"))
    
    # Prepare update data
    update_data = {}
    
    if data.name is not None:
        if not data.name.strip():
            return response_error(get_language_content("scheduled_task_name_required"))
        update_data["name"] = data.name.strip()
    
    if data.description is not None:
        update_data["description"] = data.description
    
    if data.task_type is not None:
        update_data["task_type"] = data.task_type.value
    
    if data.input is not None:
        update_data["input"] = data.input
    
    if data.start_time is not None:
        update_data["start_time"] = data.start_time
    
    # Handle end_time field - check if it's explicitly provided in the request
    if hasattr(data, 'end_time') and 'end_time' in data.__dict__:
        if data.end_time is not None:
            # Validate end time when it's not null
            start_time = data.start_time if data.start_time else task['start_time']
            if data.end_time <= start_time:
                return response_error(get_language_content("scheduled_task_end_time_before_start_time"))
        # Always include end_time in update_data when explicitly provided (even if null)
        update_data["end_time"] = data.end_time
    
    if data.repeat_type is not None:
        update_data["repeat_type"] = data.repeat_type.value
    
    if data.repeat_interval is not None:
        if data.repeat_interval <= 0:
            return response_error(get_language_content("scheduled_task_invalid_repeat_interval"))
        update_data["repeat_interval"] = data.repeat_interval
    
    if data.repeat_days is not None:
        if data.repeat_days and not isinstance(data.repeat_days, list) or not all(isinstance(day, int) and 1 <= day <= 7 for day in data.repeat_days):
            return response_error(get_language_content("scheduled_task_repeat_days_invalid"))
        update_data["repeat_days"] = data.repeat_days
    
    if data.repeat_day_of_month is not None:
        if data.repeat_day_of_month and (data.repeat_day_of_month < 1 or data.repeat_day_of_month > 31):
            return response_error(get_language_content("scheduled_task_repeat_day_of_month_invalid"))
        update_data["repeat_day_of_month"] = data.repeat_day_of_month
    
    if data.repeat_month is not None:
        if data.repeat_month and (data.repeat_month < 1 or data.repeat_month > 12):
            return response_error(get_language_content("scheduled_task_repeat_month_invalid"))
        update_data["repeat_month"] = data.repeat_month
    
    if data.repeat_day_of_year is not None:
        if data.repeat_day_of_year and (data.repeat_day_of_year < 1 or data.repeat_day_of_year > 365):
            return response_error(get_language_content("scheduled_task_repeat_day_of_year_invalid"))
        update_data["repeat_day_of_year"] = data.repeat_day_of_year
    
    if data.task_data is not None:
        update_data["task_data"] = data.task_data
    
    if data.node_confirm_users is not None:
        update_data["node_confirm_users"] = data.node_confirm_users
    
    if data.max_executions is not None:
        if data.max_executions < 0:
            return response_error(get_language_content("scheduled_task_invalid_max_executions"))
        update_data["max_executions"] = data.max_executions
    
    if data.status is not None:
        update_data["status"] = data.status.value
    else:
        update_data["status"] = 1
    
    # If no update data, return success directly
    if not update_data:
        return response_success({
            "message": get_language_content("scheduled_task_update_success")
        })
    
    # Update scheduled task
    success = scheduled_tasks_model.update_scheduled_task(task_id, update_data)
    
    if success:
        return response_success({
            "message": get_language_content("scheduled_task_update_success")
        })
    else:
        return response_error(get_language_content("scheduled_task_update_failed"))


@router.delete("/delete/{task_id}", response_model=RespBaseSchema)
async def delete_scheduled_task(
    task_id: int,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Soft delete a scheduled task.
    
    This endpoint performs a soft delete operation on the specified scheduled task.
    The task is not physically removed from the database but is marked as deleted
    (status = 4) and will no longer be visible in normal queries or executed by
    the scheduler.
    
    The task must exist and belong to the authenticated user. If the task is
    currently running, it will be stopped and marked as deleted.
    
    Parameters:
    - task_id: ID of the task to delete (required, must exist and belong to user)
    
    Returns:
        Success response with deletion confirmation, or error response if task not found
    
    Raises:
        HTTPException: If task not found or database operation fails
    
    Note:
        This is a soft delete operation. The task data remains in the database
        but is marked as deleted and will not be executed or returned in queries.
    """
    scheduled_tasks_model = ScheduledTasks()
    
    # Check if task exists and belongs to current user
    task = scheduled_tasks_model.get_scheduled_task_by_id(task_id, userinfo.uid)
    if not task:
        return response_error(get_language_content("scheduled_task_not_found"))
    
    # Soft delete scheduled task
    success = scheduled_tasks_model.delete_scheduled_task(task_id)
    
    if success:
        return response_success({
            "message": get_language_content("scheduled_task_delete_success")
        })
    else:
        return response_error(get_language_content("scheduled_task_delete_failed"))


@router.get("/list", response_model=RespBaseSchema)
async def get_scheduled_tasks_list(
    page: int = 1,
    page_size: int = 10,
    app_id: Optional[int] = None,
    name: Optional[str] = None,
    status: Optional[int] = None,
    task_type: Optional[str] = None,
    pagination_status: int = 0,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Retrieve a paginated list of scheduled tasks for the authenticated user.
    
    This endpoint returns a list of scheduled tasks that belong to the authenticated
    user, with optional filtering capabilities. The results are paginated to handle
    large datasets efficiently. Only non-deleted tasks are returned by default.
    
    The response includes both the task list and pagination metadata to help with
    frontend pagination implementation.
    
    Parameters:
    - page: Page number for pagination (default: 1, minimum: 1)
    - page_size: Number of tasks per page (default: 10, maximum: 100)
    - app_id: Filter tasks by specific application ID (optional)
    - name: Filter tasks by name using partial string matching (optional, case-insensitive)
    - status: Filter tasks by status (optional, 1=ENABLED, 2=DISABLED, 3=PAUSED)
    - task_type: Filter tasks by type (optional, "one_time" or "recurring")
    - pagination_status: Pagination control (default: 0, 0=enable pagination, 1=disable pagination)
    
    Returns:
        Success response containing:
        - list: Array of scheduled task objects with full details
        - total_count: Total number of tasks matching the filters
        - total_pages: Total number of pages available (1 when pagination disabled)
        - page: Current page number (1 when pagination disabled)
        - page_size: Number of items per page (total_count when pagination disabled)
    
    Raises:
        HTTPException: If pagination parameters are invalid or database operation fails
    
    Note:
        Tasks are sorted by creation date (newest first). Deleted tasks (status = 4)
        are automatically excluded from the results. When pagination is disabled
        (pagination_status=1), all matching tasks are returned in a single response.
    """
    scheduled_tasks_model = ScheduledTasks()
    
    # Get scheduled tasks list
    result = scheduled_tasks_model.get_scheduled_tasks_list(
        user_id=userinfo.uid,
        page=page,
        page_size=page_size,
        app_id=app_id,
        name=name,
        status=status,
        task_type=task_type,
        pagination_status=pagination_status
    )
    
    return response_success(result)


@router.get("/detail/{task_id}", response_model=RespBaseSchema)
async def get_scheduled_task_detail(
    task_id: int,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Retrieve detailed information about a specific scheduled task.
    
    This endpoint returns comprehensive information about a scheduled task including
    its configuration, execution history, and current status. The task must exist
    and belong to the authenticated user.
    
    The response includes all task fields including execution statistics, timing
    information, and configuration details needed for task management and monitoring.
    
    Parameters:
    - task_id: ID of the task to retrieve (required, must exist and belong to user)
    
    Returns:
        Success response containing complete task object with fields:
        - id: Unique task identifier
        - name: Task name
        - description: Task description
        - task_type: Type of task ("one_time" or "recurring")
        - status: Current task status (1=ENABLED, 2=DISABLED, 3=PAUSED, 4=DELETED)
        - user_id: Owner user ID
        - app_id: Associated application ID
        - workflow_id: Associated workflow ID
        - input: Workflow input configuration
        - start_time: Scheduled start time
        - end_time: Scheduled end time (null if unlimited)
        - next_run_time: Next scheduled execution time
        - repeat_type: Repeat pattern type
        - repeat_interval: Repeat interval value
        - repeat_days: Array of days for weekly repeat
        - repeat_day_of_month: Day for monthly repeat
        - repeat_month: Month for yearly repeat
        - repeat_day_of_year: Day of year for yearly repeat
        - task_data: Additional task configuration
        - last_run_time: Last execution time
        - last_run_status: Status of last execution
        - execution_count: Total number of executions
        - max_executions: Maximum allowed executions
        - created_at: Task creation timestamp
        - updated_at: Last update timestamp
    
    Raises:
        HTTPException: If task not found or database operation fails
    
    Note:
        Only non-deleted tasks can be retrieved. The task must belong to the
        authenticated user for security purposes.
    """
    scheduled_tasks_model = ScheduledTasks()
    
    # Get scheduled task detail
    task = scheduled_tasks_model.get_scheduled_task_by_id(task_id, userinfo.uid)
    
    if not task:
        return response_error(get_language_content("scheduled_task_not_found"))
    
    return response_success(task)


@router.get("/workflow/{app_id}/{workflow_id}", response_model=RespBaseSchema)
async def get_workflow_scheduled_task(
    app_id: int,
    workflow_id: int,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Get scheduled task for a specific workflow.
    
    This endpoint retrieves the scheduled task associated with a specific
    workflow within an application. Only one scheduled task per workflow
    is supported, so this returns either the existing task or null.
    
    Parameters:
    - app_id: ID of the application (required)
    - workflow_id: ID of the workflow (required)
    
    Returns:
        Success response containing task object if exists, or null if no task found.
        Task object includes all fields as described in the detail endpoint.
    
    Raises:
        HTTPException: If database operation fails
    
    Note:
        Only non-deleted tasks are returned. The task must belong to the
        authenticated user for security purposes.
    """
    scheduled_tasks_model = ScheduledTasks()
    upload_files_model = UploadFiles()
    
    # Get scheduled task by workflow
    task = scheduled_tasks_model.get_scheduled_task_by_workflow(app_id, workflow_id, userinfo.uid)

    if task:
        file_list = []
        if task_input := task.get('input'):
            for k, v in task_input['properties'].items():
                if v['type'] == 'file':
                    file_id = v['value']
                    file_data = upload_files_model.get_file_by_id(file_id)
                    file_name = file_data['name'] + file_data['extension']
                    file_path_relative_to_upload_files = Path(file_data['path']).relative_to('upload_files')
                    file_url = f'{settings.STORAGE_URL}/upload/{file_path_relative_to_upload_files}'
                    file_list.append({
                        'name': k,
                        'variable_name': v['display_name'] if v.get('display_name') else k,
                        'id': file_id,
                        'file_name': file_name,
                        'file_path': file_url
                    })
        task['file_list'] = file_list
    
    # Ensure data is always a dict for response_success
    return response_success(task if task is not None else {})
