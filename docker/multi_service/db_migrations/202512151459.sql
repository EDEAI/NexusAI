ALTER TABLE `chatrooms`
	ADD COLUMN `base_chatroom_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'ID of the chatroom which the temporary session is based on' AFTER `chat_agent_id`,
	ADD INDEX `base_chatroom_id` (`base_chatroom_id`);

ALTER TABLE `apps`
	DROP INDEX `api_token`,
	ADD INDEX `api_token` (`api_token`) USING BTREE;
