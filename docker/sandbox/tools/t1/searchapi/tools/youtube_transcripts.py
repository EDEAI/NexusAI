from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

SEARCH_API_URL = "https://www.searchapi.io/api/v1/search"


class SearchAPI:
    """
    SearchAPI tool provider.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize SearchAPI tool provider."""
        self.searchapi_api_key = api_key

    def run(self, video_id: str, language: str, **kwargs: Any) -> str:
        """Run video_id through SearchAPI and parse result."""
        return self._process_response(self.results(video_id, language, **kwargs))

    def results(self, video_id: str, language: str, **kwargs: Any) -> dict:
        """Run video_id through SearchAPI and return the raw result."""
        params = self.get_params(video_id, language, **kwargs)
        response = requests.get(
            url=SEARCH_API_URL, params=params, headers={"Authorization": f"Bearer {self.searchapi_api_key}"}
        )
        response.raise_for_status()
        return response.json()

    def get_params(self, video_id: str, language: str, **kwargs: Any) -> dict[str, str]:
        """Get parameters for SearchAPI."""
        return {
            "engine": "youtube_transcripts",
            "video_id": video_id,
            "lang": language or "en",
            **{key: value for (key, value) in kwargs.items() if value not in {None, ""}},
        }

    @staticmethod
    def _process_response(res: dict) -> str:
        """Process response from SearchAPI."""
        if "error" in res:
            return res["error"]
        toret = ""
        if "transcripts" in res and "text" in res["transcripts"][0]:
            for item in res["transcripts"]:
                toret += item["text"] + " "
        if toret == "":
            toret = "No good search result found"
        return toret


class YoutubeTranscriptsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the SearchApi tool.
        """
        video_id = tool_parameters["video_id"]
        language = tool_parameters.get("language", "en")
        api_key = self.runtime.credentials["searchapi_api_key"]
        result = SearchAPI(api_key).run(video_id, language=language)
        yield self.create_text_message(text=result)
