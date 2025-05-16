-- Add new OpenAI text-to-image models: gpt-image-1, dall-e-3, dall-e-2
-- First adding entries to the models table
INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (37, 1, 'gpt-image-1', 6, 1, 0, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (38, 1, 'dall-e-3', 6, 1, 0, 0, 0, CURRENT_TIMESTAMP, NULL, 1);

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `support_image`, `created_time`, `updated_time`, `status`) 
VALUES (39, 1, 'dall-e-2', 6, 1, 0, 0, 1, CURRENT_TIMESTAMP, NULL, 1);

-- Now adding the corresponding model configurations with different defaults for each model
-- gpt-image-1 configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (37, 1, 37, '{"model":"gpt-image-1","background":"auto","moderation":"auto","n":null,"output_compression":100,"output_format":"png","quality":"auto","size":"auto","user":null}', 0, 98, CURRENT_TIMESTAMP, NULL, 1);

-- dall-e-3 configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (38, 1, 38, '{"model":"dall-e-3","n":null,"quality":"standard","response_format":"b64_json","size":"1024x1024","style":"vivid","user":null}', 1, 99, CURRENT_TIMESTAMP, NULL, 1);

-- dall-e-2 configuration
INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `sort_order`, `created_time`, `updated_time`, `status`) 
VALUES (39, 1, 39, '{"model":"dall-e-2","n":null,"response_format":"b64_json","size":"1024x1024","user":null}', 0, 100, CURRENT_TIMESTAMP, NULL, 1); 