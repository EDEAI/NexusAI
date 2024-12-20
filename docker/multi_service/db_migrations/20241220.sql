CREATE TABLE `tags` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`team_id` INT NOT NULL COMMENT 'Team ID',
	`mode` TINYINT(1) NOT NULL DEFAULT '1' COMMENT 'Tag mode 1: app 2: dataset',
	`name` VARCHAR(50) NOT NULL COMMENT 'Tag name' COLLATE 'utf8mb4_general_ci',
	`created_time` DATETIME NOT NULL COMMENT 'Tag  created time',
	`updated_time` DATETIME NULL DEFAULT NULL COMMENT 'Tag  updated time',
	`status` TINYINT(1) NULL DEFAULT '1' COMMENT 'Tag status 1: Normal 2: Disabled 3: Deleted',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `team_id` (`team_id`) USING BTREE,
	INDEX `mode` (`mode`) USING BTREE,
	INDEX `status` (`status`) USING BTREE
)
COMMENT='App Tag Data Table'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=5
;

CREATE TABLE `tag_bindings` (
	`id` INT NOT NULL AUTO_INCREMENT COMMENT 'Tag bindings ID',
	`tag_id` INT NOT NULL COMMENT 'Tag ID',
	`app_id` INT NOT NULL COMMENT 'App ID',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `tag_id` (`tag_id`) USING BTREE,
	INDEX `target_id` (`app_id`) USING BTREE
)
COMMENT='App And Tag Binding Data Table'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;

ALTER TABLE `app_runs`
	ADD COLUMN `ai_tool_type` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'AI tool type 0: Regular APP (not an AI tool) 1: Agent generator 2: Skill generator 3: Chat history summary' AFTER `type`;
ALTER TABLE `app_runs`
	ADD INDEX `ai_tool_type` (`ai_tool_type`);

CREATE TABLE `ai_tool_llm_records` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'AI tool LLM record ID',
	`app_run_id` INT(11) NOT NULL COMMENT 'App run ID',
	`llm_input` LONGTEXT NULL DEFAULT NULL COMMENT 'LLM input messages in LangChain format' COLLATE 'utf8mb4_bin',
	`message` TEXT NOT NULL COMMENT 'LLM output message string' COLLATE 'utf8mb4_general_ci',
	`prompt_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Prompt tokens',
	`completion_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Completion tokens',
	`total_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Total tokens',
	`created_time` DATETIME NOT NULL DEFAULT current_timestamp() COMMENT 'Record created time',
	`updated_time` DATETIME NULL DEFAULT NULL COMMENT 'Record updated time',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `app_run_id` (`app_run_id`) USING BTREE,
	CONSTRAINT `ai_tool_llm_records_chk_1` CHECK (json_valid(`llm_input`))
)
COMMENT='AI Tool LLM Record Data Table'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;