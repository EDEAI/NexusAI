from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import Tool


class CrossRefQueryDOITool(Tool):
    """
    Tool for querying the metadata of a publication using its DOI.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        doi = tool_parameters.get("doi")
        if not doi:
            raise ToolProviderCredentialValidationError("doi is required.")
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()
        message = response.get("message", {})
        yield self.create_json_message(message)
