from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from services.microsoft_todo_api import create_todo, MicrosoftTodoApiException


class CreateTodoTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.access_token = self.runtime.credentials.get("access_token")
        if not self.access_token:
            raise ToolProviderCredentialValidationError("Missing Microsoft access token.")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters["title"]
            due_date = tool_parameters.get("due_date")  # optional

            task = create_todo(self.access_token, title, due_date)

            response = f"✅ Todo created:\n- Title: {task.get('title')}\n- Status: {task.get('status')}"
            if due_date:
                response += f"\n- Due: {task.get('dueDateTime', {}).get('dateTime', 'N/A')}"

            yield self.create_text_message(response)

        except MicrosoftTodoApiException as e:
            raise ToolProviderCredentialValidationError(f"[Microsoft Todo API Error] {str(e)}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")

