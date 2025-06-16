-- Add new Anthropic Claude 4 models: claude-opus-4-20250514, claude-sonnet-4-20250514
-- First adding entries to the models table
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (40, 3, 'claude-opus-4-20250514', 1, 1, 200000, 32000, 1, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (41, 3, 'claude-sonnet-4-20250514', 1, 1, 200000, 64000, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Now adding the corresponding model configurations
-- claude-opus-4-20250514 configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (40, 1, 40, '{"model_name": "claude-opus-4-20250514","max_tokens_to_sample": 32000,"temperature": null,"top_k": null,"top_p": null,"timeout": null,"max_retries": 2,"anthropic_api_url": null,"default_headers": null,"model_kwargs": {},"streaming": false}', 0, 93, CURRENT_TIMESTAMP, NULL, 1);

-- claude-sonnet-4-20250514 configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (41, 1, 41, '{"model_name": "claude-sonnet-4-20250514","max_tokens_to_sample": 64000,"temperature": null,"top_k": null,"top_p": null,"timeout": null,"max_retries": 2,"anthropic_api_url": null,"default_headers": null,"model_kwargs": {},"streaming": false}', 0, 94, CURRENT_TIMESTAMP, NULL, 1);

-- Update Claude 3.7 Sonnet configuration to increase max_tokens_to_sample from 8192 to 64000
UPDATE `model_configurations` SET `config` = '{"model_name": "claude-3-7-sonnet-latest","max_tokens_to_sample": 64000,"temperature": null,"top_k": null,"top_p": null,"timeout": null,"max_retries": 2,"anthropic_api_url": null,"default_headers": null,"model_kwargs": {},"streaming": false}' WHERE `id` = 23; 

-- Update models status to 2
UPDATE `models` SET `status` = '2' WHERE `models`.`id` = 37;
UPDATE `models` SET `status` = '2' WHERE `models`.`id` = 38;
UPDATE `models` SET `status` = '2' WHERE `models`.`id` = 39;