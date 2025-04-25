ALTER TABLE `documents`
	ADD COLUMN `text_split_config` LONGTEXT NULL COMMENT 'Text split configuration' AFTER `node_exec_id`,
	ADD CONSTRAINT `documents_chk_1` CHECK (json_valid(`text_split_config`));

UPDATE `nexus_ai`.`dataset_process_rules` SET `config`='{"type": "RecursiveCharacterTextSplitter", "chunk_size": 4000, "chunk_overlap": 200, "keep_separator": false, "strip_whitespace": true}' WHERE  `id`=1;
