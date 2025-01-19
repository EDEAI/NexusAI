ALTER TABLE `apps`
	CHANGE COLUMN `description` `description` TEXT NULL DEFAULT NULL COMMENT 'App description' COLLATE 'utf8mb4_general_ci' AFTER `name`;