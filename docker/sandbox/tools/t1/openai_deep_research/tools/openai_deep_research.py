from collections.abc import Generator
from typing import Any

from openai import OpenAI

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class OpenaiDeepResearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials[
            "apikey"
        ]
        prompt = tool_parameters["prompt"]
        model = tool_parameters["model"]
        client = OpenAI(api_key=api_key)
        resp = client.responses.create(
            model=model,
            # Options: "low", "medium", "high"; o4-mini only support "medium"
            reasoning={
                "effort": "medium",
            },
            input=prompt,
            background=True,
            tools=[
                {
                    "type": "web_search_preview",
                    "user_location": {"type": "approximate"},
                    "search_context_size": "medium",
                }
            ],
            store=True,  # So you can view the log at your OpenAI account: Dashboard -> Logs
        )
        task_id = resp.id
        yield self.create_text_message(str(task_id))