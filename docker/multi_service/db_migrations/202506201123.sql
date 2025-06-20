ALTER TABLE `chatrooms` ADD `last_chat_time` DATETIME NULL DEFAULT NULL COMMENT 'Last chat time' AFTER `updated_time`;

ALTER TABLE `chatrooms`
	ADD INDEX `last_chat_time` (`last_chat_time`);