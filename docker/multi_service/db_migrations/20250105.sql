ALTER TABLE `ai_tool_llm_records`
	ADD COLUMN `loop_id` BIGINT NOT NULL DEFAULT '0' COMMENT 'Loop ID' AFTER `run_type`;

ALTER TABLE `ai_tool_llm_records`
	ADD INDEX `loop_id` (`loop_id`);