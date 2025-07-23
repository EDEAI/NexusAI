from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from services.microsoft_todo_api import mark_todo_completed, MicrosoftTodoApiException


class MarkTodoCompletedTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.access_token = self.runtime.credentials.get("access_token")
        if not self.access_token:
            raise ToolProviderCredentialValidationError("Missing Microsoft access token.")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            task_id = tool_parameters["task_id"]

            updated_task = mark_todo_completed(self.access_token, task_id)

            title = updated_task.get("title", "Unknown Title")
            status = updated_task.get("status", "unknown")

            yield self.create_text_message(
                f"✅ Marked task as completed:\n- Title: {title}\n- Status: {status}"
            )

        except MicrosoftTodoApiException as e:
            raise ToolProviderCredentialValidationError(f"[Microsoft Todo API Error] {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
