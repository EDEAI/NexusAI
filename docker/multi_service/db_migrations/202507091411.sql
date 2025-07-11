ALTER TABLE `chatrooms`
	ADD COLUMN `chat_file_list` LONGTEXT NULL DEFAULT NULL COMMENT 'Chat File List' AFTER `initial_message_id`,
	ADD CONSTRAINT `chatrooms_chk_1` CHECK (json_valid(`chat_file_list`));

ALTER TABLE `mcp_tool_use_records`
	ADD COLUMN `files_to_upload` LONGTEXT NULL DEFAULT NULL COMMENT 'Files to upload' AFTER `args`,
	ADD CONSTRAINT `mcp_tool_use_records_chk_3` CHECK (json_valid(`files_to_upload`));
