ALTER TABLE `chatroom_messages`
	ADD COLUMN `ability_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'ID of the corresponding Agent ability of the message' AFTER `agent_id`,
	ADD INDEX `ability_id` (`ability_id`);
