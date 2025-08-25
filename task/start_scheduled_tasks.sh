#!/bin/bash

# 定时任务执行器启动脚本
# 用法：
#   ./start_scheduled_tasks.sh              # 执行一次
#   ./start_scheduled_tasks.sh daemon       # 守护进程模式
#   ./start_scheduled_tasks.sh daemon 30    # 守护进程模式，30秒检查间隔

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/timed_execution_of_workflow.py"

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误：找不到定时任务执行脚本 $PYTHON_SCRIPT"
    exit 1
fi

# 获取参数
MODE=${1:-once}
INTERVAL=${2:-60}

echo "启动定时任务执行器..."
echo "模式: $MODE"

if [ "$MODE" = "daemon" ]; then
    echo "检查间隔: ${INTERVAL}秒"
    python3 "$PYTHON_SCRIPT" --mode daemon --interval "$INTERVAL"
elif [ "$MODE" = "once" ]; then
    python3 "$PYTHON_SCRIPT" --mode once
else
    echo "未知模式: $MODE"
    echo "用法: $0 [once|daemon] [interval_seconds]"
    exit 1
fi