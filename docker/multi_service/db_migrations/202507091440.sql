-- Add Google as a new model supplier
INSERT INTO `suppliers` (`id`, `name`, `mode`, `created_time`, `updated_time`, `status`) VALUES (5, 'Google', 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add Google supplier configuration (empty config initially)
UPDATE `supplier_configurations` SET `id` = '4' WHERE `supplier_configurations`.`id` = 24;
INSERT INTO `supplier_configurations` (`id`, `team_id`, `supplier_id`, `config`, `created_time`, `updated_time`, `status`) VALUES (5, 1, 5, '{}', CURRENT_TIMESTAMP, NULL, 1);

-- Add Google Gemini models
-- gemini-2.5-pro - Most powerful thinking model (1M input + 64K output = ~1.1M total)
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (45, 5, 'gemini-2.5-pro', 1, 1, 1114112, 65536, 1, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.5-flash - Fast and balanced performance (1M input + 64K output = ~1.1M total)
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (46, 5, 'gemini-2.5-flash', 1, 1, 1114112, 65536, 1, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.5-flash-lite-preview-06-17 - Lightweight version (1M input + 8K output = ~1M total)
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (47, 5, 'gemini-2.5-flash-lite-preview-06-17', 1, 1, 1064000, 64000, 1, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.0-flash - Powerful workhorse model (1M input + 8K output = ~1M total)
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (48, 5, 'gemini-2.0-flash', 1, 1, 1056768, 8192, 1, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.0-flash-lite - Fast and efficient (1M input + 8K output = ~1M total)
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (49, 5, 'gemini-2.0-flash-lite', 1, 1, 1056768, 8192, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for Google Gemini models
-- gemini-2.5-pro configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (45, 1, 45, '{"model": "gemini-2.5-pro", "credentials": null, "temperature": 1, "top_p": null, "top_k": null, "max_tokens": null, "n": 1, "max_retries": 2, "timeout": null, "transport": "rest"}', 0, 96, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.5-flash configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (46, 1, 46, '{"model": "gemini-2.5-flash", "credentials": null, "temperature": 1, "top_p": null, "top_k": null, "max_tokens": null, "n": 1, "max_retries": 2, "timeout": null, "transport": "rest"}', 0, 97, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.5-flash-lite-preview-06-17 configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (47, 1, 47, '{"model": "gemini-2.5-flash-lite-preview-06-17", "credentials": null, "temperature": 1, "top_p": null, "top_k": null, "max_tokens": null, "n": 1, "max_retries": 2, "timeout": null, "transport": "rest"}', 0, 98, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.0-flash configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (48, 1, 48, '{"model": "gemini-2.0-flash", "credentials": null, "temperature": 1, "top_p": null, "top_k": null, "max_tokens": null, "n": 1, "max_retries": 2, "timeout": null, "transport": "rest"}', 0, 99, CURRENT_TIMESTAMP, NULL, 1);

-- gemini-2.0-flash-lite configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (49, 1, 49, '{"model": "gemini-2.0-flash-lite", "credentials": null, "temperature": 1, "top_p": null, "top_k": null, "max_tokens": null, "n": 1, "max_retries": 2, "timeout": null, "transport": "rest"}', 0, 100, CURRENT_TIMESTAMP, NULL, 1); 