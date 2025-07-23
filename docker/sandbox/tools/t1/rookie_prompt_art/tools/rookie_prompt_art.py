from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage
from utils.prompt_loader import PromptLoader
from datetime import datetime

class RookiePromptArtTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        model_info = tool_parameters.get("model")
        art_type = tool_parameters.get("category", "one_sentence_novel")
        # 初始化模板加载器
        prompt_loader = PromptLoader()

        context = {
            "author": tool_parameters.get("author","jaguarliu"),
            "datetime": datetime.today().strftime("%Y-%m-%d")
        }

        prompt = prompt_loader.get_prompt(context, art_type)
        response = self.session.model.llm.invoke(
            model_config=LLMModelConfig(
                provider=model_info.get('provider'),
                model=model_info.get('model'),
                mode=model_info.get('mode'),
                completion_params=model_info.get('completion_params')
            ),
            prompt_messages=[
                SystemPromptMessage(content=prompt),
                UserPromptMessage(
                    content=f"用户的输入是：{tool_parameters.get('query')}"
                )
            ],
            stream=False
        )

        yield self.create_blob_message(response.message.content,meta={
            'mime_type': 'image/svg+xml',
            'filename': 'result.svg'
        })
