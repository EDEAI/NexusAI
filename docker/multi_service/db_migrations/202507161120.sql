-- 1. Alter table structure, add type field
ALTER TABLE `teams`
ADD COLUMN `type` int NOT NULL DEFAULT 1 COMMENT 'Team type: 1 Default team, 2 Personal workspace' AFTER `status`;

-- 2. Insert a new personal workspace record
INSERT INTO `teams` (`name`, `type`, `created_time`, `status`)
VALUES ('个人工作区', 2, NOW(), 1);

CREATE TABLE `user_team_relations` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `user_id` INT NOT NULL COMMENT 'User ID',
  `team_id` INT NOT NULL COMMENT 'Team ID',
  `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_team_id` (`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='User and Team relation table';

INSERT INTO user_team_relations (user_id, team_id, created_time)
SELECT id, team_id, NOW()
FROM users
WHERE team_id IS NOT NULL;