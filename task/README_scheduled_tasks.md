# 定时任务执行器 (Scheduled Task Executor)

## 概述

定时任务执行器是一个用于自动执行NexusAI系统中定时任务的脚本。它会定期检查数据库中的定时任务，并根据任务配置自动执行相应的工作流。

## 主要功能

1. **定时任务查询**：自动查询数据库中需要执行的定时任务
2. **工作流执行**：根据任务配置调用工作流执行函数
3. **任务状态更新**：更新任务执行状态和下次执行时间
4. **重复任务支持**：支持多种重复模式（分钟、小时、天、周、月、年）
5. **错误处理**：完善的错误处理和日志记录

## 文件结构

```
task/
├── timed_execution_of_workflow.py     # 主执行器脚本
├── test_scheduled_task_executor.py    # 测试脚本
├── start_scheduled_tasks.sh           # 启动脚本
└── README_scheduled_tasks.md          # 本文档
```

## 使用方法

### 1. 直接运行Python脚本

```bash
# 执行一次检查
python3 timed_execution_of_workflow.py --mode once

# 守护进程模式，默认60秒检查间隔
python3 timed_execution_of_workflow.py --mode daemon

# 守护进程模式，自定义检查间隔（30秒）
python3 timed_execution_of_workflow.py --mode daemon --interval 30
```

### 2. 使用启动脚本

```bash
# 给脚本添加执行权限
chmod +x start_scheduled_tasks.sh

# 执行一次检查
./start_scheduled_tasks.sh once

# 守护进程模式，默认60秒检查间隔
./start_scheduled_tasks.sh daemon

# 守护进程模式，30秒检查间隔
./start_scheduled_tasks.sh daemon 30
```

### 3. 运行测试

```bash
# 运行测试脚本
python3 test_scheduled_task_executor.py
```

## 任务执行逻辑

### 任务筛选条件

执行器会查询满足以下条件的任务：

1. 状态为启用（status = 1）
2. 下次执行时间 <= 当前时间
3. 未超过结束时间（如果设置了end_time）
4. 未达到最大执行次数（如果设置了max_executions）

### 工作流执行

对于每个符合条件的任务：

1. 获取用户信息以获取team_id
2. 解析任务的输入参数（input字段）
3. 调用`start_workflow`函数执行工作流
4. 更新任务执行结果和统计信息

### 下次执行时间计算

根据任务的重复类型计算下次执行时间：

- **minute**：当前时间 + 间隔分钟数
- **hour**：当前时间 + 间隔小时数
- **day**：当前时间 + 间隔天数
- **week**：根据指定的星期几计算下次执行时间
- **month**：根据指定的月份日期计算下次执行时间
- **year**：根据指定的月份和日期计算下次执行时间

## 日志记录

执行器使用系统日志记录所有重要操作：

- 任务查询和筛选过程
- 工作流执行成功/失败
- 下次执行时间计算
- 错误信息和异常堆栈

日志级别：
- **INFO**：正常操作记录
- **DEBUG**：详细调试信息
- **ERROR**：错误和异常信息

## 生产环境部署

### 1. 使用Systemd服务

创建服务文件 `/etc/systemd/system/nexusai-scheduled-tasks.service`：

```ini
[Unit]
Description=NexusAI Scheduled Task Executor
After=network.target

[Service]
Type=simple
User=nexusai
Group=nexusai
WorkingDirectory=/path/to/NexusAI
ExecStart=/usr/bin/python3 /path/to/NexusAI/task/timed_execution_of_workflow.py --mode daemon --interval 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable nexusai-scheduled-tasks
sudo systemctl start nexusai-scheduled-tasks
```

### 2. 使用Supervisor

在supervisor配置中添加：

```ini
[program:nexusai-scheduled-tasks]
command=python3 /path/to/NexusAI/task/timed_execution_of_workflow.py --mode daemon --interval 60
directory=/path/to/NexusAI
user=nexusai
autostart=true
autorestart=true
stderr_logfile=/var/log/nexusai/scheduled-tasks.err.log
stdout_logfile=/var/log/nexusai/scheduled-tasks.out.log
```

### 3. 使用Cron（不推荐用于生产环境）

如果只需要定期执行，可以使用cron：

```bash
# 每分钟检查一次
* * * * * cd /path/to/NexusAI && python3 task/timed_execution_of_workflow.py --mode once
```

## 注意事项

1. **数据库权限**：确保执行脚本的用户有数据库读写权限
2. **环境变量**：确保所有必要的环境变量已正确设置
3. **依赖模块**：确保所有Python依赖模块已安装
4. **日志空间**：定期清理日志文件以免占用过多磁盘空间
5. **并发控制**：避免同时运行多个执行器实例

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置和连接字符串
   - 确认数据库服务是否正常运行
   - 检查网络连接

2. **工作流执行失败**
   - 检查应用和工作流是否存在
   - 确认用户权限
   - 查看工作流配置是否正确

3. **任务状态异常**
   - 检查任务配置参数
   - 确认时间设置是否合理
   - 查看执行日志

### 调试方法

1. 运行测试脚本检查基本功能
2. 查看应用日志文件
3. 使用单次执行模式进行调试
4. 检查数据库中的任务状态

## 更新日志

- **v1.0.0**：初始版本，实现基本的定时任务执行功能
  - 支持多种重复模式
  - 完善的错误处理
  - 详细的日志记录
  - 支持一次性和守护进程模式