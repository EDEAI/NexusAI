import time
import random
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RandomWaitTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """在指定范围内随机等待秒数"""
        # 获取参数
        min_seconds = tool_parameters.get("min_seconds", 1)
        max_seconds = tool_parameters.get("max_seconds", 10)
        
        # 确保参数是数字且min <= max
        try:
            min_seconds = float(min_seconds)
            max_seconds = float(max_seconds)
            
            if min_seconds < 0:
                min_seconds = 0
            if max_seconds < min_seconds:
                max_seconds = min_seconds
        except (ValueError, TypeError):
            min_seconds = 1
            max_seconds = 10
            
        # 生成随机等待时间
        wait_seconds = random.uniform(min_seconds, max_seconds)
        wait_seconds = round(wait_seconds, 2)  # 保留两位小数
        
        # 输出开始等待的消息
        message = f"Random waiting for {wait_seconds} seconds... (range: {min_seconds}-{max_seconds} seconds)"
        yield self.create_text_message(message)
        
        # 等待随机秒数
        time.sleep(wait_seconds)
        
        # 输出等待完成的消息
        message = f"Random waiting for {wait_seconds} seconds... (range: {min_seconds}-{max_seconds} seconds)"
        yield self.create_text_message(message)
        
        # 返回元数据
        yield self.create_variable_message("metadata", {
            "min_seconds": min_seconds,
            "max_seconds": max_seconds,
            "waited_seconds": wait_seconds,
            "type": "random"
        })