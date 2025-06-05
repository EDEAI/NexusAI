-- Create third_party_users table for third-party user login functionality
CREATE TABLE IF NOT EXISTS `third_party_users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Third-party User ID',
  `platform` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Third-party platform identifier',
  `openid` varchar(100) COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Third-party platform user openid',
  `nickname` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'User''s nickname',
  `avatar` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'User''s avatar',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'User created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'The user''s most recent updated time',
  `last_login_time` datetime DEFAULT NULL COMMENT 'The time the user last logged in',
  `last_login_ip` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'The IP address of the user''s last login',
  `language` varchar(10) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'en' COMMENT 'Current language',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'User status 1: Normal 2: Disabled 3: Deleted',
  PRIMARY KEY (`id`),
  UNIQUE KEY `platform_openid` (`platform`,`openid`),
  KEY `status` (`status`),
  KEY `platform` (`platform`),
  KEY `openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Third-party User Data Table'; 