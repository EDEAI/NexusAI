ALTER TABLE `rag_records`
	ADD COLUMN `agent_run_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Agent App run ID' AFTER `agent_id`,
	ADD COLUMN `workflow_run_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Workflow App run ID' AFTER `workflow_id`,
	ADD INDEX `agent_run_id` (`agent_run_id`),
	ADD INDEX `workflow_run_id` (`workflow_run_id`);

ALTER TABLE `app_runs`
	ADD COLUMN `selected_ability_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Agent ability ID selected by the user' AFTER `raw_user_prompt`,
	ADD COLUMN `auto_match_ability` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Is auto match ability enabled for the Agent? 0: No 1: Yes' AFTER `selected_ability_id`,
	ADD COLUMN `matched_ability_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Agent ability ID matched by AI' AFTER `auto_match_ability`;
