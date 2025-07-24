-- Remove foreign key constraints first (if they exist)
-- Note: When tables have foreign key relationships, child tables should be dropped before parent tables

-- Drop role_permission table (as it depends on roles and permissions tables)
DROP TABLE IF EXISTS `role_permission`;

-- Drop roles table
DROP TABLE IF EXISTS `roles`;

-- Drop permissions table
DROP TABLE IF EXISTS `permissions`;

CREATE TABLE `permissions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `title_cn` VARCHAR(64) NOT NULL COMMENT 'Permission title in Chinese',
  `title_en` VARCHAR(64) NOT NULL COMMENT 'Permission title in English',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT 'Status: 1-normal, 2-disabled, 3-deleted',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NULL DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `title_cn` (`title_cn`),
  KEY `title_en` (`title_en`),
  KEY `status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Permissions table';

CREATE TABLE `roles` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `name` VARCHAR(64) NOT NULL COMMENT 'Role name',
  `description` VARCHAR(255) DEFAULT NULL COMMENT 'Role description',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT 'Status: 1-normal, 2-disabled, 3-deleted',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NULL DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Roles table';

ALTER TABLE `roles`
ADD COLUMN `team_id` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Team ID' AFTER `id`,
ADD KEY `team_id` (`team_id`);

ALTER TABLE `roles`
ADD COLUMN `built_in` TINYINT NOT NULL DEFAULT 0 COMMENT 'Built-in role: 0-custom, 1-built-in' AFTER `description`,
ADD INDEX `idx_built_in` (`built_in`);


CREATE TABLE `role_permission` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `role_id` INT UNSIGNED NOT NULL COMMENT 'Role id',
  `permission_id` INT UNSIGNED NOT NULL COMMENT 'Permission id',
  PRIMARY KEY (`id`),
  KEY `role_id` (`role_id`),
  KEY `permission_id` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Role-Permission relation table';

INSERT INTO `permissions` (`title_cn`, `title_en`, `status`) VALUES
('创建智能体', 'Create Agent', 1),
('创建工作流', 'Create Workflow', 1),
('创建技能', 'Create Skill', 1),
('创建圆桌', 'Create Roundtable', 1),
('创建知识库', 'Create Knowledge Base', 1);

INSERT INTO `roles` (`team_id`, `built_in`, `name`, `description`, `status`) VALUES
-- ('综合管理员', 'Comprehensive administrator', 1),
-- ('智能体管理员', 'Agent administrator', 1),
-- ('工作流管理员', 'Workflow administrator', 1),
-- ('技能管理员', 'Skill administrator', 1),
-- ('圆桌管理员', 'Roundtable administrator', 1),
-- ('知识库管理员', 'Knowledge base administrator', 1);
('0','1','comprehensive_administrator', '', 1),
('0','1','agent_administrator', '', 1),
('0','1','workflow_administrator', '', 1),
('0','1','skill_administrator', '', 1),
('0','1','roundtable_administrator', '', 1),
('0','1','knowledge_base_administrator', '', 1);

INSERT INTO `role_permission` (`role_id`, `permission_id`) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(2, 1),
(3, 2),
(4, 3),
(5, 4),
(6, 5);


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
  `role` TINYINT(1) NOT NULL DEFAULT 2 COMMENT 'Team role 1: Administrator 2: Ordinary Member',
  `role_id` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Bind role id',
  `inviter_id` INT NOT NULL DEFAULT 0 COMMENT 'Inviter ID',
  `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_team_id` (`team_id`),
  INDEX `idx_role` (`role`),
  INDEX `idx_role_id` (`role_id`),
  INDEX `idx_inviter_id` (`inviter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='User and Team relation table';

INSERT INTO user_team_relations (user_id, team_id, role, role_id, inviter_id, created_time)
SELECT id, team_id, 
       role, 
       CASE WHEN role != 1 THEN 1 ELSE role_id END AS role_id, 
       IFNULL(inviter_id, 0) AS inviter_id, 
       NOW()
FROM users
WHERE team_id IS NOT NULL;

UPDATE users
SET role_id = 1
WHERE role != 1;


-- INSERT INTO user_team_relations (user_id, team_id, role, role_id, inviter_id, created_time)
-- SELECT id, team_id, role, role_id, inviter_id, NOW()
-- FROM users
-- WHERE team_id IS NOT NULL;