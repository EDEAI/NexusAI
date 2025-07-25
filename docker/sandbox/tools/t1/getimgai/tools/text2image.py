import json
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from .getimgai_appx import GetImgAIApp
from dify_plugin import Tool


class Text2ImageTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app = GetImgAIApp(
            api_key=self.runtime.credentials["getimg_api_key"], base_url=self.runtime.credentials["base_url"]
        )
        options = {
            "style": tool_parameters.get("style"),
            "prompt": tool_parameters.get("prompt"),
            "aspect_ratio": tool_parameters.get("aspect_ratio"),
            "output_format": tool_parameters.get("output_format", "jpeg"),
            "response_format": tool_parameters.get("response_format", "url"),
            "width": tool_parameters.get("width"),
            "height": tool_parameters.get("height"),
            "steps": tool_parameters.get("steps"),
            "negative_prompt": tool_parameters.get("negative_prompt"),
            "prompt_2": tool_parameters.get("prompt_2"),
        }
        options = {k: v for (k, v) in options.items() if v}
        text2image_result = app.text2image(mode=tool_parameters.get("mode", "essential-v2"), params=options, wait=True)
        if not isinstance(text2image_result, str):
            text2image_result = json.dumps(text2image_result, ensure_ascii=False, indent=4)
        if not text2image_result:
            yield self.create_text_message("getimg.ai request failed.")
        yield self.create_text_message(text2image_result)
