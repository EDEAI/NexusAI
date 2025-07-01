ALTER TABLE `apps`
	CHANGE COLUMN `name` `name` VARCHAR(255) NOT NULL COMMENT 'App name' COLLATE 'utf8mb4_general_ci' AFTER `user_id`;
