from collections.abc import Generator
from typing import Any
import random
import io

import json_repair
import imagesize
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage, ImagePromptMessageContent


SYSTEM_PROMPT = """
1. Detect items, with no more than 20 items. 
2. Output a json list where each entry contains the 2D bounding box in "box_2d" and {label} in "label".
"""

BOX_TEMPLATE = """
<div style="position: absolute; left: {x1}px; top: {y1}px; width: {w}px;height: {h}px; border: 2px solid {color}; background-color: rgba(255,255,255,0.6);color: {color}; font-weight: bold; padding: 2px 4px; font-size: 16px;">
{label}
</div>
"""

HTML_TEMPLATE = """
<html>
<head>
  <meta charset="utf-8">
  <title>标注展示</title>
</head>
<body>

<div style="position: relative; width: {w}px; height: {h}px; background-image: url('{url}'); background-size: contain; background-repeat: no-repeat; background-position: top left;">
{box_html}
</div>

</body>
</html>
"""

def convert_boxes_to_absolute(boxes, width, height):
    abs_boxes = []
    for box in boxes:
        y1_rel, x1_rel, y2_rel, x2_rel = box["box_2d"]
        abs_x1 = int(x1_rel / 1000 * width)
        abs_y1 = int(y1_rel / 1000 * height)
        abs_x2 = int(x2_rel / 1000 * width)
        abs_y2 = int(y2_rel / 1000 * height)
        abs_boxes.append({
            "label": box["label"],
            "box_2d_abs": [abs_x1, abs_y1, abs_x2, abs_y2]
        })
    return abs_boxes


def convert_boxes_to_html(boxes, width, height, image_url):
    html_boxes = []
    for box in boxes:
        x1_abs, y1_abs, x2_abs, y2_abs = box["box_2d_abs"]
        x1 = x1_abs
        y1 = y1_abs
        x2 = x2_abs
        y2 = y2_abs
        w = x2 - x1
        h = y2 - y1
        label = box["label"]
        color = f"rgb({random.randint(100, 255)},{random.randint(100, 255)},{random.randint(100, 255)})"
        html = BOX_TEMPLATE.format(
            x1=x1, y1=y1, x2=x2, y2=y2, w=w, h=h, label=label, color=color
        )
        html_boxes.append(html)

    final_html = HTML_TEMPLATE.format(
        w=width, h=height, url=image_url, box_html="\n".join(html_boxes)
    )
    return final_html


class ObjectDetectionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        image = tool_parameters.get("image")
        if image.type != "image":
            raise ValueError("Input must be an image")

        label = tool_parameters.get("labels")
        response = self.session.model.llm.invoke(
            model_config=tool_parameters.get('model'),
            prompt_messages=[
                SystemPromptMessage(
                    content=SYSTEM_PROMPT.format(label=label)
                ),
                UserPromptMessage(
                    content=[ImagePromptMessageContent(
                        format=image.extension.removeprefix("."),
                        mime_type=image.mime_type,
                        url=image.url,
                    )]
                )
            ],
            stream=True
        )

        final_message = ""
        for chunk in response:
            if chunk.delta.message:
                assert isinstance(chunk.delta.message.content, str)
                final_message += chunk.delta.message.content

        image_file = io.BytesIO(image.blob)
        width, height = imagesize.get(image_file)

        boxes = json_repair.loads(final_message)
        abs_boxes = convert_boxes_to_absolute(boxes, width, height)
        box_html = convert_boxes_to_html(abs_boxes, width, height, image.url)
        yield self.create_text_message(box_html)
        yield self.create_json_message({
            "result": abs_boxes
        })