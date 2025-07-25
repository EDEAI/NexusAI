import time
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.base import MiniMaxBaseTool
import logging
from dify_plugin.config.logger_format import plugin_logger_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class MiniMaxVideoGenerationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")
        group_id = self.runtime.credentials.get("group_id")
        minimax = MiniMaxBaseTool(api_key=api_key, group_id=group_id)

        model = tool_parameters.get("model")
        prompt = tool_parameters.get("prompt")
        prompt_optimizer = tool_parameters.get("prompt_optimizer")
        duration = tool_parameters.get("duration")
        resolution = tool_parameters.get("resolution")
        first_frame_image = tool_parameters.get("first_frame_image")

        response = minimax.video_generation(
            model=model,
            prompt=prompt,
            prompt_optimizer=prompt_optimizer,
            duration=duration,
            resolution=resolution,
            first_frame_image=None if not first_frame_image else first_frame_image,
        )
        if response.status_code != 200:
            yield self.create_text_message(
                f"Video generation failed {response.status_code} {response.text}"
            )
            return
        task_id = response.json().get("task_id")
        if not task_id:
            yield self.create_text_message(f"Video generation failed {response.text}")
            return
        yield self.create_text_message(f"Video generation task id {task_id}")
        max_retries = 100
        retry_count = 0
        interval = 5
        video_file_id = None

        while retry_count < max_retries:
            time.sleep(interval)

            task_response = minimax.video_generation_task(task_id=task_id)
            if task_response.status_code != 200:
                yield self.create_text_message(
                    f"Video generation task failed {task_response.status_code} {task_response.text}"
                )
                break
            task_json = task_response.json()
            status_code = task_json.get("base_resp", {}).get("status_code", -1)
            if status_code != 0:
                yield self.create_text_message(
                    f"Video generation task failed  {task_response.text}"
                )
                break

            task_status = task_json.get("status")

            match task_status:
                case "Preparing":
                    logger.debug("Video generation task status preparing")
                case "Queueing":
                    logger.debug("Video generation task status queueing")
                case "Processing":
                    logger.debug("Video generation task status processing")
                case "Success":
                    video_file_id = task_json.get("file_id")
                    yield self.create_text_message(
                        "Video generation task status Success"
                    )
                    break
                case "failed":
                    yield self.create_text_message(
                        f"Video generation task status failed {task_response.text}"
                    )
                    break

            retry_count += 1

        if not video_file_id:
            yield self.create_text_message("Video generation failed")
            return
        file_response = minimax.file_retrieve(file_id=video_file_id)
        if file_response.status_code != 200:
            yield self.create_text_message(
                f"Video generation get file failed {file_response.status_code} {file_response.text}"
            )
            return
        video_url = file_response.json().get("file", {}).get("download_url")
        yield self.create_image_message(video_url)
        video_data = {"video_url": video_url}
        yield self.create_json_message(video_data)
