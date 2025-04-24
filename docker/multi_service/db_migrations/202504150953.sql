ALTER TABLE `agent_chat_messages`
	ADD COLUMN `file_list` LONGTEXT NULL DEFAULT NULL COMMENT 'File list' COLLATE 'utf8mb4_bin' AFTER `message`,
	ADD COLUMN `file_content_list` LONGTEXT NULL DEFAULT NULL COMMENT 'Conent of each file in the file list' COLLATE 'utf8mb4_bin' AFTER `file_list`,
	ADD CONSTRAINT `agent_chat_messages_chk_1` CHECK (json_valid(`file_list`)),
	ADD CONSTRAINT `agent_chat_messages_chk_2` CHECK (json_valid(`file_content_list`));

ALTER TABLE `chatroom_messages`
	ADD COLUMN `file_list` LONGTEXT NULL DEFAULT NULL COMMENT 'File list' COLLATE 'utf8mb4_bin' AFTER `message`,
	ADD COLUMN `file_content_list` LONGTEXT NULL DEFAULT NULL COMMENT 'Conent of each file in the file list' COLLATE 'utf8mb4_bin' AFTER `file_list`,
	ADD CONSTRAINT `chatroom_messages_chk_3` CHECK (json_valid(`file_list`)),
	ADD CONSTRAINT `chatroom_messages_chk_4` CHECK (json_valid(`file_content_list`));
