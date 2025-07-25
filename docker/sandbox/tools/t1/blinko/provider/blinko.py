from typing import Dict, Any, Optional, List
import os
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.blinko import BlinkoTool


class BlinkoProvider(ToolProvider):
    def __init__(self, env=None):
        """
        Initialize the Blinko provider
        """
        super().__init__()
        
    def validate_env(self) -> List[str]:
        """
        Validate the environment variables
        """
        errors = []
        if not os.environ.get('BLINKO_TOKEN'):
            errors.append("Missing BLINKO_TOKEN environment variable")
        return errors

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in BlinkoTool.from_credentials(credentials).invoke(
                tool_parameters={"query": "test credentials"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
