ALTER TABLE `ai_tool_llm_records`
	CHANGE COLUMN `ai_tool_type` `ai_tool_type` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'AI tool type 1: Agent generator 2: Skill generator 3: Round Table meeting summary generator 4: Round Table app target data generator 5: See the batch agent example' AFTER `app_run_id`;
