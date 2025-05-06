-- Add new OpenAI LLM models: o3, o4-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
-- First adding entries to the models table
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (30, 1, 'o3', 1, 1, 200000, 100000, 1, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (31, 1, 'o4-mini', 1, 1, 200000, 100000, 1, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (32, 1, 'gpt-4.1', 1, 1, 1047576, 32768, 1, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (33, 1, 'gpt-4.1-mini', 1, 1, 1047576, 32768, 1, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (34, 1, 'gpt-4.1-nano', 1, 1, 1047576, 32768, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Now adding the corresponding model configurations
-- Using sort orders to maintain the specified sequence (o3, o4-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (30, 1, 30, '{"n": 1, "stop": null, "model": "o3", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 0, 85, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (31, 1, 31, '{"n": 1, "stop": null, "model": "o4-mini", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 0, 86, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (32, 1, 32, '{"n": 1, "stop": null, "model": "gpt-4.1", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 0, 87, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (33, 1, 33, '{"n": 1, "stop": null, "model": "gpt-4.1-mini", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 0, 88, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (34, 1, 34, '{"n": 1, "stop": null, "model": "gpt-4.1-nano", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}', 0, 89, CURRENT_TIMESTAMP, NULL, 1);

-- Add new Doubao vision models: Doubao-1.5-vision-pro and Doubao-1.5-vision-lite
-- First adding entries to the models table
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (35, 4, 'Doubao-1.5-vision-pro', 1, 1, 128000, 16384, 1, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (36, 4, 'Doubao-1.5-vision-lite', 1, 1, 128000, 16384, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Now adding the corresponding model configurations
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (35, 1, 35, '{"model": "doubao-1.5-vision-pro-250328", "temperature": 1, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', 0, 93, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (36, 1, 36, '{"model": "doubao-1.5-vision-lite-250315", "temperature": 1, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', 0, 94, CURRENT_TIMESTAMP, NULL, 1); 