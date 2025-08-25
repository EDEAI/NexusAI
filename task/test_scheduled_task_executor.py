#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务执行器测试脚本

用于测试定时任务的基本功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).absolute().parent.parent))

# 设置数据库自动提交
os.environ['DATABASE_AUTO_COMMIT'] = 'True'

from datetime import datetime, timedelta
from timed_execution_of_workflow import ScheduledTaskExecutor
from core.database.models.scheduled_tasks import ScheduledTasks

def test_get_pending_tasks():
    """测试获取待执行任务功能"""
    print("=== 测试获取待执行任务 ===")
    
    executor = ScheduledTaskExecutor()
    pending_tasks = executor.get_pending_tasks()
    
    print(f"发现 {len(pending_tasks)} 个待执行任务")
    
    for task in pending_tasks:
        print(f"任务ID: {task['id']}")
        print(f"任务名称: {task['name']}")
        print(f"任务类型: {task['task_type']}")
        print(f"下次执行时间: {task['next_run_time']}")
        print(f"重复类型: {task['repeat_type']}")
        print("---")

def test_calculate_next_run_time():
    """测试计算下次执行时间功能"""
    print("=== 测试计算下次执行时间 ===")
    
    executor = ScheduledTaskExecutor()
    
    # 测试不同类型的重复任务
    test_tasks = [
        {
            'id': 1,
            'task_type': 'recurring',
            'repeat_type': 'minute',
            'repeat_interval': 5
        },
        {
            'id': 2,
            'task_type': 'recurring',
            'repeat_type': 'hour',
            'repeat_interval': 2
        },
        {
            'id': 3,
            'task_type': 'recurring',
            'repeat_type': 'day',
            'repeat_interval': 1
        },
        {
            'id': 4,
            'task_type': 'recurring',
            'repeat_type': 'week',
            'repeat_interval': 1,
            'repeat_days': [1, 3, 5]  # 周一、周三、周五
        },
        {
            'id': 5,
            'task_type': 'one_time'
        }
    ]
    
    for task in test_tasks:
        next_time = executor._calculate_next_run_time(task)
        print(f"任务 {task['id']} ({task['task_type']}, {task.get('repeat_type', 'none')}): {next_time}")

def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    
    try:
        scheduled_tasks = ScheduledTasks()
        
        # 尝试查询任务总数
        result = scheduled_tasks.select_one(
            aggregates={"id": "count"},
            conditions=[{"column": "status", "op": "!=", "value": 4}]
        )
        
        total_tasks = result["count_id"] if result and "count_id" in result else 0
        print(f"数据库连接成功，共有 {total_tasks} 个非删除状态的定时任务")
        
        # 测试新的方法
        pending_tasks = scheduled_tasks.get_pending_tasks_for_execution()
        print(f"通过新方法查询到 {len(pending_tasks)} 个待执行任务")
        
    except Exception as e:
        print(f"数据库连接失败: {e}")

def main():
    """主测试函数"""
    print("定时任务执行器测试")
    print("=" * 50)
    
    test_database_connection()
    print()
    
    test_get_pending_tasks()
    print()
    
    test_calculate_next_run_time()
    print()
    
    print("测试完成")

if __name__ == '__main__':
    main()