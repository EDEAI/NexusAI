ALTER TABLE `apps`
ADD COLUMN `avatar` VARCHAR(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'App avatar image URL' AFTER `description`; 