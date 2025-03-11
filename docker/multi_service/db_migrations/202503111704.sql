ALTER TABLE `chatroom_messages`
	ADD COLUMN `message_type` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Message type 0: Normal message 1: Speaker Selector message 2: Title Generator message' COLLATE 'utf8mb4_general_ci' AFTER `message`,
	ADD INDEX `message_type` (`message_type`);

UPDATE `chatroom_messages`
	SET `message_type` = 1
	WHERE `user_id` = 0 AND `agent_id` = 0;
