ALTER TABLE `chatroom_driven_records`
	ADD COLUMN `chatroom_id` INT(11) NOT NULL COMMENT 'Chatroom ID' AFTER `data_driven_run_id`;
