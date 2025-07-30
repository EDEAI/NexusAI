from typing import Any,Generator
from openai import OpenAI
from yarl import URL
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class StepfunTool(Tool):
    """Stepfun Image Generation Tool"""

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        base_url = self.runtime.credentials.get("stepfun_base_url") or "https://api.stepfun.com"
        base_url = str(URL(base_url) / "v1")
        client = OpenAI(api_key=self.runtime.credentials["stepfun_api_key"], base_url=base_url)
        extra_body = {}
        model = "step-1x-medium"
        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            yield self.create_text_message("Please input prompt")
        if len(prompt) > 1024:
            yield self.create_text_message("The prompt length should less than 1024")
        seed = tool_parameters.get("seed", 0)
        if seed > 0:
            extra_body["seed"] = seed
        steps = tool_parameters.get("steps", 50)
        if steps > 0:
            extra_body["steps"] = steps
        cfg_scale = tool_parameters.get("cfg_scale", 7.5)
        if cfg_scale > 0:
            extra_body["cfg_scale"] = cfg_scale
        response = client.images.generate(
            prompt=prompt,
            model=model,
            size=tool_parameters.get("size", "1024x1024"),
            n=tool_parameters.get("n", 1),
            extra_body=extra_body,
        )
        for image in response.data:
            yield self.create_image_message(image_url=image.url)
            yield self.create_json_message({"url": image.url})
