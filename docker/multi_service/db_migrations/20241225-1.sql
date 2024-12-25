ALTER TABLE `ai_tool_llm_records`
	CHANGE COLUMN `llm_input` `inputs` LONGTEXT NULL DEFAULT NULL COMMENT 'Inputs' COLLATE 'utf8mb4_bin' AFTER `app_run_id`,
	DROP CONSTRAINT `ai_tool_llm_records_chk_1`,
	ADD CONSTRAINT `ai_tool_llm_records_chk_1` CHECK (json_valid(`inputs`));
ALTER TABLE `ai_tool_llm_records`
	CHANGE COLUMN `message` `outputs` LONGTEXT NULL DEFAULT NULL COMMENT 'Outputs' COLLATE 'utf8mb4_bin' AFTER `inputs`,
	ADD CONSTRAINT `ai_tool_llm_records_chk_2` CHECK (json_valid(`outputs`));
ALTER TABLE `ai_tool_llm_records`
	ADD COLUMN `correct_prompt` LONGTEXT NULL DEFAULT NULL COMMENT 'Prompt for correcting LLM output results' COLLATE 'utf8mb4_bin' AFTER `inputs`,
	ADD CONSTRAINT `ai_tool_llm_records_chk_3` CHECK (json_valid(`correct_prompt`));
ALTER TABLE `ai_tool_llm_records`
	ADD COLUMN `model_data` LONGTEXT NULL DEFAULT NULL COMMENT 'Data required for AI models' COLLATE 'utf8mb4_bin' AFTER `correct_prompt`,
	ADD CONSTRAINT `ai_tool_llm_records_chk_4` CHECK (json_valid(`model_data`));
ALTER TABLE `ai_tool_llm_records` ADD `correct_output` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Human correct output 0: No 1: Yes' AFTER `outputs`, ADD INDEX (`correct_output`);
ALTER TABLE `ai_tool_llm_records` ADD `status` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Execute status 0: Cannot execute 1: Can execute 2: Executing 3: Successfully executed 4: Failed to execute ' AFTER `correct_output`, ADD INDEX (`status`);
ALTER TABLE `ai_tool_llm_records` ADD `error` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Error message' AFTER `status`;
ALTER TABLE `ai_tool_llm_records` ADD `elapsed_time` DECIMAL(10,6) NOT NULL DEFAULT '0' COMMENT 'Elapsed time' AFTER `error`;
ALTER TABLE `ai_tool_llm_records` ADD `finished_time` DATETIME NULL DEFAULT NULL COMMENT 'Record finished time' AFTER `updated_time`;