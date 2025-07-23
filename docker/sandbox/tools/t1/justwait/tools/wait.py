import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WaitTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """等待指定的秒数"""
        # 获取参数
        seconds = tool_parameters.get("seconds", 5)
        
        # 确保seconds是一个数字且大于等于0
        try:
            seconds = float(seconds)
            if seconds < 0:
                seconds = 0
        except (ValueError, TypeError):
            seconds = 5
            
        # 输出开始等待的消息
        message = f"Waiting for {seconds} seconds..."
        yield self.create_text_message(message)
        
        # 等待指定的秒数
        time.sleep(seconds)
        
        # 输出等待完成的消息
        message = f"Waiting for {seconds} seconds... done"
        yield self.create_text_message(message)
        
        # 返回元数据
        yield self.create_variable_message("metadata", {
            "waited_seconds": seconds,
            "type": "fixed"
        }) 