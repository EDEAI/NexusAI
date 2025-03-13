ALTER TABLE `app_runs`
	ADD COLUMN `agent_run_type` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Agent run type 0: Not an Agent 1: Agent chat 2: Run in a workflow 3: Chat in a Round Table 4: Guidance Execution of a Round Table' AFTER `type`,
	ADD INDEX `agent_run_type` (`agent_run_type`);
