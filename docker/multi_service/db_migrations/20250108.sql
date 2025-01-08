CREATE TABLE `chatroom_driven_records` (
  `id` int NOT NULL COMMENT 'Record ID',
  `data_source_run_id` int NOT NULL COMMENT 'Data source run ID',
  `data_driven_run_id` int NOT NULL DEFAULT '0' COMMENT 'Data driven run ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Chatroom Data Driven Record Data Table';


ALTER TABLE `chatroom_driven_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `data_source_run_id` (`data_source_run_id`),
  ADD KEY `data_driven_run_id` (`data_driven_run_id`);


ALTER TABLE `chatroom_driven_records`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Record ID';