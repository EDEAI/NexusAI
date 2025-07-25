from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import NpmRegistryClient


class NpmGetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        package_name: str = tool_parameters.get("package_name", "")
        version: str = tool_parameters.get("version", "")
        if not package_name:
            yield self.create_text_message("Please provide a package name.")
            return

        try:
            with NpmRegistryClient() as client:

                if not version:
                    package_info = client.get_package_info(package_name)
                    yield self.create_json_message(package_info.model_dump())
                else:
                    version_info = client.get_package_version_info(
                        package_name, version
                    )
                    yield self.create_json_message(version_info.model_dump())

        except Exception as e:
            yield self.create_text_message(
                f"An error occurred while getting npm package information: {str(e)}"
            )
