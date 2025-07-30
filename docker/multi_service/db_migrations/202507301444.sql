-- Add Tongyi as a new model supplier
INSERT INTO `suppliers` (`id`, `name`, `mode`, `created_time`, `updated_time`, `status`) VALUES (6, 'Tongyi', 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add Tongyi supplier configuration (empty config initially)
INSERT INTO `supplier_configurations` (`id`, `team_id`, `supplier_id`, `config`, `created_time`, `updated_time`, `status`) VALUES (99, 1, 6, '{}', CURRENT_TIMESTAMP, NULL, 1);

-- Add Qwen models
-- Qwen3-Plus - 128K context, default model
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (50, 6, 'Qwen3-Plus', 1, 1, 131072, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-Turbo - 1M context
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (51, 6, 'Qwen3-Turbo', 1, 1, 1048576, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen2.5-Max - 128K context
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (52, 6, 'Qwen2.5-Max', 1, 1, 131072, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-Coder-Plus - 1M context
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (53, 6, 'Qwen3-Coder-Plus', 1, 1, 1048576, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-Coder-480B-A35B-Instruct - 256K context
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (54, 6, 'Qwen3-Coder-480B-A35B-Instruct', 1, 1, 262144, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-MT-Plus - 4K context
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (55, 6, 'Qwen3-MT-Plus', 1, 1, 4096, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-MT-Turbo - 4K context
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (56, 6, 'Qwen3-MT-Turbo', 1, 1, 4096, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-VL-Max - 128K context, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (57, 6, 'Qwen-VL-Max', 1, 1, 131072, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-VL-Plus - 128K context, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (58, 6, 'Qwen-VL-Plus', 1, 1, 131072, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-QVQ-Max - 128K context, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (59, 6, 'Qwen-QVQ-Max', 1, 1, 131072, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-QVQ-Plus - 128K context, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (60, 6, 'Qwen-QVQ-Plus', 1, 1, 131072, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-2.5-VL-72B - 128K context, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (61, 6, 'Qwen-2.5-VL-72B', 1, 1, 131072, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-2.5-VL-32B - 128K context, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (62, 6, 'Qwen-2.5-VL-32B', 1, 1, 131072, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-VL-OCR - 34K context, supports image
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (63, 6, 'Qwen-VL-OCR', 1, 1, 34816, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for all Qwen models
-- Qwen3-Plus configuration (default_used = 1, sort_order = 87)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (100, 1, 50, '{"model_name": "qwen-plus-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 1, 87, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-Turbo configuration (sort_order = 88)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (101, 1, 51, '{"model_name": "qwen-turbo-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 88, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen2.5-Max configuration (sort_order = 89)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (102, 1, 52, '{"model_name": "qwen-max-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 89, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-Coder-Plus configuration (sort_order = 90)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (103, 1, 53, '{"model_name": "qwen3-coder-plus", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 90, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-Coder-480B-A35B-Instruct configuration (sort_order = 91)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (104, 1, 54, '{"model_name": "qwen3-coder-480b-a35b-instruct", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 91, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-MT-Plus configuration (sort_order = 92)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (105, 1, 55, '{"model_name": "qwen-mt-plus", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 92, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen3-MT-Turbo configuration (sort_order = 93)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (106, 1, 56, '{"model_name": "qwen-mt-turbo", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 93, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-VL-Max configuration (sort_order = 94)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (107, 1, 57, '{"model_name": "qwen-vl-max-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 94, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-VL-Plus configuration (sort_order = 95)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (108, 1, 58, '{"model_name": "qwen-vl-plus-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 95, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-QVQ-Max configuration (sort_order = 96)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (109, 1, 59, '{"model_name": "qvq-max-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 96, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-QVQ-Plus configuration (sort_order = 97)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (110, 1, 60, '{"model_name": "qvq-plus-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 97, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-2.5-VL-72B configuration (sort_order = 98)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (111, 1, 61, '{"model_name": "qwen2.5-vl-72b-instruct", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 98, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-2.5-VL-32B configuration (sort_order = 99)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (112, 1, 62, '{"model_name": "qwen2.5-vl-32b-instruct", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 99, CURRENT_TIMESTAMP, NULL, 1);

-- Qwen-VL-OCR configuration (sort_order = 100)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) VALUES (113, 1, 63, '{"model_name": "qwen-vl-ocr-latest", "top_p": 0.8, "dashscope_api_key": null, "streaming": false, "max_retries": 10, "model_kwargs": {}}', 0, 100, CURRENT_TIMESTAMP, NULL, 1);