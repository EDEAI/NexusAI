UPDATE `models` SET `name` = 'Claude Sonnet 3.5' WHERE `models`.`id` = 10;
UPDATE `models` SET `name` = 'Claude Haiku 3.5' WHERE `models`.`id` = 11;
UPDATE `models` SET `name` = 'Claude Opus 3' WHERE `models`.`id` = 12;
UPDATE `models` SET `name` = 'Claude Sonnet 3' WHERE `models`.`id` = 13;
UPDATE `models` SET `name` = 'Claude Haiku 3' WHERE `models`.`id` = 14;
UPDATE `models` SET `name` = 'Claude Sonnet 3.7' WHERE `models`.`id` = 23;
UPDATE `models` SET `name` = 'Claude Opus 4' WHERE `models`.`id` = 40;
UPDATE `models` SET `name` = 'Claude Sonnet 4' WHERE `models`.`id` = 41;

-- Add Anthropic model: Claude Opus 4.1
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (68, 3, 'Claude Opus 4.1', 1, 1, 200000, 32000, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add OpenAI models: gpt-5 series
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (69, 1, 'gpt-5', 1, 1, 400000, 128000, 1, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (70, 1, 'gpt-5-mini', 1, 1, 400000, 128000, 1, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (71, 1, 'gpt-5-nano', 1, 1, 400000, 128000, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for all teams - Anthropic Claude Opus 4.1 (model_id=68)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 68, '{"model_name": "claude-opus-4-1-20250805", "max_tokens_to_sample": 32000, "temperature": null, "top_k": null, "top_p": null, "timeout": null, "max_retries": 2, "anthropic_api_url": null, "default_headers": null, "model_kwargs": {}, "streaming": false}', 
       0, 92, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Add model configurations for all teams - OpenAI gpt-5 (model_id=69)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 69, '{"n": 1, "stop": null, "model": "gpt-5", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 
       0, 82, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Add model configurations for all teams - OpenAI gpt-5-mini (model_id=70)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 70, '{"n": 1, "stop": null, "model": "gpt-5-mini", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 
       0, 83, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Add model configurations for all teams - OpenAI gpt-5-nano (model_id=71)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 71, '{"n": 1, "stop": null, "model": "gpt-5-nano", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 
       0, 84, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;