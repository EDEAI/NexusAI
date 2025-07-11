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

CREATE TABLE `role_permission` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `role_id` INT UNSIGNED NOT NULL COMMENT 'Role id',
  `permission_id` INT UNSIGNED NOT NULL COMMENT 'Permission id',
  PRIMARY KEY (`id`),
  KEY `role_id` (`role_id`),
  KEY `permission_id` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Role-Permission relation table';

ALTER TABLE `users`
ADD COLUMN `role_id` INT UNSIGNED DEFAULT NULL COMMENT 'Bind role id' AFTER `role`,
ADD KEY `role_id` (`role_id`);

INSERT INTO `permissions` (`title_cn`, `title_en`, `status`) VALUES
('创建智能体', 'Create Agent', 1),
('创建工作流', 'Create Workflow', 1),
('创建技能', 'Create Skill', 1),
('创建圆桌', 'Create Roundtable', 1),
('创建知识库', 'Create Knowledge Base', 1);

INSERT INTO `roles` (`name`, `description`, `status`) VALUES
('智能体管理员', 'Agent administrator', 1),
('工作流管理员', 'Workflow administrator', 1),
('技能管理员', 'Skill administrator', 1),
('圆桌管理员', 'Roundtable administrator', 1),
('知识库管理员', 'Knowledge base administrator', 1);

INSERT INTO `role_permission` (`role_id`, `permission_id`) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);