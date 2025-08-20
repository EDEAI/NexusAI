-- Add SiliconFlow as a new model supplier
INSERT INTO `suppliers` (`id`, `name`, `mode`, `created_time`, `updated_time`, `status`) VALUES (8, 'SiliconFlow', 1, CURRENT_TIMESTAMP, NULL, 1);

-- Add SiliconFlow models: Qwen3-Reranker-8B, Qwen3-Reranker-4B, Qwen3-Reranker-0.6B, bge-reranker-v2-m3
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (72, 8, 'Qwen3-Reranker-8B', 3, 1, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (73, 8, 'Qwen3-Reranker-4B', 3, 1, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (74, 8, 'Qwen3-Reranker-0.6B', 3, 1, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) VALUES (75, 8, 'bge-reranker-v2-m3', 3, 1, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

-- Add model configurations for all teams
-- Qwen3-Reranker-8B configuration (default, sort_order = 97)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 72, '{"type": "SiliconFlowReranker", "model": "Qwen/Qwen3-Reranker-8B", "top_n": 3}', 
       1, 97, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Qwen3-Reranker-4B configuration (sort_order = 98)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 73, '{"type": "SiliconFlowReranker", "model": "Qwen/Qwen3-Reranker-4B", "top_n": 3}', 
       0, 98, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- Qwen3-Reranker-0.6B configuration (sort_order = 99)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 74, '{"type": "SiliconFlowReranker", "model": "Qwen/Qwen3-Reranker-0.6B", "top_n": 3}', 
       0, 99, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;

-- bge-reranker-v2-m3 configuration (sort_order = 100)
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
SELECT NULL, t.id, 75, '{"type": "SiliconFlowReranker", "model": "BAAI/bge-reranker-v2-m3", "top_n": 3}', 
       0, 100, CURRENT_TIMESTAMP, NULL, 1
FROM teams t;
