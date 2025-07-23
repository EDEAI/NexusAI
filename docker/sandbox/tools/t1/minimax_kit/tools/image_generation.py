from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.base import MiniMaxBaseTool


class MiniMaxImageGenerationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")
        group_id = self.runtime.credentials.get("group_id")
        minimax = MiniMaxBaseTool(api_key=api_key, group_id=group_id)

        model = tool_parameters.get("model")
        prompt = tool_parameters.get("prompt")
        aspect_ratio = tool_parameters.get("aspect_ratio")
        prompt_optimizer = tool_parameters.get("prompt_optimizer")
        n = tool_parameters.get("n")

        response = minimax.text_to_image(
            model=model,
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            response_format="url",
            prompt_optimizer=prompt_optimizer,
            n=n,
        )
        if response.status_code != 200:
            yield self.create_text_message(
                f"Image generation failed {response.status_code} {response.text}"
            )
            return
        status_code = response.json().get("base_resp", {}).get("status_code", -1)
        if status_code != 0:
            yield self.create_text_message(f"Image generation failed {response.text}")
            return
        image_data = response.json().get("data", {})
        image_urls = image_data.get("image_urls")

        if not image_urls:
            yield self.create_text_message(f"Image generation failed {response.text}")
            return

        for image_url in image_urls:
            yield self.create_image_message(image_url)

        image_data = {
            "image_urls": image_urls,
        }

        yield self.create_json_message(image_data)
