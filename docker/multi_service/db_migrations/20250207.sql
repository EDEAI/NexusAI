ALTER TABLE `agents`
	ADD COLUMN `initial_message_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'The initial message ID of the chat history' AFTER `allow_upload_file`;

ALTER TABLE `apps`
	ADD COLUMN `attrs_are_visible` TINYINT(1) NOT NULL DEFAULT '1' COMMENT 'Are attributes of this app visible? 0: No 1: Yes' AFTER `publish_status`,
	ADD INDEX `attrs_are_visible` (`attrs_are_visible`);

ALTER TABLE `app_runs`
	ADD COLUMN `model_data` LONGTEXT NULL DEFAULT NULL COMMENT 'Data required for AI models' COLLATE 'utf8mb4_bin' AFTER `raw_user_prompt`,
	DROP COLUMN `messages`,
	DROP CONSTRAINT `app_runs_chk_8`,
	ADD CONSTRAINT `app_runs_chk_8` CHECK (json_valid(`model_data`));

ALTER TABLE `chatroom_messages`
	ADD COLUMN `agent_run_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Agent App run ID (0 when the sender is a user)' AFTER `agent_id`,
	ADD COLUMN `model_data` LONGTEXT NULL DEFAULT NULL COMMENT 'Data required for AI models' COLLATE 'utf8mb4_bin' AFTER `message`,
	DROP COLUMN `updated_time`,
	ADD INDEX `agent_run_id` (`agent_run_id`),
	ADD CONSTRAINT `chatroom_messages_chk_2` CHECK (json_valid(`model_data`));

CREATE TABLE `agent_chat_messages` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Agent chat message ID',
	`user_id` INT(11) NOT NULL COMMENT 'User ID',
	`agent_id` INT(11) NOT NULL COMMENT 'Agent ID',
	`agent_run_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Agent App run ID (0 when the sender is a user)',
	`message` TEXT NOT NULL COMMENT 'Agent output message (or user input message)' COLLATE 'utf8mb4_general_ci',
	`prompt_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Prompt tokens',
	`completion_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Completion tokens',
	`total_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Total tokens',
	`created_time` DATETIME NOT NULL DEFAULT current_timestamp() COMMENT 'Message created time',
	PRIMARY KEY (`id`),
	INDEX `user_id` (`user_id`),
	INDEX `agent_id` (`agent_id`),
	INDEX `agent_run_id` (`agent_run_id`)
)
COMMENT='Agent Chat Message Data Table'
COLLATE='utf8mb4_general_ci'
;
