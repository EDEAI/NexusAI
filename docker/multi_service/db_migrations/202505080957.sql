ALTER TABLE `app_runs`
	ADD COLUMN `chatroom_message_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Chatroom message ID' AFTER `chatroom_id`,
	ADD INDEX `chatroom_message_id` (`chatroom_message_id`);
ALTER TABLE `chatroom_messages`
	DROP COLUMN `agent_run_id`;
