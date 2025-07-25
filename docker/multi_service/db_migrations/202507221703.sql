ALTER TABLE `tool_authorizations`
	ADD COLUMN `tool_category` VARCHAR(50) NOT NULL COMMENT 'Tool Classification\n' AFTER `user_id`;