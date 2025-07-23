from utils.did_appx import DIDApp

import json
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class AnimationsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app = DIDApp(
            api_key=self.runtime.credentials["did_api_key"],
            base_url=self.runtime.credentials["base_url"],
        )

        config = {
            "stitch": tool_parameters.get("stitch", True),
            "mute": tool_parameters.get("mute"),
            "result_format": tool_parameters.get("result_format") or "mp4",
        }
        config = {k: v for (k, v) in config.items() if v is not None and v != ""}
        options = {
            "source_url": tool_parameters["source_url"],
            "driver_url": tool_parameters.get("driver_url"),
            "config": config,
        }
        options = {k: v for (k, v) in options.items() if v is not None and v != ""}
        if not options.get("source_url"):
            raise ValueError("Source URL is required")
        if config.get("logo_url"):
            if not config.get("logo_x"):
                raise ValueError(
                    "Logo X position is required when logo URL is provided"
                )
            if not config.get("logo_y"):
                raise ValueError(
                    "Logo Y position is required when logo URL is provided"
                )
        animations_result = app.animations(params=options, wait=True)
        if not isinstance(animations_result, str):
            animations_result = json.dumps(
                animations_result, ensure_ascii=False, indent=4
            )
        if not animations_result:
            yield self.create_text_message("D-ID animations request failed.")
        yield self.create_text_message(animations_result)
