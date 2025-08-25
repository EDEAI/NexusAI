#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务执行脚本

功能：
1. 查询需要执行的定时任务
2. 根据任务配置执行工作流
3. 更新任务执行状态和下次执行时间
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).absolute().parent.parent))

import json
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dateutil.relativedelta import relativedelta

# 设置数据库自动提交
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

# 初始化日志记录器
logger = Logger.get_logger('scheduled-tasks')

class ScheduledTaskExecutor:
    """
    定时任务执行器
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
        scheduled_task_id: int
    ):
        """
        修复版本的start_workflow函数，正确处理输入验证
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
        
        # 正确的输入验证方式：从图中获取start node的input定义
        graph = create_graph_from_dict(workflow['graph'])
        graph.validate()
        
        # 获取start node的input定义
        start_node = graph.nodes.nodes[0]  # 第一个节点是start node
        input_definition = start_node.data['input']
        
        if input_definition:
            # 复制input定义并设置值
            input_obj = deepcopy(input_definition)
            
            # 为每个定义的变量设置值
            for key, value in inputs.items():
                if key in input_obj.properties:
                    input_obj.properties[key].value = value
            
            # 为缺失的必需变量提供默认值
            for var_name, var_obj in input_obj.properties.items():
                if getattr(var_obj, 'required', False) and (var_obj.value is None or var_obj.value == ''):
                    # 根据变量类型提供默认值
                    if var_obj.type == 'string':
                        var_obj.value = f"default_{var_name}"
                    elif var_obj.type == 'number':
                        var_obj.value = 0
                    elif var_obj.type == 'file':
                        var_obj.value = None  # 文件类型保持为None
                    else:
                        var_obj.value = f"default_{var_name}"
                    
                    logger.warning(f"Task {workflow['id']}: Missing required variable '{var_name}', using default value: {var_obj.value}")
            
            # 验证必需变量
            validate_required_variable(input_obj)
            
            # 使用处理后的input_obj
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
            'scheduled_task_id':scheduled_task_id,
            'total_steps': graph.get_total_steps()
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
        获取需要执行的定时任务
        
        Returns:
            需要执行的任务列表
        """
        try:
            current_time = datetime.now()
            
            # 使用数据库模型中的方法获取待执行任务
            tasks = self.scheduled_tasks_model.get_pending_tasks_for_execution()
            
            # 过滤任务：检查结束时间和最大执行次数限制
            pending_tasks = []
            for task in tasks:
                # 检查结束时间限制
                if task.get('end_time') and current_time > task['end_time']:
                    logger.info(f"Task {task['id']} ({task['name']}) has exceeded end time, skipping")
                    # 将超时的任务状态设置为已完成
                    self._disable_completed_task(task['id'], "Task has exceeded end time")
                    continue
                
                # 检查最大执行次数限制
                max_executions = task.get('max_executions', 0)
                if max_executions > 0 and task.get('execution_count', 0) >= max_executions:
                    logger.info(f"Task {task['id']} ({task['name']}) has reached max executions ({max_executions}), skipping")
                    # 将达到最大执行次数的任务状态设置为已完成
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
        禁用已完成的任务
        
        Args:
            task_id: 任务ID
            reason: 禁用原因
        """
        try:
            self.scheduled_tasks_model.update(
                {"column": "id", "value": task_id},
                {"status": 2}  # 设置为禁用状态
            )
            logger.info(f"Task {task_id} disabled: {reason}")
        except Exception as e:
            logger.error(f"Error disabling task {task_id}: {e}")
    
    def execute_task(self, task: Dict[str, Any]) -> bool:
        """
        执行单个定时任务
        
        Args:
            task: 任务信息
            
        Returns:
            执行是否成功
        """
        task_id = task['id']
        task_name = task['name']
        
        try:
            logger.info(f"Starting execution of task {task_id} ({task_name})")
            
            # 调试：显示任务的输入配置
            logger.info(f"Task {task_id} input configuration: {task['input']} (type: {type(task['input'])})")
            
            # 获取用户信息以获取team_id
            user_info = self.users_model.get_user_by_id(task['user_id'])
            if not user_info:
                logger.error(f"User {task['user_id']} not found for task {task_id}")
                self._update_task_execution_result(task_id, False, "User not found")
                return False
            
            team_id = user_info['team_id']
            
            # 解析输入参数
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
            
            # 处理复杂的输入格式：如果包含嵌套的变量定义结构，提取实际值
            if 'inputs' in inputs and isinstance(inputs['inputs'], dict):
                # 这是从定时任务API创建的格式，需要提取实际值
                nested_inputs = inputs['inputs']
                if 'properties' in nested_inputs:
                    # 从变量定义中提取值
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
            
            # 确保inputs是简单的键值对格式
            if not inputs or not isinstance(inputs, dict):
                logger.error(f"Task {task_id}: Invalid or empty inputs after processing: {inputs}")
                self._update_task_execution_result(task_id, False, "Invalid inputs format after processing")
                return False
            
            # 生成运行名称
            current_time = datetime.now()
            run_name = f"Scheduled_Task_{task_id}_{current_time.strftime('%Y%m%d_%H%M%S')}"
            
            # 调用修复版本的工作流执行函数
            try:
                result = self._start_workflow_fixed(
                    team_id=team_id,
                    user_id=task['user_id'],
                    app_id=task['app_id'],
                    run_type=1,  # 使用发布版本
                    run_name=run_name,
                    inputs=inputs,
                    knowledge_base_mapping=None,
                    node_confirm_users=None,
                    data_source_run_id=0,
                    scheduled_task_id=task_id
                )
            except Exception as workflow_error:
                # 如果是输入验证错误，提供更详细的错误信息
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
        更新任务执行结果
        
        Args:
            task_id: 任务ID
            success: 执行是否成功
            message: 执行消息
        """
        try:
            current_time = datetime.now()
            
            # 获取任务信息以计算下次执行时间（使用直接查询，不受用户限制）
            task = self.scheduled_tasks_model.select_one(
                columns="*",
                conditions=[{"column": "id", "value": task_id}]
            )
            if not task:
                logger.error(f"Task {task_id} not found when updating execution result")
                return
            
            # 更新执行统计
            execution_count = task.get('execution_count', 0) + 1
            last_run_status = 1 if success else 2  # 1: 成功, 2: 失败
            
            update_data = {
                'last_run_time': current_time,
                'last_run_status': last_run_status,
                'execution_count': execution_count
            }
            
            # 计算下次执行时间
            next_run_time = self._calculate_next_run_time(task)
            if next_run_time:
                update_data['next_run_time'] = next_run_time
                logger.info(f"Task {task_id} next run time: {next_run_time}")
            else:
                # 如果是一次性任务或无法计算下次执行时间，则禁用任务
                update_data['status'] = 2  # 禁用
                logger.info(f"Task {task_id} completed, no next run time")
            
            # 更新任务
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
        计算下次执行时间
        
        Args:
            task: 任务信息
            
        Returns:
            下次执行时间，如果是一次性任务则返回None
        """
        try:
            task_type = task.get('task_type')
            if task_type == 'one_time':
                return None  # 一次性任务没有下次执行时间
            
            repeat_type = task.get('repeat_type', 'none')
            if repeat_type == 'none':
                return None
            
            current_time = datetime.now()
            repeat_interval = task.get('repeat_interval', 1)
            
            # 基于当前时间计算下次执行时间
            if repeat_type == 'minute':
                return current_time + timedelta(minutes=repeat_interval)
            
            elif repeat_type == 'hour':
                return current_time + timedelta(hours=repeat_interval)
            
            elif repeat_type == 'day':
                return current_time + timedelta(days=repeat_interval)
            
            elif repeat_type == 'week':
                repeat_days = task.get('repeat_days')
                if repeat_days and isinstance(repeat_days, list):
                    # 找到下一个应该执行的星期几
                    next_time = current_time + timedelta(days=1)
                    for _ in range(7):  # 最多检查7天
                        weekday = next_time.weekday() + 1  # 1-7 (Monday-Sunday)
                        if weekday in repeat_days:
                            return next_time.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
                        next_time += timedelta(days=1)
                else:
                    # 如果没有指定具体的星期几，则按间隔周数计算
                    return current_time + timedelta(weeks=repeat_interval)
            
            elif repeat_type == 'month':
                repeat_day_of_month = task.get('repeat_day_of_month')
                if repeat_day_of_month:
                    # 指定每月的某一天
                    next_month = current_time + relativedelta(months=repeat_interval)
                    try:
                        return next_month.replace(day=repeat_day_of_month)
                    except ValueError:
                        # 如果指定的日期在下个月不存在（如2月30日），则使用月末
                        next_month = next_month.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
                        return next_month
                else:
                    # 按月份间隔计算
                    return current_time + relativedelta(months=repeat_interval)
            
            elif repeat_type == 'year':
                repeat_month = task.get('repeat_month')
                repeat_day_of_year = task.get('repeat_day_of_year')
                
                if repeat_month and repeat_day_of_year:
                    # 指定每年的某月某日
                    next_year = current_time + relativedelta(years=repeat_interval)
                    try:
                        target_date = datetime(next_year.year, repeat_month, repeat_day_of_year)
                        return target_date.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
                    except ValueError:
                        # 处理无效日期（如2月29日在非闰年）
                        return current_time + relativedelta(years=repeat_interval)
                else:
                    # 按年份间隔计算
                    return current_time + relativedelta(years=repeat_interval)
            
            else:
                logger.warning(f"Unknown repeat_type: {repeat_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating next run time for task {task.get('id')}: {e}")
            return None
    
    def run_once(self) -> int:
        """
        执行一次定时任务检查和执行
        
        Returns:
            执行的任务数量
        """
        try:
            logger.info("Starting scheduled task execution cycle")
            
            # 获取需要执行的任务
            pending_tasks = self.get_pending_tasks()
            
            if not pending_tasks:
                logger.debug("No pending tasks found")
                return 0
            
            executed_count = 0
            
            # 逐个执行任务
            for task in pending_tasks:
                try:
                    success = self.execute_task(task)
                    if success:
                        executed_count += 1
                    
                    # 任务间稍作延迟，避免同时启动太多工作流
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
        以守护进程模式运行定时任务执行器
        
        Args:
            check_interval: 检查间隔（秒），默认60秒
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
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='定时任务执行脚本')
    parser.add_argument('--mode', choices=['once', 'daemon'], default='daemon',
                        help='运行模式：once(执行一次) 或 daemon(守护进程模式)')
    parser.add_argument('--interval', type=int, default=60,
                        help='守护进程模式下的检查间隔（秒），默认60秒')
    parser.add_argument('--loop', action='store_true',
                        help='在once模式下循环执行，相当于daemon模式')
    
    args = parser.parse_args()
    
    executor = ScheduledTaskExecutor()
    
    if args.mode == 'once':
        if args.loop:
            # once模式下循环执行
            logger.info(f"Starting scheduled task loop mode with {args.interval}s interval")
            try:
                while True:
                    executed_count = executor.run_once()
                    print(f"Executed {executed_count} tasks")
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Scheduled task loop stopped by user")
                print("Stopped by user")
        else:
            # 执行一次
            executed_count = executor.run_once()
            print(f"Executed {executed_count} tasks")
    elif args.mode == 'daemon':
        # 守护进程模式
        executor.run_daemon(args.interval)


if __name__ == '__main__':
    main()