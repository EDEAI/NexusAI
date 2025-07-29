ALTER TABLE `mcp_tool_use_records`
	CHANGE COLUMN `result` `result` MEDIUMTEXT NULL DEFAULT NULL COMMENT 'MCP tool use result' COLLATE 'utf8mb4_general_ci' AFTER `workflow_run_status`;
