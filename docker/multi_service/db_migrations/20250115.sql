ALTER TABLE `app_runs`
	ADD COLUMN `raw_user_prompt` TEXT NULL DEFAULT NULL COMMENT 'LLM raw user prompt' COLLATE 'utf8mb4_general_ci' AFTER `inputs`,
	ADD COLUMN `messages` LONGTEXT NULL DEFAULT NULL COMMENT 'Final LLM messages' COLLATE 'utf8mb4_bin' AFTER `raw_user_prompt`,
	ADD CONSTRAINT `app_runs_chk_8` CHECK (json_valid(`messages`));