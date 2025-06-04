ALTER TABLE `chatrooms`
	ADD COLUMN `chat_agent_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'ID of the Agent in Agent Chat mode' AFTER `app_id`,
	ADD INDEX `chat_agent_id` (`chat_agent_id`);
