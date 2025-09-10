import logging
from typing import Any

from dify_plugin.config.logger_format import plugin_logger_handler
from maintainer.ai.model.nacos_mcp_info import McpServerDetailInfo, McpToolMeta
from mcp import types

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

def is_tool_enabled(tool_name: str , _tools_meta :dict[str, McpToolMeta]) -> bool:
	if _tools_meta is None:
		return True
	if tool_name in _tools_meta:
		mcp_tool_meta = _tools_meta[tool_name]
		if mcp_tool_meta.enabled is not None:
			if not mcp_tool_meta.enabled:
				return False
	return True

def update_tools_according_to_nacos(tools :types.ListToolsResult
		,mcp_server_detail :McpServerDetailInfo):

	def update_args_description(_local_args: dict[str, Any],
			_nacos_args: dict[str, Any]):
		for key, value in _local_args.items():
			if key in _nacos_args and "description" in _nacos_args[key]:
				_local_args[key]["description"] = _nacos_args[key][
					"description"]



	if (mcp_server_detail is None or mcp_server_detail.toolSpec is None or
			mcp_server_detail.toolSpec.tools is None):
		return tools.tools

	nacos_tools_meta = mcp_server_detail.toolSpec.toolsMeta
	nacos_tools = mcp_server_detail.toolSpec.tools
	new_tools = []
	for tool in tools.tools:
		if not is_tool_enabled(tool.name, nacos_tools_meta):
			continue
		for nacos_tool in nacos_tools:
			if tool.name == nacos_tool.name:
				try:
					if nacos_tool.description is not None:
						tool.description = nacos_tool.description
					local_args = tool.inputSchema["properties"]
					nacos_args = nacos_tool.inputSchema["properties"]
					update_args_description(local_args, nacos_args)
				except Exception as e:
					logger.info(f"update tool {tool.name} args description failed: {e}")
				break
		new_tools.append(tool)

	return new_tools


