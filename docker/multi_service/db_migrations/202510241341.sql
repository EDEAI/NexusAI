-- Add LLMs: Claude Sonnet 4.5, Claude Haiku 4.5
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (87, 3, 'Claude Sonnet 4.5', 1, 1, 200000, 64000, 1, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (88, 3, 'Claude Haiku 4.5', 1, 1, 200000, 64000, 1, CURRENT_TIMESTAMP, NULL, 1);


-- Add model configurations for all teams
-- Claude Sonnet 4.5 (sort_order = 90)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 87, '{"top_k": null, "top_p": null, "timeout": null, "streaming": false, "model_name": "claude-sonnet-4-5", "max_retries": 2, "temperature": null, "model_kwargs": {}, "default_headers": null, "anthropic_api_url": null, "max_tokens_to_sample": 32000}', 
       0, 90, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Claude Haiku 4.5 (sort_order = 91)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 88, '{"top_k": null, "top_p": null, "timeout": null, "streaming": false, "model_name": "claude-haiku-4-5", "max_retries": 2, "temperature": null, "model_kwargs": {}, "default_headers": null, "anthropic_api_url": null, "max_tokens_to_sample": 32000}', 
       0, 91, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;


-- Update LLM: Gemini 2.5 Flash Lite
UPDATE `models` 
SET `name` = 'gemini-2.5-flash-lite'
WHERE `id` = 47;

UPDATE `model_configurations` 
SET `config` = '{"n": 1, "model": "gemini-2.5-flash-lite", "top_k": null, "top_p": null, "timeout": null, "transport": "rest", "max_tokens": null, "credentials": null, "max_retries": 2, "temperature": 1}'
WHERE `model_id` = 47;
