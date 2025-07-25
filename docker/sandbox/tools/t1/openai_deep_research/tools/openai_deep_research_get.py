from collections.abc import Generator
from typing import Any

from openai import OpenAI

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class OpenaiDeepResearchGetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials[
            "apikey"
        ]
        task_id = tool_parameters["taskid"]
        client = OpenAI(api_key=api_key)
        resp = client.responses.retrieve(task_id)
        if resp.status == "failed":
            raise Exception(
                f"Task {task_id} failed: {resp.error}. Please contact OpenAI for assistance."
            )
        elif resp.status == "completed":
            def extract_markdown_from_response(resp) -> str:
                """Extracts the markdown content from the deep research API response."""
                if resp.status != "completed":
                    return str(resp.status)

                if not hasattr(resp, "output"):
                    return "Empty response or no output found."

                for item in resp.output:
                    if hasattr(item, "type") and item.type == "message":
                        for content_item in item.content:
                            if hasattr(content_item, "type") and content_item.type == "output_text":
                                return content_item.text
                return "Empty response or no output found."
            markdown_content = extract_markdown_from_response(resp)
            yield self.create_text_message(markdown_content)
            yield self.create_json_message({
                "task_id": task_id,
                "status": str(resp.status),
            })
        else:
            yield self.create_text_message(f"Task is still in progress, current status: {str(resp.status)}")
            yield self.create_json_message({
                "task_id": task_id,
                "status": str(resp.status)
            })
