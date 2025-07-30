-- Add OpenAI speech recognition models

-- Insert GPT-4o-Transcribe model
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (42, 1, 'gpt-4o-transcribe', 4, 1, 16000, 2000, 0, NOW(), NOW(), 1);

-- Insert GPT-4o-Mini-Transcribe model
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (43, 1, 'gpt-4o-mini-transcribe', 4, 1, 16000, 2000, 0, NOW(), NOW(), 1);

-- Insert Whisper-1 model
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (44, 1, 'whisper-1', 4, 1, 0, 0, 0, NOW(), NOW(), 1);

-- Insert model configuration for GPT-4o-Transcribe
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (42, 1, 42, '{"model": "gpt-4o-transcribe", "stream": false, "include": null, "language": null, "prompt": null, "response_format": "json", "temperature": 0, "timestamp_granularities": ["segment"]}', 1, 98, NOW(), NOW(), 1); 

-- Insert model configuration for GPT-4o-Mini-Transcribe
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (43, 1, 43, '{"model": "gpt-4o-mini-transcribe", "stream": false, "include": null, "language": null, "prompt": null, "response_format": "json", "temperature": 0, "timestamp_granularities": ["segment"]}', 0, 99, NOW(), NOW(), 1); 

-- Insert model configuration for Whisper-1
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (44, 1, 44, '{"model": "whisper-1", "stream": false, "include": null, "language": null, "prompt": null, "response_format": "json", "temperature": 0, "timestamp_granularities": ["segment"]}', 0, 100, NOW(), NOW(), 1); 