import logging
from dify_plugin.config.logger_format import plugin_logger_handler
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class MermaidProvider(ToolProvider):
    """
    This class provides the functionality to convert mermaid code to various document formats.
    It is responsible for validating the credentials required for the conversion tools.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            logger.info("Credentials validation successful.")
        except Exception as e:
            logger.error(f"Credential validation failed: {e}", exc_info=True)
            raise ToolProviderCredentialValidationError(str(e))
