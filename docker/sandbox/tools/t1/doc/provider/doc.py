from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class DocProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # For this tool, no API credentials are needed
        # We're using python-docx which is a pure Python library
        pass
