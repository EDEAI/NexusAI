-- Add node_confirm_users field to scheduled_tasks table
ALTER TABLE `scheduled_tasks` ADD `node_confirm_users` JSON NULL COMMENT 'Confirmer of node output data' AFTER `input`;