CREATE TABLE `non_llm_records` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Record ID',
	`user_id` INT(11) NOT NULL COMMENT 'User ID',
	`team_id` INT(11) NOT NULL COMMENT 'Team ID',
	`chatroom_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Chatroom ID',
	`model_config_id` INT(11) NOT NULL COMMENT 'Model config ID',
	`model_type` TINYINT(1) NOT NULL COMMENT 'Model type 1: text-generation 2: embeddings 3: reranking 4: speech2text 5: tts 6: text2img 7: moderation',
	`input_file_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'Audio file ID',
	`output_text` TEXT NULL COMMENT 'Output text',
	`status` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Execute status 0: Cannot execute 1: Can execute 2: Executing 3: Successfully executed 4: Failed to execute ',
	`error` TEXT NULL DEFAULT NULL COMMENT 'Error message' COLLATE 'utf8mb4_general_ci',
	`elapsed_time` DECIMAL(10,6) NOT NULL DEFAULT '0.000000' COMMENT 'Elapsed time',
	`input_audio_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Input audio tokens',
	`prompt_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Prompt tokens',
	`completion_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Completion tokens',
	`total_tokens` INT(11) NOT NULL DEFAULT '0' COMMENT 'Total tokens',
	`created_time` DATETIME NOT NULL DEFAULT current_timestamp() COMMENT 'Record created time',
	PRIMARY KEY (`id`),
	INDEX `user_id` (`user_id`),
	INDEX `team_id` (`team_id`),
	INDEX `chatroom_id` (`chatroom_id`),
	INDEX `model_config_id` (`model_config_id`),
	INDEX `model_type` (`model_type`),
	INDEX `status` (`status`)
)
COMMENT='Non-LLM Record Data Table'
COLLATE='utf8mb4_general_ci'
;
