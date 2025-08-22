-- Remove position column from users table
ALTER TABLE `users`
	DROP COLUMN `position`;

-- Add position column to user_team_relations table and create index
ALTER TABLE `user_team_relations`
	ADD COLUMN `position` VARCHAR(100) NULL COMMENT 'User position in the team' AFTER `team_id`,
	ADD INDEX `idx_position` (`position`);