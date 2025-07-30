from collections.abc import Generator
from typing import Any
import base64
import mimetypes

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class EmbedAsBase64Tool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file = tool_parameters.get("file")
        link_text = tool_parameters.get("link_text", "")
        mime_type = tool_parameters.get("mime_type", "")
        format = tool_parameters.get("format", "plain")

        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file.filename)
        is_image = mime_type.startswith("image/")
        base64_blob = base64.b64encode(file.blob).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{base64_blob}"

        if format == "markdown":
            link_text = link_text or file.filename
            result = f"![{link_text}]({data_uri})" if is_image else f"[{link_text}]({data_uri})"
        else:
            result = data_uri

        yield self.create_text_message(result)
