from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from services.microsoft_todo_api import get_todos, MicrosoftTodoApiException


class GetTodosTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.access_token = self.runtime.credentials.get("access_token")
        if not self.access_token:
            raise ToolProviderCredentialValidationError("Missing Microsoft access token.")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            include_completed = tool_parameters.get("include_completed", "false")
            todos = get_todos(self.access_token, include_completed)

            if not todos:
                yield self.create_text_message("✅ No matching todos found.")
                return

            response = "📋 Your Microsoft Todo tasks:\n"
            for todo in todos[:10]:  # Limit to 10 tasks for readability
                title = todo.get("title", "Untitled")
                status = todo.get("status", "unknown").capitalize()
                due = todo.get("dueDateTime", {}).get("dateTime", "No due date")
                response += f"- {title} | Status: {status} | Due: {due}\n"

            yield self.create_text_message(response)

        except MicrosoftTodoApiException as e:
            raise ToolProviderCredentialValidationError(f"[Microsoft Todo API Error] {str(e)}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
