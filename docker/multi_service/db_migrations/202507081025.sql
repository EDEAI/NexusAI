ALTER TABLE `app_runs`
	CHANGE COLUMN `name` `name` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Run name' COLLATE 'utf8mb4_general_ci' AFTER `agent_run_type`;
