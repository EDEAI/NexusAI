-- Add Txt2img models: Doubao-seedream-4.0, gemini-2.5-flash-image-preview
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (76, 4, 'Doubao-seedream-4.0', 6, 1, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (77, 5, 'gemini-2.5-flash-image-preview', 6, 1, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for all teams
-- Doubao-seedream-4.0 configuration (sort_order = 100)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 76, '{"model": "doubao-seedream-4.0-250828", "size": "2K", "response_format": "url", "watermark": false}', 
       0, 100, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- gemini-2.5-flash-image-preview configuration (sort_order = 100)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 77, '{"model": "gemini-2.5-flash-image-preview"}', 
       1, 100, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;


-- Add local embedding & reranker models
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (78, 2, 'bce-embedding-base_v1', 2, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (79, 2, 'bge-m3', 2, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (80, 2, 'Qwen3-Embedding-0.6B', 2, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (81, 2, 'Qwen3-Embedding-4B', 2, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (82, 2, 'Qwen3-Embedding-8B', 2, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (83, 2, 'bce-reranker-base_v1', 3, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (84, 2, 'Qwen3-Reranker-0.6B', 3, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (85, 2, 'Qwen3-Reranker-4B', 3, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`)
       VALUES (86, 2, 'Qwen3-Reranker-8B', 3, 2, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for all teams
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 78, '{"type": "SentenceTransformerEmbeddings"}', 
       0, 95, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 79, '{"type": "SentenceTransformerEmbeddings"}', 
       0, 96, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 80, '{"type": "SentenceTransformerEmbeddings"}', 
       0, 97, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 81, '{"type": "SentenceTransformerEmbeddings"}', 
       0, 98, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 82, '{"type": "SentenceTransformerEmbeddings"}', 
       0, 99, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;


INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 83, '{"type": "CrossEncoderReranker", "model_type": "HuggingFaceCrossEncoder"}', 
       0, 96, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 84, '{"type": "CrossEncoderReranker", "model_type": "Qwen3CrossEncoder"}', 
       0, 97, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 85, '{"type": "CrossEncoderReranker", "model_type": "Qwen3CrossEncoder"}', 
       0, 98, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 86, '{"type": "CrossEncoderReranker", "model_type": "Qwen3CrossEncoder"}', 
       0, 99, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
