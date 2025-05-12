CREATE TABLE IF NOT EXISTS `agent_callable_items` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `agent_id` int NOT NULL COMMENT 'Agent ID',
  `app_id` int NOT NULL COMMENT 'App ID (Skill or Workflow)',
  `item_type` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Item type 1: Skill 2: Workflow',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Updated time',
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  KEY `app_id` (`app_id`),
  KEY `item_type` (`item_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Agent Callable Items Data Table';

CREATE TABLE IF NOT EXISTS `mcp_servers` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `server_id` varchar(100) NOT NULL COMMENT 'MCP server unique identifier',
  `name` varchar(100) NOT NULL COMMENT 'MCP server name',
  `description` text COMMENT 'MCP server description',
  `doc_url` varchar(255) COMMENT 'Documentation URL',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Status 1: Normal 2: Disabled 3: Deleted',
  PRIMARY KEY (`id`),
  UNIQUE KEY `server_id` (`server_id`),
  KEY `status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='MCP Servers Data Table';