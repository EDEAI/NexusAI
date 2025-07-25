# SFTP Provider
# This file is required by the Dify plugin system, but doesn't need content
# since we're only using it to group the tool files together.

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SftpProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
