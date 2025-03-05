ALTER TABLE `chatrooms` ADD COLUMN `is_temporary` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Whether it is a temporary session 0: No, 1: Yes' AFTER `app_id`;
ALTER TABLE `chatrooms` ADD INDEX(`is_temporary`);

ALTER TABLE `datasets` ADD COLUMN `temporary_chatroom_id` int NOT NULL DEFAULT '0' COMMENT 'ID of the temporary chatroom, 0 means no temporary chatroom' AFTER `app_id`;
ALTER TABLE `datasets` ADD INDEX(`temporary_chatroom_id`);