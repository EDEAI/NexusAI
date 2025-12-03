ALTER TABLE `custom_tools`
	CHANGE COLUMN `code` `code` MEDIUMTEXT NULL COMMENT 'Tool code' COLLATE 'utf8mb4_general_ci' AFTER `dependencies`;

ALTER TABLE `ai_tool_llm_records`
	CHANGE COLUMN `user_prompt` `user_prompt` MEDIUMTEXT NULL COMMENT 'Prompt word filled in by the user' COLLATE 'utf8mb4_general_ci' AFTER `inputs`;
