-- Add platform and openid fields to users table for third-party user login functionality
ALTER TABLE `users` 
ADD COLUMN `platform` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Third-party platform identifier' AFTER `language`,
ADD COLUMN `openid` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Third-party platform user openid' AFTER `platform`;

-- Add individual indexes for platform and openid fields
ALTER TABLE `users` 
ADD INDEX `idx_platform` (`platform`),
ADD INDEX `idx_openid` (`openid`); 