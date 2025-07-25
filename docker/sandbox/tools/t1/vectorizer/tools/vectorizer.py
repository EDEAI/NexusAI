from collections.abc import Generator
from typing import Any
from httpx import post
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from dify_plugin.file.file import File, FileType


class VectorizerTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        api_key_name = self.runtime.credentials.get("api_key_name", "")
        api_key_value = self.runtime.credentials.get("api_key_value", "")
        mode = tool_parameters.get("mode", "test")
        image: File | None = tool_parameters.get("image")
        if not image:
            raise ValueError("Got no image")
        if image.type != FileType.IMAGE:
            raise ValueError("Not a valid image")

        image_binary = image.blob
        response = post(
            "https://vectorizer.ai/api/v1/vectorize",
            data={"mode": mode},
            files={"image": image_binary},
            auth=(api_key_name, api_key_value),
            timeout=30,
        )
        if response.status_code != 200:
            raise Exception(response.text)
        
        yield self.create_text_message("the vectorized svg is saved as an image.")
        yield self.create_blob_message(
            blob=response.content, meta={"mime_type": "image/svg+xml"}
        )
