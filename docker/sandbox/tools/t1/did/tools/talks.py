from utils.did_appx import DIDApp

import json
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class TalksTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app = DIDApp(
            api_key=self.runtime.credentials["did_api_key"],
            base_url=self.runtime.credentials["base_url"],
        )
        driver_expressions_str = tool_parameters.get("driver_expressions")
        driver_expressions = (
            json.loads(driver_expressions_str) if driver_expressions_str else None
        )
        script = {
            "type": tool_parameters.get("script_type") or "text",
            "input": tool_parameters.get("text_input"),
            "audio_url": tool_parameters.get("audio_url"),
            "reduce_noise": tool_parameters.get("audio_reduce_noise", False),
        }
        script = {k: v for (k, v) in script.items() if v is not None and v != ""}
        config = {
            "stitch": tool_parameters.get("stitch", True),
            "sharpen": tool_parameters.get("sharpen"),
            "fluent": tool_parameters.get("fluent"),
            "result_format": tool_parameters.get("result_format") or "mp4",
            "pad_audio": tool_parameters.get("pad_audio"),
            "driver_expressions": driver_expressions,
        }
        config = {k: v for (k, v) in config.items() if v is not None and v != ""}
        options = {
            "source_url": tool_parameters["source_url"],
            "driver_url": tool_parameters.get("driver_url"),
            "script": script,
            "config": config,
        }
        options = {k: v for (k, v) in options.items() if v is not None and v != ""}
        if not options.get("source_url"):
            raise ValueError("Source URL is required")
        if script.get("type") == "audio":
            script.pop("input", None)
            if not script.get("audio_url"):
                raise ValueError("Audio URL is required for audio script type")
        if script.get("type") == "text":
            script.pop("audio_url", None)
            script.pop("reduce_noise", None)
            if not script.get("input"):
                raise ValueError("Text input is required for text script type")
        talks_result = app.talks(params=options, wait=True)
        if not talks_result:
            yield self.create_text_message("D-ID talks request failed.")
            return
        if not isinstance(talks_result, str):
            yield self.create_json_message(talks_result)
            return
        yield self.create_text_message(talks_result)
