from typing import Any
from tools.base import BaseStabilityAuthorization
from dify_plugin import ToolProvider


class StabilityToolProvider(ToolProvider, BaseStabilityAuthorization):
    """
    This class is responsible for providing the stability tool.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        This method is responsible for validating the credentials.
        """
        self.sd_validate_credentials(credentials)
