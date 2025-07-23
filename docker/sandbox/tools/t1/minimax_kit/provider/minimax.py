from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.base import MiniMaxBaseTool


class MiniMaxProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_key = credentials.get("api_key")
            group_id = credentials.get("group_id")
            response = MiniMaxBaseTool(api_key=api_key, group_id=group_id).file_list(
                purpose="retrieval"
            )
            response.raise_for_status()
            status_code = response.json().get("base_resp", {}).get("status_code", -1)
            if status_code != 0:
                raise ToolProviderCredentialValidationError(
                    f"Invalid credentials. Please check your API key and group ID. {response.text}"
                )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
