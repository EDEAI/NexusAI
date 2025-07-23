from collections.abc import Generator
from typing import Any

from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from utils.jenkins_client import JenkinsClient

class GetBuildInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        client = JenkinsClient(**self.runtime.credentials)
        job_name = tool_parameters.get("job_name", "")
        build_number = tool_parameters.get("build_number", "")

        if not job_name or not build_number:
            yield self.create_text_message("Error: Job name and build number are required.")
            return

        try:
            info = client.get_build_info(job_name, build_number)
            yield self.create_json_message(info)
        except Exception as e:
            yield self.create_text_message(f"Error getting build info: {str(e)}")