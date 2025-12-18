CREATE TABLE `api_keys` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'API key ID',
  `app_id` int NOT NULL COMMENT 'The app ID this API key belongs to',
  `user_id` int NOT NULL COMMENT 'The user ID who created this API key',
  `key` varchar(28) NOT NULL COMMENT 'The API key value',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1: active, 0: deleted',
  `last_used_time` datetime DEFAULT NULL COMMENT 'Last time this API key was used',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'API key created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'API key updated time',
  PRIMARY KEY (`id`),
  KEY `app_id` (`app_id`),
  KEY `user_id` (`user_id`),
  KEY `key` (`key`),
  KEY `status` (`status`)
)
COMMENT='API Key Table'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;

ALTER TABLE `chatrooms` 
ADD COLUMN `api_key_id` int DEFAULT NULL COMMENT 'API key ID if the chatroom was created via API',
ADD KEY `api_key_id` (`api_key_id`);

ALTER TABLE `app_runs` 
ADD COLUMN `api_key_id` int DEFAULT NULL COMMENT 'API key ID if the run was triggered via API',
ADD KEY `api_key_id` (`api_key_id`);

ALTER TABLE `upload_files` 
ADD COLUMN `api_key_id` int DEFAULT NULL COMMENT 'API key ID if the file was uploaded via API',
ADD KEY `api_key_id` (`api_key_id`);
