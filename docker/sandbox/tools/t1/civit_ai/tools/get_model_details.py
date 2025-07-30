from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .civitai_client import CivitAI


class ModelDetails(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("civitai_api_key")
        if not api_key:
            yield self.create_text_message("Please input api_key")
        cli = CivitAI(api_key)
        if not "model_id" in tool_parameters:
            yield self.create_text_message("Please input model_id")
            return
        model_id = tool_parameters["model_id"]
        json = cli.get_model_details(str(model_id))
        yield self.create_json_message(json)

        mapping = {"name": json["name"],
                   "description": json["description"],
                   "type": json["type"],
                   "nsfw": json["nsfw"],
                   "tags": json["tags"],
                   "nsfw_level": json["nsfwLevel"],
                   "download_count": json["stats"]["downloadCount"],
                   "thumbs_up_count": json["stats"]["thumbsUpCount"],
                   "thumbs_down_count": json["stats"]["thumbsDownCount"],
                   "creator_name": json["creator"]["username"],
                   "creator_icon_url": json["creator"]["image"],
                   "version_ids": [v["id"] for v in json["modelVersions"]]}
        for key in mapping:
            yield self.create_variable_message(
                key, mapping[key]
            )
