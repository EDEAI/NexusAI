import io
from typing import Any, Generator
import matplotlib.pyplot as plt
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class PieChartTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        data = tool_parameters.get("data", "")
        if not data:
            yield self.create_text_message("Please input data")
        data = data.split(";")
        categories = tool_parameters.get("categories") or None
        if all((i.isdigit() for i in data)):
            data = [int(i) for i in data]
        else:
            data = [float(i) for i in data]
        (flg, ax) = plt.subplots()
        if categories:
            categories = categories.split(";")
            if len(categories) != len(data):
                categories = None
        if categories:
            ax.pie(data, labels=categories)
        else:
            ax.pie(data)
        buf = io.BytesIO()
        flg.savefig(buf, format="png")
        buf.seek(0)
        plt.close(flg)
        yield self.create_text_message("the pie chart is saved as an image.")
        yield self.create_blob_message(blob=buf.read(), meta={"mime_type": "image/png"})
