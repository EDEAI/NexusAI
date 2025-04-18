-- Add o1-pro model to OpenAI
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `created_time`, `updated_time`, `status`) VALUES (25, '1', 'o1-pro', '1', '1', '200000', '100000', CURRENT_TIMESTAMP, NULL, '1');

-- Add model configuration for o1-pro
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (25, '1', '25', '{"n": 1, "stop": null, "model": "o1-pro", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', '0', 90, CURRENT_TIMESTAMP, NULL, '1');

-- Add support_image field to models table
ALTER TABLE `models` ADD `support_image` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Support image input 0: No 1: Yes' AFTER `max_output_tokens`;

-- Update existing models that support image input
UPDATE `models` SET `support_image` = 1 WHERE `id` IN (4, 5, 6, 10, 11, 12, 13, 14, 20, 23, 24, 25);

-- Add Doubao vision models
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (26, '4', 'Doubao-1.5-vision-pro-32k', '1', '1', '32000', '12288', '1', CURRENT_TIMESTAMP, NULL, '1');
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (27, '4', 'Doubao-vision-pro-32k', '1', '1', '32000', '4096', '1', CURRENT_TIMESTAMP, NULL, '1');

-- Add model configurations for Doubao vision models
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (26, '1', '26', '{"model": "doubao-1-5-vision-pro-32k-250115", "temperature": 1, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', '0', 40, CURRENT_TIMESTAMP, NULL, '1');
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (27, '1', '27', '{"model": "doubao-vision-pro-32k-241028", "temperature": 1, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', '0', 41, CURRENT_TIMESTAMP, NULL, '1');

-- Update sort_order for existing Doubao models
UPDATE `model_configurations` SET `sort_order` = 94 WHERE `id` = 15; -- Doubao-1.5-pro-256k
UPDATE `model_configurations` SET `sort_order` = 95 WHERE `id` = 26; -- Doubao-1.5-vision-pro-32k
UPDATE `model_configurations` SET `sort_order` = 96 WHERE `id` = 16; -- Doubao-1.5-pro-32k
UPDATE `model_configurations` SET `sort_order` = 97 WHERE `id` = 17; -- Doubao-1.5-lite-32k
UPDATE `model_configurations` SET `sort_order` = 98 WHERE `id` = 18; -- Doubao-pro-256k
UPDATE `model_configurations` SET `sort_order` = 99 WHERE `id` = 27; -- Doubao-vision-pro-32k
UPDATE `model_configurations` SET `sort_order` = 100 WHERE `id` = 19; -- Doubao-lite-128k
