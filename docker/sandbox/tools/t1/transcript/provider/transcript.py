from typing import Any
from dify_plugin import ToolProvider


class YouTubeTranscriptProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        No credentials needed for YouTube Transcript API
        """
        pass
