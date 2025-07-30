from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .civitai_client import CivitAI


class ModelVersionDetails(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("civitai_api_key")
        if not api_key:
            yield self.create_text_message("Please input api_key")
        cli = CivitAI(api_key)
        if tool_parameters.get("model_version_id") is None:
            yield self.create_text_message("Please input model_version_id")
        json = cli.get_model_version(
            str(tool_parameters.get("model_version_id")))
        yield self.create_json_message(json)

        mapping = {"created_at": json["createdAt"],
                   "published_at": json["publishedAt"],
                   "url": json["downloadUrl"],
                   "download_count": json["stats"]["downloadCount"],
                   "file_names": [f["name"] for f in json["files"]],
                   "file_urls": [f["downloadUrl"] for f in json["files"]],
                   "image_urls": [img["url"] for img in json["images"]],
                   "image_nsfw": [img["nsfwLevel"] for img in json["images"]]}
        for key in mapping:
            yield self.create_variable_message(key, mapping[key])
