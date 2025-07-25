from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Generator, Any, Dict
from .image_utils import (
    validate_params,
    submit_image_task,
    poll_task_status
)

DOODLE2IMAGE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"

class Doodle2Image(Tool):
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
            validate_params(tool_parameters, ["model", "prompt", "sketch_image_url", "size", "count", "style"])

            # 获取 API Key
            api_key = self.runtime.credentials.get("tonyi_api_key")

            # 构造接口请求体
            payload = {
                "model": tool_parameters["model"],
                "input": {
                    "sketch_image_url": tool_parameters["sketch_image_url"],
                    "prompt": tool_parameters["prompt"]
                },
                "parameters": {
                    "style": tool_parameters["style"],
                    "size": tool_parameters["size"],
                    "n": tool_parameters["count"],
                    "sketch_weight": tool_parameters.get("sketch_weight")
                }
            }

            # 提交任务
            task_id = submit_image_task(api_key, DOODLE2IMAGE_URL, payload)
            
            # 轮询并产出图片结果
            yield from poll_task_status(self, api_key, task_id)

        except Exception as e:
            # 返回错误信息
            yield self.create_text_message(str(e))
