-- Add OpenAI models: gpt-5-pro, gpt-5.1
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
VALUES
  (89, 1, 'gpt-5-pro', 1, 1, 400000, 272000, 1, CURRENT_TIMESTAMP, NULL, 1),
  (90, 1, 'gpt-5.1', 1, 1, 400000, 128000, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add Google model: gemini-3-pro-preview
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
VALUES
  (91, 5, 'gemini-3-pro-preview', 1, 1, 1114112, 65536, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for all teams - OpenAI gpt-5-pro (model_id=89)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`)
SELECT NULL, t.id, 89, '{"n": 1, "stop": null, "model": "gpt-5-pro", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}',
       0, 81, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Add model configurations for all teams - OpenAI gpt-5.1 (model_id=90)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`)
SELECT NULL, t.id, 90, '{"n": 1, "stop": null, "model": "gpt-5.1", "streaming": false, "max_tokens": null, "http_client": null, "max_retries": 2, "temperature": 1, "model_kwargs": {}, "openai_proxy": null, "default_query": null, "default_headers": null, "openai_api_base": null, "request_timeout": null, "http_async_client": null, "openai_organization": null, "tiktoken_model_name": null}',
       0, 80, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Add model configurations for all teams - Google gemini-3-pro-preview (model_id=91)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`)
SELECT NULL, t.id, 91, '{"model": "gemini-3-pro-preview", "credentials": null, "temperature": 1, "top_p": null, "top_k": null, "max_tokens": null, "n": 1, "max_retries": 2, "timeout": null, "transport": "rest"}',
       0, 95, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
