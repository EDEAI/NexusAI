import io
from typing import Any, Generator
import matplotlib.pyplot as plt
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class BarChartTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        data = tool_parameters.get("data", "")
        if not data:
            yield self.create_text_message("Please input data")
        data = data.split(";")
        if all((i.isdigit() for i in data)):
            data = [int(i) for i in data]
        else:
            data = [float(i) for i in data]
        axis = tool_parameters.get("x_axis") or None
        if axis:
            axis = axis.split(";")
            if len(axis) != len(data):
                axis = None
        (flg, ax) = plt.subplots(figsize=(10, 8))
        if axis:
            axis = [label[:10] + "..." if len(label) > 10 else label for label in axis]
            ax.set_xticklabels(axis, rotation=45, ha="right")
            ax.bar(range(len(data)), data)
            ax.set_xticks(range(len(data)))
        else:
            ax.bar(range(len(data)), data)
        buf = io.BytesIO()
        flg.savefig(buf, format="png")
        buf.seek(0)
        plt.close(flg)
        yield self.create_text_message("the bar chart is saved as an image.")
        yield self.create_blob_message(blob=buf.read(), meta={"mime_type": "image/png"})
