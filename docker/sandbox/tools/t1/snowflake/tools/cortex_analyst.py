from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import httpx


class CortexAnalystTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        payload = {}
        if self.runtime.credentials.get("pat"):
            if not self.runtime.credentials.get("account"):
                yield self.create_text_message(
                    "Account is required for PAT authentication."
                )

            if not tool_parameters.get("semantic_model") and not tool_parameters.get("semantic_view"):
                yield self.create_text_message(
                    "Either semantic_model or semantic_view is required for Cortex Analyst."
                )

            if tool_parameters.get("semantic_model"):
                models = [model.strip() for model in tool_parameters.get("semantic_model").split(",") if model.strip()]
                if len(models) == 1:
                    payload["semantic_model_file"] = models[0]
                else:
                    payload["semantic_models"] = [{"semantic_model_file": model} for model in models]
            else:
                views = [view.strip() for view in tool_parameters.get("semantic_view").split(",") if view.strip()]
                if len(views) == 1:
                    payload["semantic_view_file"] = views[0]
                else:
                    yield self.create_text_message(
                        "Only one semantic_view is allowed at a time."
                    )

            if not tool_parameters.get("message"):
                yield self.create_text_message(
                    "Message is required for Cortex Analyst."
                )

            endpoint = "https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message".format(
                account=self.runtime.credentials.get("account")
            )
            try:
                messages = []
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": tool_parameters.get("message", None),
                            }
                        ],
                    }
                )
                payload["messages"] = messages

                response = httpx.post(
                    endpoint,
                    headers={
                        "Authorization": "Bearer {}".format(
                            self.runtime.credentials.get("pat")
                        ),
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=60,
                )
                if response.status_code == 200:
                    yield self.create_json_message(self._parse_response(response.json()))
                else:
                    yield self.create_text_message(
                        f"Error: {response.status_code} - {response.text} - {payload}"
                    )
            except Exception as e:
                yield self.create_text_message(f"Exception: {str(e)}")
        else:
            yield self.create_text_message("PAT authentication is required.")

    def _parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the response from Cortex Analyst API
        """
        
        res = {}

        res['request_id'] = response.get("request_id", None)
        res['metadata'] = response.get("response_metadata", None)
        res['metadata']['semantic_model_selection'] = response.get("semantic_model_selection", None)

        if not response.get("message"):
            return res
        
        for content in response["message"].get("content",[]):
            if content.get("type") == "text":
                res['text'] = content.get('text', None)
            if content.get("type") == "sql":
                res['sql'] = content.get('statement', None)
                res['confidence'] = content.get('confidence', None)
            if content.get('suggestion'):
                res['suggestion'] = content.get('suggestions', None)

        if response.get("warnings"):
            res['warnings'] = response.get("warnings")

        return res
