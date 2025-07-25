from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Generator, Any, Dict
from .image_utils import (
    validate_params,
    submit_image_task,
    poll_task_status
)

CREATIVEPOSTER_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"

class CreativePoster(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        1. 验证必填参数
        2. 构建请求 payload
        3. 提交任务并获取 task_id
        4. 轮询并产出结果
        5. 捕获任何异常并产出文本错误
        """
        try:
            # 参数校验
            validate_params(tool_parameters, ["model", "title", "wh_ratios", "lora_name"])

            # 获取 API Key
            api_key = self.runtime.credentials.get("tonyi_api_key")

            # 构造接口请求体
            payload = {
                "model": tool_parameters["model"],
                "input": {
                    "title": tool_parameters["title"],
                    "sub_title": tool_parameters["sub_title"],
                    "body_text": tool_parameters["body_text"],
                    "prompt_text_zh": tool_parameters["prompt_text_zh"],
                    "wh_ratios": tool_parameters["wh_ratios"],
                    "lora_name": tool_parameters["lora_name"],
                    "lora_weight": 0.8,
                    "ctrl_ratio": 0.7,
                    "ctrl_step": 0.7,
                    "generate_mode": "generate",
                    "generate_num": 1
                },
                "parameters": {}
            }

            # 提交任务
            task_id = submit_image_task(api_key, CREATIVEPOSTER_URL, payload)
            
            # 轮询并产出海报结果
            yield from poll_task_status(self, api_key, task_id)

        except Exception as e:
            # 返回错误信息
            yield self.create_text_message(str(e))
