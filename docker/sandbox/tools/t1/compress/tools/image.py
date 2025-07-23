from collections.abc import Generator
from typing import Any
import io

from PIL import Image
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class CompressImageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        image_file: File = tool_parameters["image_file"]
        target_size = tool_parameters["target_size"]

        if image_file.type != "image":
            raise ValueError("The file is not an image, file type: " + image_file.type)

        compressed_bytes, info = compress_image(image_file.blob, target_size)

        yield self.create_json_message(info)
        yield self.create_blob_message(blob=compressed_bytes, meta={"mime_type": image_file.mime_type})


def compress_image(input_bytes, target_size_mb=1.0, max_attempts=10):
    img = Image.open(io.BytesIO(input_bytes))
    original_size_mb = len(input_bytes) / (1024 * 1024)
    if img.mode != "RGB":
        img = img.convert("RGB")

    original_dimensions = img.size

    # if image is too large, resize it
    max_size = 1920
    ratio = max_size / max(img.size)
    if ratio < 1:
        new_size = tuple(int(x * ratio) for x in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # binary search for the best quality
    min_quality = 5
    max_quality = 95
    current_quality = 85
    attempt = 0
    result_bytes = None
    final_size_mb = 0

    while attempt < max_attempts:
        # save image to binary stream in memory
        temp_buffer = io.BytesIO()
        img.save(temp_buffer, format="JPEG", quality=current_quality, optimize=True)
        temp_bytes = temp_buffer.getvalue()
        current_size_mb = len(temp_bytes) / (1024 * 1024)

        # update the best result
        if result_bytes is None or abs(current_size_mb - target_size_mb) < abs(
            final_size_mb - target_size_mb
        ):
            result_bytes = temp_bytes
            final_size_mb = current_size_mb

        # check if the target size is reached
        if abs(current_size_mb - target_size_mb) < 0.1:
            break

        if current_size_mb > target_size_mb:
            max_quality = current_quality - 1
        else:
            min_quality = current_quality + 1

        current_quality = (min_quality + max_quality) // 2

        if max_quality <= min_quality:
            break

        attempt += 1

    info = {
        "original_size": f"{round(original_size_mb, 2)} MB",
        "compressed_size": f"{round(final_size_mb, 2)} MB",
        "compression_ratio": f"{round(final_size_mb / original_size_mb * 100, 2)}%",
        "final_quality": current_quality,
        "original_dimensions": original_dimensions,
        "final_dimensions": img.size,
        "attempts": attempt + 1,
    }

    return result_bytes, info