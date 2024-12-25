ALTER TABLE `tags`
	ADD COLUMN `user_id` INT(11) NOT NULL COMMENT 'User ID' AFTER `team_id`;