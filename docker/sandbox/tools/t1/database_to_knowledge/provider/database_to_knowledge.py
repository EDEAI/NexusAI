from typing import Any

from dify_plugin import ToolProvider
from tools.dify_knowledge_api_utils import auth


class DatabaseToKnowledgeProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        auth(credentials)
