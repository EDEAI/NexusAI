ALTER TABLE `mcp_tool_use_records`
	ADD COLUMN `result_is_truncated` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'If the MCP tool use result is truncated 0: No 1: Yes' AFTER `result`;