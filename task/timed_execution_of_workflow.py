#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduled task execution script

Features:
1. Query scheduled tasks that need to be executed
2. Execute workflows based on task configuration
3. Update task execution status and next execution time
"""

import sys
import os
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).absolute().parent.parent))

import json
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dateutil.relativedelta import relativedelta

# Set database auto commit
os.environ['DATABASE_AUTO_COMMIT'] = 'True'

from core.database.models.scheduled_tasks import ScheduledTasks
from core.database.models.users import Users
from core.workflow import start_workflow
from core.workflow.variables import validate_required_variable, create_variable_from_dict
from core.workflow.graph import create_graph_from_dict
from core.database.models import Apps, Workflows, AppRuns, AppNodeUserRelation
from core.database.models.chatroom_driven_records import ChatroomDrivenRecords
from copy import deepcopy
from log import Logger

# Initialize logger
logger = Logger.get_logger('scheduled-tasks')

class ScheduledTaskExecutor:
    """
    Scheduled task executor
    """
    
    def __init__(self):
        self.scheduled_tasks_model = ScheduledTasks()
        self.users_model = Users()
    
    def _start_workflow_fixed(
        self,
        team_id: int, 
        user_id: int, 
        app_id: int, 
        run_type: int, 
        run_name: str, 
        inputs: dict,
        knowledge_base_mapping = None,
        node_confirm_users = None,
        data_source_run_id: int = 0,
        scheduled_task_id: int = 0
    ):
        """
        Fixed version of start_workflow function, correctly handles input validation
        """
        from languages import get_language_content
        
        if run_type not in [0, 1]:
            raise Exception('Run type error.')
        run_type = run_type + 1
        app_runs = AppRuns()
        
        workflow = Workflows().workflow_info(app_id, run_type, team_id)
        
        # Check permissions
        if (
            workflow['user_id'] != user_id
            and (
                workflow['team_id'] != team_id
                or workflow['is_public'] == 0
            )
        ):
            raise Exception("You are not authorized to run this workflow.")
        
        if not inputs:
            raise ValueError(get_language_content("graph_validation_errors.inputs_cannot_be_empty"))
        
        # Correct input validation method: get input definition from start node in graph
        graph = create_graph_from_dict(workflow['graph'])
        graph.validate()
        
        # Get input definition from start node
        start_node = graph.nodes.nodes[0]  # First node is the start node
        input_definition = start_node.data['input']
        
        if input_definition:
            # Copy input definition and set values
            input_obj = deepcopy(input_definition)
            
            # Set values for each defined variable
            for key, value in inputs.items():
                if key in input_obj.properties:
                    input_obj.properties[key].value = value
            
            # Provide default values for missing required variables
            for var_name, var_obj in input_obj.properties.items():
                if getattr(var_obj, 'required', False) and (var_obj.value is None or var_obj.value == ''):
                    # Provide default values based on variable type
                    if var_obj.type == 'string':
                        var_obj.value = f"default_{var_name}"
                    elif var_obj.type == 'number':
                        var_obj.value = 0
                    elif var_obj.type == 'file':
                        var_obj.value = None  # File type remains None
                    else:
                        var_obj.value = f"default_{var_name}"
                    
                    logger.warning(f"Task {workflow['id']}: Missing required variable '{var_name}', using default value: {var_obj.value}")
            
            # Validate required variables
            validate_required_variable(input_obj)
            
            # Use processed input object
            validated_inputs = input_obj.to_dict()
        else:
            validated_inputs = inputs
        
        app_run_data = {
            'user_id': user_id,
            'app_id': app_id,
            'workflow_id': workflow['id'],
            'type': run_type,
            'name': run_name,
            'graph': graph.to_dict(),
            'inputs': validated_inputs,
            'status': 1,
            'total_steps': graph.get_total_steps(),
            'scheduled_task_id': scheduled_task_id
        }
        
        if knowledge_base_mapping is not None:
            app_run_data['knowledge_base_mapping'] = knowledge_base_mapping
            
        app_run_id = app_runs.insert(app_run_data)
        
        if data_source_run_id > 0:
            chatroomdriven_info = ChatroomDrivenRecords().get_data_by_data_source_run_id(data_source_run_id)
            if chatroomdriven_info:
                ChatroomDrivenRecords().update_data_driven_run_id(chatroomdriven_info['id'], data_source_run_id, app_run_id)
                
        if node_confirm_users:
            AppNodeUserRelation().create_data(app_run_id, node_confirm_users)
        
        Apps().increment_execution_times(app_id)
        
        return {'app_id': app_id, 'workflow_id': workflow['id'], 'app_run_id': app_run_id}
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Get scheduled tasks that need to be executed
        
        Returns:
            List of tasks to be executed
        """
        try:
            current_time = datetime.now()
            
            # Use database model method to get pending tasks
            tasks = self.scheduled_tasks_model.get_pending_tasks_for_execution()
            
            # Filter tasks: check end time and maximum execution limit
            pending_tasks = []
            for task in tasks:
                # Check end time limit
                if task.get('end_time') and current_time > task['end_time']:
                    logger.info(f"Task {task['id']} ({task['name']}) has exceeded end time, skipping")
                    # Set expired tasks status to completed
                    self._disable_completed_task(task['id'], "Task has exceeded end time")
                    continue
                
                # Check maximum execution limit
                max_executions = task.get('max_executions', 0)
                if max_executions > 0 and task.get('execution_count', 0) >= max_executions:
                    logger.info(f"Task {task['id']} ({task['name']}) has reached max executions ({max_executions}), skipping")
                    # Set tasks that reached max executions to completed
                    self._disable_completed_task(task['id'], f"Task has reached max executions ({max_executions})")
                    continue
                
                pending_tasks.append(task)
            
            logger.info(f"Found {len(pending_tasks)} pending tasks to execute")
            return pending_tasks
            
        except Exception as e:
            logger.error(f"Error getting pending tasks: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def _disable_completed_task(self, task_id: int, reason: str):
        """
        Disable completed tasks
        
        Args:
            task_id: Task ID
            reason: Disable reason
        """
        try:
            self.scheduled_tasks_model.update(
                {"column": "id", "value": task_id},
                {"status": 2}  # Set to disabled status
            )
            logger.info(f"Task {task_id} disabled: {reason}")
        except Exception as e:
            logger.error(f"Error disabling task {task_id}: {e}")
    
    def execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Execute single scheduled task
        
        Args:
            task: Task information
            
        Returns:
            Whether execution was successful
        """
        task_id = task['id']
        task_name = task['name']
        
        try:
            logger.info(f"Starting execution of task {task_id} ({task_name})")
            
            # Debug: show task's input configuration
            logger.info(f"Task {task_id} input configuration: {task['input']} (type: {type(task['input'])})")
            
            # Get user info to obtain team_id
            user_info = self.users_model.get_user_by_id(task['user_id'])
            if not user_info:
                logger.error(f"User {task['user_id']} not found for task {task_id}")
                self._update_task_execution_result(task_id, False, "User not found")
                return False
            
            team_id = user_info['team_id']
            
            # Parse input parameters
            inputs = task['input']
            if isinstance(inputs, str):
                try:
                    inputs = json.loads(inputs)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse inputs for task {task_id}: {e}")
                    self._update_task_execution_result(task_id, False, f"Invalid input format: {e}")
                    return False
            
            if not isinstance(inputs, dict):
                logger.error(f"Invalid inputs type for task {task_id}: {type(inputs)}")
                self._update_task_execution_result(task_id, False, "Inputs must be a dictionary")
                return False
            
            # Handle complex input format: if contains nested variable definition structure, extract actual values
            if 'inputs' in inputs and isinstance(inputs['inputs'], dict):
                # This is the format created from scheduled task API, need to extract actual values
                nested_inputs = inputs['inputs']
                if 'properties' in nested_inputs:
                    # Extract values from variable definitions
                    simple_inputs = {}
                    for key, var_def in nested_inputs['properties'].items():
                        if isinstance(var_def, dict) and 'value' in var_def:
                            simple_inputs[key] = var_def['value']
                        else:
                            simple_inputs[key] = var_def
                    inputs = simple_inputs
                    logger.info(f"Task {task_id}: Extracted simple inputs from complex format: {inputs}")
                else:
                    inputs = nested_inputs
            
            # Ensure inputs are in simple key-value format
            if not inputs or not isinstance(inputs, dict):
                logger.error(f"Task {task_id}: Invalid or empty inputs after processing: {inputs}")
                self._update_task_execution_result(task_id, False, "Invalid inputs format after processing")
                return False
            
            # Generate run name
            current_time = datetime.now()
            run_name = f"Scheduled_Task_{task_id}_{current_time.strftime('%Y%m%d_%H%M%S')}"
            
            # Call fixed version of workflow execution function
            try:
                result = self._start_workflow_fixed(
                    team_id=team_id,
                    user_id=task['user_id'],
                    app_id=task['app_id'],
                    run_type=1,  # Use published version
                    run_name=run_name,
                    inputs=inputs,
                    knowledge_base_mapping=None,
                    node_confirm_users=None,
                    data_source_run_id=0,
                    scheduled_task_id=task_id
                )
            except Exception as workflow_error:
                # If input validation error, provide more detailed error information
                error_msg = str(workflow_error)
                if "'name'" in error_msg or "create_variable_from_dict" in error_msg:
                    error_msg = f"Invalid input format for workflow. Task inputs: {inputs}. Original error: {error_msg}"
                logger.error(f"Workflow execution failed for task {task_id}: {error_msg}")
                self._update_task_execution_result(task_id, False, error_msg)
                return False
            
            if result:
                logger.info(f"Task {task_id} executed successfully, app_run_id: {result.get('app_run_id')}")
                self._update_task_execution_result(task_id, True, f"Workflow started successfully, app_run_id: {result.get('app_run_id')}")
                return True
            else:
                logger.error(f"Task {task_id} execution failed: workflow start returned no result")
                self._update_task_execution_result(task_id, False, "Workflow start returned no result")
                return False
                
        except Exception as e:
            error_msg = f"Task {task_id} execution failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self._update_task_execution_result(task_id, False, str(e))
            return False
    
    def _update_task_execution_result(self, task_id: int, success: bool, message: str = ""):
        """
        Update task execution result
        
        Args:
            task_id: Task ID
            success: Whether execution was successful
            message: Execution message
        """
        try:
            current_time = datetime.now()
            
            # Get task info to calculate next execution time (use direct query, not restricted by user)
            task = self.scheduled_tasks_model.select_one(
                columns="*",
                conditions=[{"column": "id", "value": task_id}]
            )
            if not task:
                logger.error(f"Task {task_id} not found when updating execution result")
                return
            
            # Update execution statistics
            execution_count = task.get('execution_count', 0) + 1
            last_run_status = 1 if success else 2  # 1: Success, 2: Failed
            
            update_data = {
                'last_run_time': current_time,
                'last_run_status': last_run_status,
                'execution_count': execution_count
            }
            
            # Calculate next execution time
            next_run_time = self._calculate_next_run_time(task)
            if next_run_time:
                update_data['next_run_time'] = next_run_time
                logger.info(f"Task {task_id} next run time: {next_run_time}")
            else:
                # If one-time task or cannot calculate next execution time, disable task
                update_data['status'] = 2  # Disabled
                logger.info(f"Task {task_id} completed, no next run time")
            
            # Update task
            self.scheduled_tasks_model.update(
                {"column": "id", "value": task_id},
                update_data
            )
            
            status_msg = "successfully" if success else "with error"
            logger.info(f"Task {task_id} execution result updated {status_msg}: {message}")
            
        except Exception as e:
            logger.error(f"Error updating task {task_id} execution result: {e}")
            logger.error(traceback.format_exc())
    
    def _calculate_next_run_time(self, task: Dict[str, Any]) -> Optional[datetime]:
        """
        Calculate next execution time
        
        Args:
            task: Task information
            
        Returns:
            Next execution time, returns None if one-time task
        """
        try:
            task_type = task.get('task_type')
            if task_type == 'one_time':
                return None  # One-time task has no next execution time
            
            repeat_type = task.get('repeat_type', 'none')
            if repeat_type == 'none':
                return None
            
            current_time = datetime.now()
            repeat_interval = task.get('repeat_interval', 1)
            
            # Calculate next execution time based on current time
            if repeat_type == 'minute':
                return current_time + timedelta(minutes=repeat_interval)
            
            elif repeat_type == 'hour':
                return current_time + timedelta(hours=repeat_interval)
            
            elif repeat_type == 'day':
                return current_time + timedelta(days=repeat_interval)
            
            elif repeat_type == 'week':
                repeat_days = task.get('repeat_days')
                if repeat_days and isinstance(repeat_days, list):
                    # Find next day of week that should be executed
                    next_time = current_time + timedelta(days=1)
                    for _ in range(7):  # Check at most 7 days
                        weekday = next_time.weekday() + 1  # 1-7 (Monday-Sunday)
                        if weekday in repeat_days:
                            return next_time.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
                        next_time += timedelta(days=1)
                else:
                    # If no specific day of week specified, calculate by week interval
                    return current_time + timedelta(weeks=repeat_interval)
            
            elif repeat_type == 'month':
                repeat_day_of_month = task.get('repeat_day_of_month')
                if repeat_day_of_month:
                    # Specify a certain day of each month
                    next_month = current_time + relativedelta(months=repeat_interval)
                    try:
                        return next_month.replace(day=repeat_day_of_month)
                    except ValueError:
                        # If specified date doesn't exist in next month (like Feb 30), use end of month
                        next_month = next_month.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
                        return next_month
                else:
                    # Calculate by month interval
                    return current_time + relativedelta(months=repeat_interval)
            
            elif repeat_type == 'year':
                repeat_month = task.get('repeat_month')
                repeat_day_of_year = task.get('repeat_day_of_year')
                
                if repeat_month and repeat_day_of_year:
                    # Specify a certain month and day of each year
                    next_year = current_time + relativedelta(years=repeat_interval)
                    try:
                        target_date = datetime(next_year.year, repeat_month, repeat_day_of_year)
                        return target_date.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
                    except ValueError:
                        # Handle invalid dates (like Feb 29 in non-leap year)
                        return current_time + relativedelta(years=repeat_interval)
                else:
                    # Calculate by year interval
                    return current_time + relativedelta(years=repeat_interval)
            
            else:
                logger.warning(f"Unknown repeat_type: {repeat_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating next run time for task {task.get('id')}: {e}")
            return None
    
    def run_once(self) -> int:
        """
        Execute scheduled task check and execution once
        
        Returns:
            Number of executed tasks
        """
        try:
            logger.info("Starting scheduled task execution cycle")
            
            # Get tasks that need to be executed
            pending_tasks = self.get_pending_tasks()
            
            if not pending_tasks:
                logger.debug("No pending tasks found")
                return 0
            
            executed_count = 0
            
            # Execute tasks one by one
            for task in pending_tasks:
                try:
                    success = self.execute_task(task)
                    if success:
                        executed_count += 1
                    
                    # Small delay between tasks to avoid starting too many workflows simultaneously
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error executing task {task['id']}: {e}")
                    continue
            
            logger.info(f"Completed scheduled task execution cycle, executed {executed_count}/{len(pending_tasks)} tasks")
            return executed_count
            
        except Exception as e:
            logger.error(f"Error in scheduled task execution cycle: {e}")
            logger.error(traceback.format_exc())
            return 0
    
    def run_daemon(self, check_interval: int = 60):
        """
        Run scheduled task executor in daemon mode
        
        Args:
            check_interval: Check interval (seconds), default 60 seconds
        """
        logger.info(f"Starting scheduled task daemon with {check_interval}s check interval")
        
        try:
            while True:
                self.run_once()
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("Scheduled task daemon stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in scheduled task daemon: {e}")
            logger.error(traceback.format_exc())
            raise


def main():
    """
    Main function
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduled task execution script')
    parser.add_argument('--mode', choices=['once', 'daemon'], default='once',
                        help='Run mode: once (execute once) or daemon (daemon mode)')
    parser.add_argument('--interval', type=int, default=60,
                        help='Check interval in daemon mode (seconds), default 60 seconds')
    
    args = parser.parse_args()
    
    executor = ScheduledTaskExecutor()
    
    if args.mode == 'once':
        # Execute once
        executed_count = executor.run_once()
        print(f"Executed {executed_count} tasks")
    elif args.mode == 'daemon':
        # Daemon mode
        executor.run_daemon(args.interval)


if __name__ == '__main__':
    main()