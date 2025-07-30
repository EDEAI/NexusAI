from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from gradio_client import Client

class AbstractsIndexTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # Get parameters
            query = tool_parameters.get("query", "")
            
            if not query:
                yield self.create_text_message("Error: Query parameter cannot be empty")
                return
            
            # Get Gradio endpoint from provider configuration
            gradio_endpoint = self.runtime.credentials.get("gradio_endpoint")
            if not gradio_endpoint:
                yield self.create_text_message("Error: Gradio endpoint not configured")
                return
            
            # Create Gradio client and call API
            client = Client(gradio_endpoint)
            result = client.predict(
                query=query,
                api_name="/search"
            )
            
            # Return both text and json formats
            # First return text format
            if isinstance(result, (list, dict)):
                text_result = str(result)
            else:
                text_result = result
            yield self.create_text_message(text_result)
            
            # Then return JSON format
            yield self.create_json_message({
                "query": query,
                "result": result,
                "status": "success",
                "endpoint": gradio_endpoint
            })
                
        except Exception as e:
            # Error handling
            error_msg = f"Query failed: {str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "query": tool_parameters.get("query", ""),
                "result": None,
                "status": "error",
                "error": str(e)
            })