from typing import Dict, Any, List, Optional
from core.database import MySQL
import math
import json
from datetime import datetime

class ScheduledTasks(MySQL):
    """
    A class that extends MySQL to manage operations on the scheduled_tasks table.
    """
    table_name = "scheduled_tasks"
    """
    Indicates whether the `scheduled_tasks` table has an `updated_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    def create_scheduled_task(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Create scheduled task
        
        Args:
            data: Scheduled task data
            
        Returns:
            Created task ID, returns None if failed
        """
        try:
            # repeat_days: If string, try to parse as JSON, must be list; empty list or not passed saves as SQL NULL
            if 'repeat_days' in data and data['repeat_days'] is not None:
                if isinstance(data['repeat_days'], str):
                    try:
                        data['repeat_days'] = json.loads(data['repeat_days'])
                    except Exception:
                        raise ValueError('repeat_days must be a JSON-parsable string or list')
                if not isinstance(data['repeat_days'], list):
                    raise ValueError('repeat_days must be a list')
                if len(data['repeat_days']) == 0:
                    data['repeat_days'] = None
                else:
                    # 将列表转换为JSON字符串存储到数据库
                    data['repeat_days'] = json.dumps(data['repeat_days'])
            else:
                # Not passed or None: save as NULL
                data['repeat_days'] = None

            # input: If string, try to parse as JSON, must be dict, and validate with workflow
            if 'input' in data and data['input'] is not None:
                normalized_inputs = data['input']
                if isinstance(normalized_inputs, str):
                    try:
                        normalized_inputs = json.loads(normalized_inputs)
                    except Exception:
                        raise ValueError('inputs must be a JSON-parsable string or dict object')
                if not isinstance(normalized_inputs, dict):
                    raise ValueError('inputs must be a dict object')
                try:
                    from core.workflow import create_variable_from_dict, validate_required_variable
                    validate_required_variable(create_variable_from_dict(normalized_inputs))
                except Exception:
                    pass
                if not normalized_inputs:
                    raise ValueError('inputs cannot be empty')
                data['input'] = normalized_inputs

            # task_data: If string, try to parse as JSON, keep object (dict/list/scalar)
            if 'task_data' in data and data['task_data'] is not None:
                if isinstance(data['task_data'], str):
                    try:
                        data['task_data'] = json.loads(data['task_data'])
                    except Exception:
                        # Non-JSON string kept as-is for backward compatibility
                        pass

            # Set next execution time
            data['next_run_time'] = data.get('start_time')
            
            task_id = self.insert(data)
            return task_id
        except Exception as e:
            print(f"Failed to create scheduled task: {e}")
            return None

    def update_scheduled_task(self, task_id: int, data: Dict[str, Any]) -> bool:
        """
        Update scheduled task
        
        Args:
            task_id: Task ID
            data: Update data
            
        Returns:
            Whether update was successful
        """
        try:
            # repeat_days: When updating, if field is provided, empty array or None saves as SQL NULL
            if 'repeat_days' in data:
                if data['repeat_days'] is None:
                    data['repeat_days'] = None
                else:
                    if isinstance(data['repeat_days'], str):
                        try:
                            data['repeat_days'] = json.loads(data['repeat_days'])
                        except Exception:
                            raise ValueError('repeat_days must be a JSON-parsable string or list')
                    if not isinstance(data['repeat_days'], list):
                        raise ValueError('repeat_days must be a list')
                    if len(data['repeat_days']) == 0:
                        data['repeat_days'] = None
                    else:
                        # 将列表转换为JSON字符串存储到数据库
                        data['repeat_days'] = json.dumps(data['repeat_days'])

            # input: Parse as dict and validate
            if 'input' in data and data['input'] is not None:
                normalized_inputs = data['input']
                if isinstance(normalized_inputs, str):
                    try:
                        normalized_inputs = json.loads(normalized_inputs)
                    except Exception:
                        raise ValueError('inputs must be a JSON-parsable string or dict object')
                if not isinstance(normalized_inputs, dict):
                    raise ValueError('inputs must be a dict object')
                try:
                    from core.workflow import create_variable_from_dict, validate_required_variable
                    validate_required_variable(create_variable_from_dict(normalized_inputs))
                except Exception:
                    pass
                if not normalized_inputs:
                    raise ValueError('inputs cannot be empty')
                data['input'] = normalized_inputs

            # task_data: If string, try to parse
            if 'task_data' in data and data['task_data'] is not None:
                if isinstance(data['task_data'], str):
                    try:
                        data['task_data'] = json.loads(data['task_data'])
                    except Exception:
                        pass

            # If start time is updated, also update next execution time
            if 'start_time' in data:
                data['next_run_time'] = data['start_time']
            result = self.update(
                {"column": "id", "value": task_id},
                data
            )
            return result
        except Exception as e:
            print(f"Failed to update scheduled task: {e}")
            return False

    def delete_scheduled_task(self, task_id: int) -> bool:
        """
        Soft delete scheduled task
        
        Args:
            task_id: Task ID
            
        Returns:
            Whether deletion was successful
        """
        try:
            result = self.update(
                {"column": "id", "value": task_id},
                {"status": 4}  # DELETED
            )
            return result
        except Exception as e:
            print(f"Failed to delete scheduled task: {e}")
            return False

    def get_scheduled_task_by_id(self, task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get scheduled task details by ID
        
        Args:
            task_id: Task ID
            user_id: User ID
            
        Returns:
            Task details, returns None if not found
        """
        try:
            task = self.select_one(
                columns="*",
                conditions=[
                    {"column": "id", "value": task_id},
                    {"column": "user_id", "value": user_id},
                    {"column": "status", "op": "!=", "value": 4}  # 排除已删除的
                ]
            )
            
            if task:
                # Parse JSON fields (only when string, for backward compatibility)
                if task.get('repeat_days') and isinstance(task.get('repeat_days'), str):
                    try:
                        task['repeat_days'] = json.loads(task['repeat_days'])
                    except Exception:
                        pass
                if task.get('input') and isinstance(task.get('input'), str):
                    try:
                        task['input'] = json.loads(task['input'])
                    except Exception:
                        pass
                if task.get('task_data') and isinstance(task.get('task_data'), str):
                    try:
                        task['task_data'] = json.loads(task['task_data'])
                    except Exception:
                        pass
            
            return task
        except Exception as e:
            print(f"Failed to get scheduled task details: {e}")
            return None

    def get_scheduled_tasks_list(self, user_id: int, page: int = 1, page_size: int = 10, 
                                app_id: Optional[int] = None, name: Optional[str] = None,
                                status: Optional[int] = None, task_type: Optional[str] = None,
                                pagination_status: int = 0) -> Dict[str, Any]:
        """
        Get scheduled tasks list
        
        Args:
            user_id: User ID
            page: Page number
            page_size: Page size
            app_id: Application ID filter
            name: Task name filter
            status: Status filter
            task_type: Task type filter
            pagination_status: Pagination control (0=enable pagination, 1=disable pagination)
            
        Returns:
            Dictionary containing list data and pagination information
        """
        try:
            conditions = [
                {"column": "user_id", "value": user_id},
                {"column": "status", "op": "!=", "value": 4}  # 排除已删除的
            ]
            
            if app_id:
                conditions.append({"column": "app_id", "value": app_id})
            if name:
                conditions.append({"column": "name", "op": "like", "value": f"%{name}%"})
            if status:
                conditions.append({"column": "status", "value": status})
            if task_type:
                conditions.append({"column": "task_type", "value": task_type})
            
            # Get total count
            total_count_row = self.select_one(
                aggregates={"id": "count"},
                conditions=conditions,
            )
            total_count = total_count_row["count_id"] if total_count_row and "count_id" in total_count_row else 0
            
            # Handle pagination based on pagination_status
            if pagination_status == 0:
                # Enable pagination
                total_pages = math.ceil(total_count / page_size)
                offset = (page - 1) * page_size
                limit = page_size
            else:
                # Disable pagination - return all results
                total_pages = 1
                offset = 0
                limit = None
            
            # Get list data
            tasks = self.select(
                columns=[
                    "id",
                    "name",
                    "description",
                    "task_type",
                    "status",
                    "user_id",
                    "app_id",
                    "workflow_id",
                    "input",
                    "start_time",
                    "end_time",
                    "next_run_time",
                    "repeat_type",
                    "repeat_interval",
                    "repeat_days",
                    "repeat_day_of_month",
                    "repeat_month",
                    "repeat_day_of_year",
                    "task_data",
                    "last_run_time",
                    "last_run_status",
                    "execution_count",
                    "max_executions",
                    "created_at",
                    "updated_at"
                ],
                conditions=conditions,
                order_by="created_at DESC",
                limit=limit,
                offset=offset
            )
            
            # Parse JSON fields (only when string, for backward compatibility)
            for task in tasks:
                if task.get('repeat_days') and isinstance(task.get('repeat_days'), str):
                    try:
                        task['repeat_days'] = json.loads(task['repeat_days'])
                    except Exception:
                        pass
                if task.get('input') and isinstance(task.get('input'), str):
                    try:
                        task['input'] = json.loads(task['input'])
                    except Exception:
                        pass
                if task.get('task_data') and isinstance(task.get('task_data'), str):
                    try:
                        task['task_data'] = json.loads(task['task_data'])
                    except Exception:
                        pass
            
            return {
                "list": tasks,
                "total_count": total_count,
                "total_pages": total_pages,
                "page": page if pagination_status == 0 else 1,
                "page_size": page_size if pagination_status == 0 else total_count
            }
        except Exception as e:
            print(f"Failed to get scheduled tasks list: {e}")
            return {
                "list": [],
                "total_count": 0,
                "total_pages": 0,
                "page": page if pagination_status == 0 else 1,
                "page_size": page_size if pagination_status == 0 else 0
            }

    def check_app_exists(self, app_id: int, user_id: int) -> bool:
        """
        Check if application exists and status is normal
        
        Args:
            app_id: Application ID
            user_id: User ID
            
        Returns:
            Whether application exists
        """
        try:
            from core.database.models.apps import Apps
            apps_model = Apps()
            
            app = apps_model.select_one(
                columns=["id"],
                conditions=[
                    {"column": "id", "value": app_id},
                    {"column": "user_id", "value": user_id},
                    {"column": "status", "value": 1}  # Normal status
                ]
            )
            
            return app is not None
        except Exception as e:
            print(f"Failed to check if application exists: {e}")
            return False
    
    def check_app_permission(self, app_id: int, user_id: int) -> tuple[bool, str]:
        """
        Check if user has permission to access the application
        
        Args:
            app_id: Application ID
            user_id: User ID
            
        Returns:
            (has_permission: bool, error_message: str)
        """
        try:
            from core.database.models.apps import Apps
            from core.database.models.users import Users
            
            apps_model = Apps()
            users_model = Users()
            
            # 1. Check if app exists
            app = apps_model.select_one(
                columns=["id", "user_id", "is_public", "team_id"],
                conditions=[
                    {"column": "id", "value": app_id},
                    {"column": "status", "value": 1}  # Normal status
                ]
            )
            
            if not app:
                return False, "scheduled_task_app_not_exists"
            
            # 2. Check if app is public
            if app["is_public"] != 1:
                return False, "scheduled_task_app_not_public"
            
            # 3. Check if user is the creator
            if app["user_id"] == user_id:
                return True, ""
            
            # 4. Check if user belongs to the same team
            user = users_model.select_one(
                columns=["team_id"],
                conditions=[
                    {"column": "id", "value": user_id},
                    {"column": "status", "value": 1}
                ]
            )
            
            if not user:
                return False, "scheduled_task_app_no_team_permission"
            
            if user["team_id"] == app["team_id"]:
                return True, ""
            else:
                return False, "scheduled_task_app_no_team_permission"
                
        except Exception as e:
            print(f"Failed to check app permission: {e}")
            return False, "scheduled_task_app_not_exists"

    def get_pending_tasks_for_execution(self) -> List[Dict[str, Any]]:
        """
        Get pending tasks for execution (system-level access without user restriction)
        
        Returns:
            List of pending tasks ready for execution
        """
        try:
            from datetime import datetime
            current_time = datetime.now()
            
            conditions = [
                {"column": "status", "value": 1},  # ENABLED
                {"column": "next_run_time", "op": "<=", "value": current_time}
            ]
            
            tasks = self.select(
                columns=[
                    "id", "name", "description", "task_type", "user_id",
                    "app_id", "workflow_id", "input", "start_time", "end_time",
                    "next_run_time", "repeat_type", "repeat_interval", "repeat_days",
                    "repeat_day_of_month", "repeat_month", "repeat_day_of_year",
                    "task_data", "execution_count", "max_executions", "last_run_time",
                    "last_run_status"
                ],
                conditions=conditions,
                order_by="next_run_time ASC"
            )
            
            # Parse JSON fields for each task
            for task in tasks:
                if task.get('repeat_days') and isinstance(task.get('repeat_days'), str):
                    try:
                        task['repeat_days'] = json.loads(task['repeat_days'])
                    except Exception:
                        pass
                if task.get('input') and isinstance(task.get('input'), str):
                    try:
                        task['input'] = json.loads(task['input'])
                    except Exception:
                        pass
                if task.get('task_data') and isinstance(task.get('task_data'), str):
                    try:
                        task['task_data'] = json.loads(task['task_data'])
                    except Exception:
                        pass
            
            return tasks
        except Exception as e:
            print(f"Failed to get pending tasks for execution: {e}")
            return []

    def check_workflow_exists(self, workflow_id: int, app_id: int) -> bool:
        """
        Check if workflow exists and status is normal
        
        Args:
            workflow_id: Workflow ID
            app_id: Application ID
            
        Returns:
            Whether workflow exists
        """
        try:
            from core.database.models.workflows import Workflows
            workflows_model = Workflows()
            
            workflow = workflows_model.select_one(
                columns=["id"],
                conditions=[
                    {"column": "id", "value": workflow_id},
                    {"column": "app_id", "value": app_id},
                    {"column": "status", "value": 1}  # Normal status
                ]
            )
            
            return workflow is not None
        except Exception as e:
            print(f"Failed to check if workflow exists: {e}")
            return False