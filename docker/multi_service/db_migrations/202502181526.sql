INSERT INTO `suppliers` (`id`, `name`, `mode`, `created_time`, `updated_time`, `status`)
VALUES (4, 'Doubao', '1', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `created_time`, `updated_time`, `status`)
VALUES (15, '4', 'Doubao-1.5-pro-256k', '1', '1', '256000', '12000', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `created_time`, `updated_time`, `status`)
VALUES (16, '4', 'Doubao-1.5-pro-32k', '1', '1', '32000', '12000', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `created_time`, `updated_time`, `status`)
VALUES (17, '4', 'Doubao-1.5-lite-32k', '1', '1', '32000', '12000', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `created_time`, `updated_time`, `status`)
VALUES (18, '4', 'Doubao-pro-256k', '1', '1', '256000', '4000', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `max_context_tokens`, `max_output_tokens`, `created_time`, `updated_time`, `status`)
VALUES (19, '4', 'Doubao-lite-128k', '1', '1', '128000', '4000', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `created_time`, `updated_time`, `status`)
VALUES (15, '1', '15', '{"model": "ep-20250213164639-kgtq2", "temperature": 0.7, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', '0', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `created_time`, `updated_time`, `status`)
VALUES (16, '1', '16', '{"model": "ep-20250213145156-lgdnr", "temperature": 0.7, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', '0', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `created_time`, `updated_time`, `status`)
VALUES (17, '1', '17', '{"model": "ep-20250213164550-m586m", "temperature": 0.7, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', '0', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `created_time`, `updated_time`, `status`)
VALUES (18, '1', '18', '{"model": "ep-20250213164639-kgtq2", "temperature": 0.7, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', '0', CURRENT_TIMESTAMP, NULL, '1');

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `created_time`, `updated_time`, `status`)
VALUES (19, '1', '19', '{"model": "ep-20250213164724-95xlf", "temperature": 0.7, "model_kwargs": {}, "organization": null, "openai_proxy": null, "timeout": null, "max_retries": 2, "streaming": false, "n": 1, "max_tokens": null, "tiktoken_model_name": null, "default_headers": null, "default_query": null, "http_client": null, "http_async_client": null, "stop_sequences": null}', '0', CURRENT_TIMESTAMP, NULL, '1');


ALTER TABLE `model_configurations`
	ADD COLUMN `sort_order` TINYINT(11) NOT NULL COMMENT 'Model Sort Order' AFTER `default_used`;

ALTER TABLE `model_configurations`
	CHANGE COLUMN `sort_order` `sort_order` TINYINT(11) NOT NULL DEFAULT '0' COMMENT 'Model Sort Order' AFTER `default_used`;

UPDATE model_configurations SET sort_order = 1 WHERE id = 1;
UPDATE model_configurations SET sort_order = 1 WHERE id = 2;
UPDATE model_configurations SET sort_order = 4 WHERE id = 3;
UPDATE model_configurations SET sort_order = 1 WHERE id = 4;
UPDATE model_configurations SET sort_order = 5 WHERE id = 5;
UPDATE model_configurations SET sort_order = 6 WHERE id = 6;
UPDATE model_configurations SET sort_order = 7 WHERE id = 7;
UPDATE model_configurations SET sort_order = 100 WHERE id = 8;
UPDATE model_configurations SET sort_order = 1 WHERE id = 9;
UPDATE model_configurations SET sort_order = 1 WHERE id = 10;
UPDATE model_configurations SET sort_order = 2 WHERE id = 11;
UPDATE model_configurations SET sort_order = 3 WHERE id = 12;
UPDATE model_configurations SET sort_order = 4 WHERE id = 13;
UPDATE model_configurations SET sort_order = 100 WHERE id = 14;
UPDATE model_configurations SET sort_order = 1 WHERE id = 15;
UPDATE model_configurations SET sort_order = 2 WHERE id = 16;
UPDATE model_configurations SET sort_order = 3 WHERE id = 17;
UPDATE model_configurations SET sort_order = 4 WHERE id = 18;
UPDATE model_configurations SET sort_order = 100 WHERE id = 19;

