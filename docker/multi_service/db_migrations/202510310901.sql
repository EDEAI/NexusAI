-- ----------------------------
-- Create tenants table
-- ----------------------------
DROP TABLE IF EXISTS `tenants`;
CREATE TABLE `tenants` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Tenant ID',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Display name',
  `legal_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Legal name',
  `country` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Company code',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT 'Notes',
  `config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT 'Configuration',
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Status: 0=Inactive, 1=Active, 2=Suspended, 3=Stopped, 4=Disabled, 5=Deleted',
  `created_time` datetime NOT NULL DEFAULT current_timestamp COMMENT 'Created time',
  `updated_time` datetime NULL DEFAULT NULL COMMENT 'Updated time',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `status`(`status` ASC) USING BTREE,
  INDEX `name`(`name` ASC) USING BTREE,
  CONSTRAINT `tenants_chk_1` CHECK (json_valid(`config`))
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'Tenants table' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Add tenant_id to users table
-- ----------------------------
ALTER TABLE `users` ADD COLUMN `tenant_id` int NOT NULL DEFAULT 0 COMMENT 'Associated tenant ID, 0 for regular users' AFTER `role_id`;
ALTER TABLE `users` ADD INDEX `tenant_id`(`tenant_id` ASC) USING BTREE;

-- ----------------------------
-- Add tenant_id to teams table
-- ----------------------------
ALTER TABLE `teams` ADD COLUMN `tenant_id` int NOT NULL DEFAULT 0 COMMENT 'Associated tenant ID' AFTER `name`;
ALTER TABLE `teams` ADD INDEX `tenant_id`(`tenant_id` ASC) USING BTREE;