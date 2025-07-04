ALTER TABLE `chatroom_messages`
	CHANGE COLUMN `message` `message` MEDIUMTEXT NOT NULL COMMENT 'LLM output message string (or user input message)' COLLATE 'utf8mb4_general_ci' AFTER `llm_input`;
