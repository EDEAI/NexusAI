-- Add DeepSeek as a new model supplier
INSERT INTO `suppliers` (`id`, `name`, `mode`, `created_time`, `updated_time`, `status`) VALUES (7, 'DeepSeek', 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add DeepSeek models
-- deepseek-chat - 64K context, 8192 max output tokens, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (64, 7, 'deepseek-chat', 1, 1, 64000, 8192, 0, CURRENT_TIMESTAMP, NULL, 1);

-- deepseek-reasoner - 64K context, 0 max output tokens, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (65, 7, 'deepseek-reasoner', 1, 1, 64000, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for all teams
-- deepseek-chat configuration (sort_order = 99)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 64, '{"model": "deepseek-chat", "base_url": "https://api.deepseek.com", "streaming": false, "max_retries": 2, "temperature": 1, "model_kwargs": {}}', 
       0, 99, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- deepseek-reasoner configuration (sort_order = 100)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 65, '{"model": "deepseek-reasoner", "base_url": "https://api.deepseek.com", "streaming": false, "max_retries": 2, "temperature": 1, "model_kwargs": {}}', 
       0, 100, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Add additional Doubao models
-- Doubao-Seed-1.6 - 256K context, 32K max output tokens, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (66, 4, 'Doubao-Seed-1.6', 1, 1, 256000, 32768, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Doubao-Seed-1.6-flash - 256K context, 16K max output tokens, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (67, 4, 'Doubao-Seed-1.6-flash', 1, 1, 256000, 16384, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add Doubao model configurations for all teams
-- Doubao-Seed-1.6 configuration (sort_order = 101)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 66, '{"model": "doubao-seed-1-6-250615", "temperature": 1, "model_kwargs": {}, "max_retries": 2, "streaming": false}', 
       0, 90, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Doubao-Seed-1.6-flash configuration (sort_order = 102)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 67, '{"model": "doubao-seed-1-6-flash-250715", "temperature": 1, "model_kwargs": {}, "max_retries": 2, "streaming": false}', 
       0, 91, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Update sort_order for existing models
-- Update model_id = 35 sort_order to 92
UPDATE `model_configurations` SET `sort_order` = 92 WHERE `model_id` = 35;

-- Update model_id = 36 sort_order to 93
UPDATE `model_configurations` SET `sort_order` = 93 WHERE `model_id` = 36;

-- Change team type=2 name to "Public Workspace"
UPDATE `teams` SET `name` = 'Public Workspace' WHERE `type` = 2;

-- Update type field comment to describe team types
-- 1: Regular team, 2: Public Workspace
ALTER TABLE `teams` MODIFY COLUMN `type` int NOT NULL DEFAULT 1 COMMENT '1: Regular team, 2: Public Workspace';