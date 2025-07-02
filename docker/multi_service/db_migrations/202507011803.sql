ALTER TABLE `chatroom_messages`
	ADD COLUMN `updated_time` DATETIME NULL DEFAULT NULL COMMENT 'Message updated time' AFTER `created_time`;

CREATE TABLE `mcp_tool_use_records` (
	`id` INT NOT NULL AUTO_INCREMENT COMMENT 'MCP tool use record ID',
	`agent_id` INT NOT NULL COMMENT 'ID of the Agent that invokes the MCP tool',
	`agent_run_id` INT NOT NULL COMMENT 'App run ID of the Agent',
	`chatroom_id` INT NOT NULL COMMENT 'ID of the Chatroom in which the MCP tool use happens',
	`chatroom_message_id` INT NOT NULL COMMENT 'ID of the Chatroom message that the tool use belongs to',
	`index` INT NOT NULL COMMENT 'Index of the MCP tool use in current LLM request',
	`tool_name` VARCHAR(255) NOT NULL COMMENT 'MCP tool name',
	`args` LONGTEXT NULL DEFAULT NULL COMMENT 'MCP tool use args',
	`skill_id` INT NOT NULL DEFAULT '0' COMMENT 'ID of the Skill corresponding to the MCP tool',
	`workflow_id` INT NOT NULL DEFAULT '0' COMMENT 'ID of the Workflow corresponding to the MCP tool',
	`app_run_id` INT NOT NULL DEFAULT '0' COMMENT 'App run ID of the Skill/Workflow',
	`workflow_run_status` LONGTEXT NULL DEFAULT NULL COMMENT 'Workflow run status',
	`result` TEXT NULL DEFAULT NULL COMMENT 'MCP tool use result',
	`created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Tool use record created time',
	`updated_time` datetime DEFAULT NULL COMMENT 'Tool use record updated time',
	`status` TINYINT(1) NULL DEFAULT '1' COMMENT 'MCP tool use status 1: Pending 2: Running 3: Waiting for confirmation (Workflow) 4: Success (Skill/Workflow) or Finished 5: Failed (Skill/Workflow) or Stopped',
	PRIMARY KEY (`id`),
	INDEX `agent_id` (`agent_id`),
	INDEX `agent_run_id` (`agent_run_id`),
	INDEX `chatroom_id` (`chatroom_id`),
	INDEX `chatroom_message_id` (`chatroom_message_id`),
	INDEX `skill_id` (`skill_id`),
	INDEX `workflow_id` (`workflow_id`),
	INDEX `app_run_id` (`app_run_id`),
	INDEX `status` (`status`),
	CONSTRAINT `mcp_tool_use_records_chk_1` CHECK (json_valid(`args`)),
	CONSTRAINT `mcp_tool_use_records_chk_2` CHECK (json_valid(`workflow_run_status`))
)
COMMENT='MCP Tool Use Record Data Table'
COLLATE='utf8mb4_general_ci'
;
