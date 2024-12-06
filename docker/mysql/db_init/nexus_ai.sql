SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `nexus_ai` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `nexus_ai`;

CREATE TABLE `agents` (
  `id` int NOT NULL COMMENT 'Agent ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `app_id` int NOT NULL COMMENT 'App ID',
  `obligations` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Agent obligations',
  `input_variables` json DEFAULT NULL COMMENT 'Input variables',
  `auto_match_ability` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Whether to automatically match abilities 0: No 1: Yes',
  `default_output_format` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Default output format 1: text 2: json 3: code',
  `model_config_id` int NOT NULL DEFAULT '0' COMMENT 'Model configuration ID',
  `allow_upload_file` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Is it allowed to upload files? 0: No 1: Yes',
  `publish_status` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Agent publish status 0: Draft 1: Published',
  `published_time` datetime DEFAULT NULL COMMENT 'Agent published time',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Agent created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Agent updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Agent status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Agent Data Table';

CREATE TABLE `agent_abilities` (
  `id` int NOT NULL COMMENT 'Ability ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `agent_id` int NOT NULL COMMENT 'Agent ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Ability name',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Ability content',
  `output_format` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Output format 0: defalut 1: text 2: json 3: code',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Ability created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Ability updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Ability status 1: Normal 2: Disabled 3: Deleted	'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Agent Ability Data Table';

CREATE TABLE `agent_dataset_relation` (
  `id` int NOT NULL COMMENT 'Agent dataset relation ID',
  `agent_id` int NOT NULL COMMENT 'Agent ID',
  `dataset_id` int NOT NULL COMMENT 'Dataset ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Agent Dataset Relation Data Table';

CREATE TABLE `apps` (
  `id` int NOT NULL COMMENT 'App ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL DEFAULT '0' COMMENT 'User ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'App name',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'App description',
  `icon` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'App icon',
  `icon_background` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'App icon background',
  `mode` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'App mode 1: agent 2: workflow 3: dataset 4: custom tool 5: chatroom',
  `enable_api` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Whether to enable API 0: No 1: Yes',
  `api_token` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'API Token',
  `is_public` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Is it open to team members? 0: No 1: Yes',
  `publish_status` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Publish status 0: Draft 1: Published',
  `execution_times` int NOT NULL DEFAULT '0' COMMENT 'App execution times',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'App created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'App updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'App status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='App Data Table';

INSERT INTO `apps` (`id`, `team_id`, `user_id`, `name`, `description`, `icon`, `icon_background`, `mode`, `enable_api`, `api_token`, `is_public`, `publish_status`, `execution_times`, `created_time`, `updated_time`, `status`) VALUES
(1, 1, 1, 'File writing skill', 'This is a file writing skill', '1', '', 4, 0, NULL, 1, 1, 0, '2024-12-03 08:10:50', '2024-12-03 08:16:30', 1),
(2, 1, 1, 'MySQL data skill', 'This is a MySQL database data processing skill', '1', '', 4, 0, NULL, 1, 1, 0, '2024-12-03 17:04:35', '2024-12-03 18:16:56', 1);

CREATE TABLE `app_node_executions` (
  `id` int NOT NULL COMMENT 'Node execution ID',
  `workflow_id` int NOT NULL DEFAULT '0' COMMENT 'Workflow ID',
  `chatroom_id` int NOT NULL DEFAULT '0' COMMENT 'Chatroom ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `app_run_id` int NOT NULL DEFAULT '0' COMMENT 'App run ID',
  `type` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Trigger type 1: Debug 2: Run application 3: API',
  `level` int NOT NULL DEFAULT '0' COMMENT 'The current level of edge',
  `child_level` int NOT NULL DEFAULT '0' COMMENT 'Child node level',
  `edge_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Edge ID',
  `pre_node_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Predecessor node ID or chat agent ID',
  `node_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Node ID or chat agent ID',
  `node_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Node Type',
  `node_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Node name or chat agent name',
  `node_graph` json DEFAULT NULL COMMENT 'Node graphical data',
  `correct_output` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Human correct output 0: No 1: Yes',
  `inputs` json DEFAULT NULL COMMENT 'Inputs',
  `correct_prompt` json DEFAULT NULL COMMENT 'Prompt for correcting LLM output results',
  `model_data` json DEFAULT NULL COMMENT 'Data required for AI models',
  `task_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Task ID to be executed',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Execute status 0: Cannot execute 1: Can execute 2: Executing 3: Successfully executed 4: Failed to execute',
  `error` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Error message',
  `condition_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Condition id of the logical branch or Task id',
  `outputs` json DEFAULT NULL COMMENT 'Outputs',
  `output_type` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Output type 0: no output 1: variables 2: text 3: database 4: code 5: document',
  `need_human_confirm` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Need human confirm 0: No 1: Yes',
  `elapsed_time` decimal(10,6) NOT NULL DEFAULT '0.000000' COMMENT 'Elapsed time',
  `prompt_tokens` int NOT NULL DEFAULT '0' COMMENT 'Prompt tokens',
  `completion_tokens` int NOT NULL DEFAULT '0' COMMENT 'Completion tokens',
  `total_tokens` int NOT NULL DEFAULT '0' COMMENT 'Total tokens',
  `embedding_tokens` int NOT NULL DEFAULT '0' COMMENT 'Embedding tokens',
  `reranking_tokens` int NOT NULL DEFAULT '0' COMMENT 'Reranking tokens',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Execution created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Execution updated time',
  `finished_time` datetime DEFAULT NULL COMMENT 'Execution finished time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='App Node Execution Data Table';

CREATE TABLE `app_node_user_relation` (
  `id` int NOT NULL COMMENT 'App node user relation ID',
  `app_run_id` int NOT NULL COMMENT 'App Run ID',
  `node_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Node ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL COMMENT 'User ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='App Node Execution Relation ID';

CREATE TABLE `app_runs` (
  `id` int NOT NULL COMMENT 'Run ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `app_id` int NOT NULL COMMENT 'App ID',
  `agent_id` int NOT NULL DEFAULT '0' COMMENT 'Agent ID',
  `workflow_id` int NOT NULL DEFAULT '0' COMMENT 'Workflow ID',
  `dataset_id` int NOT NULL DEFAULT '0' COMMENT 'Dataset id',
  `tool_id` int NOT NULL DEFAULT '0' COMMENT 'Custom tool ID',
  `chatroom_id` int NOT NULL DEFAULT '0' COMMENT 'Chatroom ID',
  `type` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Trigger type 1: Debug 2: Run application 3: API',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Run name',
  `graph` json DEFAULT NULL COMMENT 'Workflow graphical data',
  `inputs` json DEFAULT NULL COMMENT 'Inputs',
  `knowledge_base_mapping` json DEFAULT NULL COMMENT 'Knowledge base mapping',
  `level` int NOT NULL DEFAULT '0' COMMENT 'The current level of operation',
  `context` json DEFAULT NULL COMMENT 'Execute context',
  `completed_edges` json DEFAULT NULL COMMENT 'Completed edges',
  `skipped_edges` json DEFAULT NULL COMMENT 'Skipped edges',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Execute status 0: Cannot execute 1: Can execute 2: Executing 3: Successfully executed 4: Failed to execute',
  `completed_steps` int NOT NULL DEFAULT '0' COMMENT 'Completed steps',
  `actual_completed_steps` int NOT NULL DEFAULT '0' COMMENT 'Actual number of completed steps',
  `need_human_confirm` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Need human confirm 0: No 1: Yes',
  `need_correct_llm` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Need correct LLM output 0: No 1: Yes',
  `error` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Error message',
  `outputs` json DEFAULT NULL COMMENT 'Outputs',
  `elapsed_time` decimal(20,6) NOT NULL DEFAULT '0.000000' COMMENT 'Elapsed time',
  `prompt_tokens` int NOT NULL DEFAULT '0' COMMENT 'Prompt tokens',
  `completion_tokens` int NOT NULL DEFAULT '0' COMMENT 'Completion tokens',
  `total_tokens` int NOT NULL DEFAULT '0' COMMENT 'Total tokens',
  `embedding_tokens` int NOT NULL DEFAULT '0' COMMENT 'Embedding tokens',
  `reranking_tokens` int NOT NULL DEFAULT '0' COMMENT 'Reranking tokens',
  `total_steps` int NOT NULL DEFAULT '0' COMMENT 'Total steps',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Run created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Run updated time',
  `finished_time` datetime DEFAULT NULL COMMENT 'Run finished time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='App Runs Data Table';

CREATE TABLE `app_workflow_relation` (
  `id` int NOT NULL COMMENT 'App workflow relation ID',
  `app_id` int NOT NULL COMMENT 'App(Agent Skill Dataset) ID',
  `workflow_id` int NOT NULL COMMENT 'Workflow ID',
  `workflow_app_id` int NOT NULL COMMENT 'Workflow app ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='App(Agent/Skill/Dataset) Workflow Relation Data Table';

CREATE TABLE `chatrooms` (
  `id` int NOT NULL COMMENT 'Chatroom ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `app_id` int NOT NULL COMMENT 'App ID',
  `max_round` int NOT NULL COMMENT 'The maximum number of chat rounds',
  `initial_message_id` int NOT NULL DEFAULT '0' COMMENT 'The initial message ID of the chat history',
  `chat_status` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Chat status 0: Stopped, 1: Chatting',
  `smart_selection` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Agent Smart Selection 0: No 1: Yes',
  `active` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Active 0: No 1: Yes',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Chatroom created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Chatroom updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Chatroom status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Chatroom Data Table';

CREATE TABLE `chatroom_agent_relation` (
  `id` int NOT NULL COMMENT 'Chatroom agent relation ID',
  `chatroom_id` int NOT NULL COMMENT 'Chatroom ID',
  `agent_id` int NOT NULL COMMENT 'Agent ID',
  `active` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Active 0: No 1: Yes'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Chatroom Agent Relation Data Table';

CREATE TABLE `chatroom_messages` (
  `id` int NOT NULL COMMENT 'Chatroom message ID',
  `chatroom_id` int NOT NULL COMMENT 'Chatroom ID',
  `app_run_id` int NOT NULL COMMENT 'App run ID',
  `user_id` int NOT NULL DEFAULT '0' COMMENT 'ID of the user who sent the message (0 when the sender is an agent)',
  `agent_id` int NOT NULL DEFAULT '0' COMMENT 'ID of the agent who sent the message (0 when the sender is a user)',
  `llm_input` json DEFAULT NULL COMMENT 'LLM input messages in LangChain format',
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'LLM output message string (or user input message)',
  `topic` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Topic of the meeting',
  `is_read` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Read status 0: Unread, 1: Read',
  `prompt_tokens` int NOT NULL DEFAULT '0' COMMENT 'Prompt tokens',
  `completion_tokens` int NOT NULL DEFAULT '0' COMMENT 'Completion tokens',
  `total_tokens` int NOT NULL DEFAULT '0' COMMENT 'Total tokens',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Message created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Message updated time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Chatroom Message Data Table';

CREATE TABLE `custom_tools` (
  `id` int NOT NULL COMMENT 'Tool ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL DEFAULT '0' COMMENT 'User ID',
  `app_id` int NOT NULL COMMENT 'App ID',
  `config` json DEFAULT NULL COMMENT 'Tool config',
  `input_variables` json DEFAULT NULL COMMENT 'Input variables',
  `dependencies` json DEFAULT NULL COMMENT 'Tool dependencies',
  `code` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Tool code',
  `output_type` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Output type 1: text 2: database 3: code 4: document',
  `output_variables` json DEFAULT NULL COMMENT 'Output variables',
  `publish_status` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Tool publish status 0: Draft 1: Published',
  `published_time` datetime DEFAULT NULL COMMENT 'Tool published time',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Tool created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Tool updated time',
  `status` tinyint(1) DEFAULT '1' COMMENT 'Tool status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Custom Tool Data Table';

INSERT INTO `custom_tools` (`id`, `team_id`, `user_id`, `app_id`, `config`, `input_variables`, `dependencies`, `code`, `output_type`, `output_variables`, `publish_status`, `published_time`, `created_time`, `updated_time`, `status`) VALUES
(1, 1, 1, 1, NULL, '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"content\": {\"name\": \"content\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"File content\"}, \"filepath\": {\"name\": \"filepath\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"File path\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', '{\"python3\": []}', '{\"python3\":\"import os\\n\\ndef write_to_file(filepath: str, content: str, mode=\'w\'):\\n    \\\"\\\"\\\"\\n    Write content to a file specified by filepath.\\n\\n    Args:\\n    - filepath (str): The path to the file.\\n    - content (str): The content to write to the file.\\n    - mode (str, optional): The mode in which to open the file (\'w\' for write, \'a\' for append). Default is \'w\'.\\n\\n    Returns:\\n    - dict: A dictionary indicating the status of the operation.\\n            {\'status\': \'True\'} if successful, {\'status\': \'<error_message>\'} if an exception occurred.\\n    \\\"\\\"\\\"\\n    try:\\n        storage_path = os.path.join(\'/storage\', filepath)\\n        with open(storage_path, mode, encoding=\'utf-8\') as file:\\n            file.write(content)\\n        return {\'status\': \'True\'}\\n    except Exception as e:\\n        return {\'status\': str(e)}\"}', 4, '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"status\": {\"name\": \"status\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Status\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', 0, NULL, '2024-12-03 08:10:50', '2024-12-03 08:16:14', 1),
(2, 1, 1, 1, 'null', '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"content\": {\"name\": \"content\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"File content\"}, \"filepath\": {\"name\": \"filepath\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"File path\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', '{\"python3\": []}', '{\"python3\":\"import os\\n\\ndef write_to_file(filepath: str, content: str, mode=\'w\'):\\n    \\\"\\\"\\\"\\n    Write content to a file specified by filepath.\\n\\n    Args:\\n    - filepath (str): The path to the file.\\n    - content (str): The content to write to the file.\\n    - mode (str, optional): The mode in which to open the file (\'w\' for write, \'a\' for append). Default is \'w\'.\\n\\n    Returns:\\n    - dict: A dictionary indicating the status of the operation.\\n            {\'status\': \'True\'} if successful, {\'status\': \'<error_message>\'} if an exception occurred.\\n    \\\"\\\"\\\"\\n    try:\\n        storage_path = os.path.join(\'/storage\', filepath)\\n        with open(storage_path, mode, encoding=\'utf-8\') as file:\\n            file.write(content)\\n        return {\'status\': \'True\'}\\n    except Exception as e:\\n        return {\'status\': str(e)}\"}', 4, '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"status\": {\"name\": \"status\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Status\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', 1, '2024-12-03 08:16:15', '2024-12-03 08:11:11', '2024-12-03 08:16:15', 1),
(3, 1, 1, 2, NULL, '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"host\": {\"name\": \"host\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Host\"}, \"port\": {\"name\": \"port\", \"type\": \"number\", \"value\": \"\", \"required\": true, \"display_name\": \"Port\"}, \"user\": {\"name\": \"user\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"User\"}, \"params\": {\"name\": \"params\", \"type\": \"string\", \"value\": \"\", \"required\": false, \"max_length\": 0, \"display_name\": \"Params\"}, \"database\": {\"name\": \"database\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Database\"}, \"password\": {\"name\": \"password\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Password\"}, \"sql_query\": {\"name\": \"sql_query\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Sql_query\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', '{\"python3\": [\"pymysql\"]}', '{\"python3\":\"import json\\nimport pymysql\\nfrom datetime import datetime\\n\\ndef execute_sql_query_with_params(host: str, user: str, password: str, database: str, port: int, sql_query: str, params: str = None):\\n    result = {\\n        \\\"status\\\": \'False\',\\n        \\\"data\\\":  {}\\n    }\\n\\n    # Connect to the database\\n    try:\\n        connection = pymysql.connect(\\n            host=host,\\n            user=user,\\n            password=password,\\n            database=database,\\n            port=port\\n        )\\n        cursor = connection.cursor(pymysql.cursors.DictCursor)\\n    except Exception as e:\\n        raise ValueError(f\\\"Error connecting to database: {str(e)}\\\")\\n\\n    try:\\n        # Parse parameters if provided and not None\\n        if params:\\n            try:\\n                params = json.loads(params)\\n                if not isinstance(params, (list, tuple)):\\n                    raise ValueError(\\\"Parameters should be a list or tuple.\\\")\\n            except json.JSONDecodeError:\\n                raise ValueError(\\\"Invalid JSON format for parameters.\\\")\\n        else:\\n            params = []  # Default to empty list if params is None or empty\\n\\n        # Determine the type of SQL query\\n        sql_type = sql_query.strip().split()[0].upper()\\n\\n        if sql_type == \\\"SELECT\\\":\\n            # Execute SELECT query\\n            cursor.execute(sql_query, params)\\n            rows = cursor.fetchall()\\n            for row in rows:\\n                for key in row:\\n                    if isinstance(row[key], datetime):\\n                        row[key] = row[key].strftime(\'%Y-%m-%d %H:%M:%S\')\\n            result[\\\"data\\\"] = rows\\n            result[\\\"status\\\"] = \'True\'\\n        else:\\n            # Execute non-SELECT query (e.g., INSERT, UPDATE, DELETE)\\n            cursor.execute(sql_query, params)\\n            connection.commit()\\n            result[\\\"status\\\"] = \'True\'\\n\\n    except Exception as e:\\n        raise ValueError(f\\\"Error executing query: {str(e)}\\\")\\n    finally:\\n        cursor.close()\\n        connection.close()\\n    return result\"}', 2, '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"data\": {\"name\": \"data\", \"type\": \"Array[object]\", \"value\": \"\", \"required\": false, \"display_name\": \"Data\"}, \"status\": {\"name\": \"status\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Status\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', 0, NULL, '2024-12-03 17:04:35', '2024-12-05 10:17:45', 1),
(4, 1, 1, 2, 'null', '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"host\": {\"name\": \"host\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Host\"}, \"port\": {\"name\": \"port\", \"type\": \"number\", \"value\": \"\", \"required\": true, \"display_name\": \"Port\"}, \"user\": {\"name\": \"user\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"User\"}, \"params\": {\"name\": \"params\", \"type\": \"string\", \"value\": \"\", \"required\": false, \"max_length\": 0, \"display_name\": \"Params\"}, \"database\": {\"name\": \"database\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Database\"}, \"password\": {\"name\": \"password\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Password\"}, \"sql_query\": {\"name\": \"sql_query\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Sql_query\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', '{\"python3\": [\"pymysql\"]}', '{\"python3\":\"import json\\nimport pymysql\\nfrom datetime import datetime\\n\\ndef execute_sql_query_with_params(host: str, user: str, password: str, database: str, port: int, sql_query: str, params: str = None):\\n    result = {\\n        \\\"status\\\": \'False\',\\n        \\\"data\\\":  {}\\n    }\\n\\n    # Connect to the database\\n    try:\\n        connection = pymysql.connect(\\n            host=host,\\n            user=user,\\n            password=password,\\n            database=database,\\n            port=port\\n        )\\n        cursor = connection.cursor(pymysql.cursors.DictCursor)\\n    except Exception as e:\\n        raise ValueError(f\\\"Error connecting to database: {str(e)}\\\")\\n\\n    try:\\n        # Parse parameters if provided and not None\\n        if params:\\n            try:\\n                params = json.loads(params)\\n                if not isinstance(params, (list, tuple)):\\n                    raise ValueError(\\\"Parameters should be a list or tuple.\\\")\\n            except json.JSONDecodeError:\\n                raise ValueError(\\\"Invalid JSON format for parameters.\\\")\\n        else:\\n            params = []  # Default to empty list if params is None or empty\\n\\n        # Determine the type of SQL query\\n        sql_type = sql_query.strip().split()[0].upper()\\n\\n        if sql_type == \\\"SELECT\\\":\\n            # Execute SELECT query\\n            cursor.execute(sql_query, params)\\n            rows = cursor.fetchall()\\n            for row in rows:\\n                for key in row:\\n                    if isinstance(row[key], datetime):\\n                        row[key] = row[key].strftime(\'%Y-%m-%d %H:%M:%S\')\\n            result[\\\"data\\\"] = rows\\n            result[\\\"status\\\"] = \'True\'\\n        else:\\n            # Execute non-SELECT query (e.g., INSERT, UPDATE, DELETE)\\n            cursor.execute(sql_query, params)\\n            connection.commit()\\n            result[\\\"status\\\"] = \'True\'\\n\\n    except Exception as e:\\n        raise ValueError(f\\\"Error executing query: {str(e)}\\\")\\n    finally:\\n        cursor.close()\\n        connection.close()\\n    return result\"}', 2, '{\"name\": \"output\", \"type\": \"object\", \"properties\": {\"data\": {\"name\": \"data\", \"type\": \"Array[object]\", \"value\": \"\", \"required\": false, \"display_name\": \"Data\"}, \"status\": {\"name\": \"status\", \"type\": \"string\", \"value\": \"\", \"required\": true, \"max_length\": 0, \"display_name\": \"Status\"}}, \"display_name\": \"\", \"to_string_keys\": \"\"}', 1, '2024-12-05 10:19:07', '2024-12-03 17:05:12', '2024-12-05 10:19:07', 1);

CREATE TABLE `datasets` (
  `id` int NOT NULL COMMENT 'Dataset ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `app_id` int NOT NULL COMMENT 'App ID',
  `process_rule_id` int NOT NULL DEFAULT '1' COMMENT 'Dataset process rule ID',
  `data_source_type` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Data source type 1: Upload files 2: Synchronize other sites',
  `collection_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Vector storage collection name',
  `embedding_model_config_id` int NOT NULL DEFAULT '0' COMMENT 'Embedding model configuration ID',
  `retriever_config` json NOT NULL COMMENT 'Retriever config',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Dataset created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Dataset updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Dataset status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Dataset Data Table';

CREATE TABLE `dataset_process_rules` (
  `id` int NOT NULL COMMENT 'Rule ID',
  `mode` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Processing mode 1: Automatic 2: Custom',
  `config` json NOT NULL COMMENT 'Rule config',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Rule created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Rule updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Rule status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Dataset Process Rule Data Table';

INSERT INTO `dataset_process_rules` (`id`, `mode`, `config`, `created_time`, `updated_time`, `status`) VALUES
(1, 1, '{\"type\": \"RecursiveCharacterTextSplitter\", \"chunk_size\": 400, \"chunk_overlap\": 200, \"keep_separator\": false, \"strip_whitespace\": true}', '2024-07-05 15:06:34', NULL, 1);

CREATE TABLE `documents` (
  `id` int NOT NULL COMMENT 'Document ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `dataset_id` int NOT NULL COMMENT 'Dataset ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Document name',
  `data_source_type` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Data source type 1: Upload files 2: Synchronize other sites 3: Workflow node output 4: Workflow node input',
  `dataset_process_rule_id` int NOT NULL COMMENT 'Dataset process rule ID',
  `upload_file_id` int NOT NULL DEFAULT '0' COMMENT 'Upload file ID',
  `node_exec_id` int NOT NULL DEFAULT '0' COMMENT 'App node execution ID',
  `word_count` int NOT NULL COMMENT 'Word count',
  `tokens` int NOT NULL COMMENT 'Tokens',
  `indexing_latency` decimal(10,6) NOT NULL DEFAULT '0.000000' COMMENT 'Indexing latency',
  `archived` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Archived status 0: Normal, 1: Archived',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Document created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Document updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Document status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Document Data Table';

CREATE TABLE `document_segments` (
  `id` int NOT NULL COMMENT 'Segment ID',
  `document_id` int NOT NULL COMMENT 'Document ID',
  `index_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Corresponding to the id in the vector library',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Segment content',
  `word_count` int NOT NULL COMMENT 'Segment word count',
  `tokens` int NOT NULL DEFAULT (0) COMMENT 'Segment tokens',
  `hit_count` int NOT NULL DEFAULT '0' COMMENT 'Hit count',
  `indexing_status` tinyint(1) NOT NULL DEFAULT (0) COMMENT 'Indexing status 0: Not indexed 1: Being indexed 2: Successfully indexed 3: Failed to be indexed',
  `indexing_time` datetime DEFAULT NULL COMMENT 'Indexing time',
  `completed_time` datetime DEFAULT NULL COMMENT 'Index completion time',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Segment created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Segment updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Segment status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Document Segment Data Table';

CREATE TABLE `document_segment_rag_records` (
  `id` int NOT NULL COMMENT 'Document segment RAG record ID',
  `rag_record_id` int NOT NULL DEFAULT '0' COMMENT 'RAG record ID',
  `dataset_id` int NOT NULL DEFAULT '0' COMMENT 'Dataset ID',
  `document_id` int NOT NULL DEFAULT '0' COMMENT 'Document ID',
  `segment_id` int NOT NULL DEFAULT '0' COMMENT 'ID of document segment retrieved',
  `score` decimal(20,6) NOT NULL DEFAULT '0.000000' COMMENT 'Document similarity score',
  `reranking_score` decimal(20,6) NOT NULL DEFAULT '0.000000' COMMENT 'Document reranking score',
  `created_time` datetime NOT NULL DEFAULT (now()) COMMENT 'Run created time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='RAG Record Table By Document Segment';

CREATE TABLE `models` (
  `id` int NOT NULL COMMENT 'Model ID',
  `supplier_id` int NOT NULL COMMENT 'Model supplier ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Model name',
  `type` tinyint(1) NOT NULL COMMENT 'Model type 1: text-generation 2: embeddings 3: reranking 4: speech2text 5: tts 6: text2img 7: moderation',
  `mode` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Request mode 1: online 2: local',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Model created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Model updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Model status 1: Normal 2: Disabled 3: Deleted	'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Model Data Table';

INSERT INTO `models` (`id`, `supplier_id`, `name`, `type`, `mode`, `created_time`, `updated_time`, `status`) VALUES
(1, 1, 'text-embedding-ada-002', 2, 1, '2024-07-13 17:37:27', '2024-10-29 09:14:20', 1),
(2, 2, 'text2vec-large-chinese', 2, 2, '2024-07-13 17:38:19', '2024-10-29 09:14:20', 1),
(3, 2, 'bge-reranker-v2-m3', 3, 2, '2024-07-13 17:38:46', '2024-10-29 09:14:23', 1),
(4, 1, 'gpt-4o', 1, 1, '2024-07-13 18:07:57', '2024-11-08 11:29:36', 1),
(5, 1, 'gpt-4o-mini', 1, 1, '2024-07-22 15:06:55', '2024-11-08 11:29:36', 1),
(6, 1, 'gpt-4-turbo', 1, 1, '2024-10-24 16:18:34', '2024-11-08 11:29:36', 1),
(7, 1, 'gpt-4-1106-preview', 1, 1, '2024-10-28 17:38:37', '2024-11-08 11:29:36', 1),
(8, 1, 'gpt-3.5-turbo', 1, 1, '2024-10-28 17:39:00', '2024-11-08 11:29:36', 1);

CREATE TABLE `model_configurations` (
  `id` int NOT NULL COMMENT 'Model supplier ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `model_id` int NOT NULL COMMENT 'Model ID',
  `config` json NOT NULL COMMENT 'Model configuration',
  `default_used` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Whether to use by default 0: no 1: yes',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Model configuration created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Model configuration updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Model configuration status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Model Configuration Data Table';

INSERT INTO `model_configurations` (`id`, `team_id`, `model_id`, `config`, `default_used`, `created_time`, `updated_time`, `status`) VALUES
(1, 1, 1, '{\"type\": \"OpenAIEmbeddings\", \"model\": \"text-embedding-ada-002\", \"max_retries\": null, \"input_pricing\": 0.0000001, \"request_timeout\": null, \"pricing_currency\": \"USD\"}', 1, '2024-07-13 17:50:56', NULL, 1),
(2, 1, 2, '{\"type\": \"Text2vecEmbeddings\"}', 1, '2024-07-13 17:52:07', NULL, 1),
(3, 1, 4, '{\"n\": 1, \"stop\": null, \"model\": \"gpt-4o\", \"streaming\": false, \"max_tokens\": null, \"http_client\": null, \"max_retries\": 2, \"temperature\": 0.7, \"model_kwargs\": {}, \"openai_proxy\": null, \"default_query\": null, \"default_headers\": null, \"openai_api_base\": null, \"request_timeout\": null, \"http_async_client\": null, \"openai_organization\": null, \"tiktoken_model_name\": null}', 1, '2024-07-16 16:54:44', NULL, 1),
(4, 1, 3, '{\"type\": \"CrossEncoderReranker\", \"model_type\": \"HuggingFaceCrossEncoder\"}', 1, '2024-07-22 15:09:09', NULL, 1),
(5, 1, 5, '{\"n\": 1, \"stop\": null, \"model\": \"gpt-4o-mini\", \"streaming\": false, \"max_tokens\": null, \"http_client\": null, \"max_retries\": 2, \"temperature\": 0.7, \"model_kwargs\": {}, \"openai_proxy\": null, \"default_query\": null, \"default_headers\": null, \"openai_api_base\": null, \"request_timeout\": null, \"http_async_client\": null, \"openai_organization\": null, \"tiktoken_model_name\": null}', 0, '2024-07-22 15:09:21', NULL, 1),
(6, 1, 6, '{\"n\": 1, \"stop\": null, \"model\": \"gpt-4-turbo\", \"streaming\": false, \"max_tokens\": null, \"http_client\": null, \"max_retries\": 2, \"temperature\": 0.7, \"model_kwargs\": {}, \"openai_proxy\": null, \"default_query\": null, \"default_headers\": null, \"openai_api_base\": null, \"request_timeout\": null, \"http_async_client\": null, \"openai_organization\": null, \"tiktoken_model_name\": null}', 0, '2024-10-24 16:20:56', NULL, 1),
(7, 1, 7, '{\"n\": 1, \"stop\": null, \"model\": \"gpt-4-1106-preview\", \"streaming\": false, \"max_tokens\": null, \"http_client\": null, \"max_retries\": 2, \"temperature\": 0.7, \"model_kwargs\": {}, \"openai_proxy\": null, \"default_query\": null, \"default_headers\": null, \"openai_api_base\": null, \"request_timeout\": null, \"http_async_client\": null, \"openai_organization\": null, \"tiktoken_model_name\": null}', 0, '2024-10-28 17:58:19', NULL, 1),
(8, 1, 8, '{\"n\": 1, \"stop\": null, \"model\": \"gpt-3.5-turbo\", \"streaming\": false, \"max_tokens\": null, \"http_client\": null, \"max_retries\": 2, \"temperature\": 0.7, \"model_kwargs\": {}, \"openai_proxy\": null, \"default_query\": null, \"default_headers\": null, \"openai_api_base\": null, \"request_timeout\": null, \"http_async_client\": null, \"openai_organization\": null, \"tiktoken_model_name\": null}', 0, '2024-10-28 17:58:30', NULL, 1);

CREATE TABLE `rag_records` (
  `id` int NOT NULL COMMENT 'RAG record ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `agent_id` int NOT NULL DEFAULT '0' COMMENT 'Agent ID',
  `workflow_id` int NOT NULL DEFAULT '0' COMMENT 'Workflow ID',
  `dataset_ids` json DEFAULT NULL COMMENT 'IDs of datasets to retrieve from',
  `type` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Trigger type 1: Debug 2: Run application',
  `input` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Input',
  `search_in_documents` json DEFAULT NULL COMMENT 'Names of documents to search in',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1: Executing 2: Successfully executed 3: Failed to execute',
  `error` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Error message',
  `elapsed_time` decimal(20,6) NOT NULL DEFAULT '0.000000' COMMENT 'Elapsed time',
  `embedding_tokens` int NOT NULL DEFAULT '0' COMMENT 'Embedding tokens',
  `reranking_tokens` int NOT NULL DEFAULT '0' COMMENT 'Reranking tokens',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Run created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Run updated time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='RAG Record Table';

CREATE TABLE `suppliers` (
  `id` int NOT NULL COMMENT 'Model supplier ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Model supplier name',
  `mode` tinyint(1) DEFAULT '1' COMMENT 'Request mode 1:online 2:local',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Supplier created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Supplier updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Supplier status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Model Supplier Data Table';

INSERT INTO `suppliers` (`id`, `name`, `mode`, `created_time`, `updated_time`, `status`) VALUES
(1, 'OpenAI', 1, '2024-07-05 10:31:30', NULL, 1),
(2, 'HuggingFace', 1, '2024-07-05 10:31:47', NULL, 1);

CREATE TABLE `supplier_configurations` (
  `id` int NOT NULL COMMENT 'Model supplier ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `supplier_id` int NOT NULL COMMENT 'Model supplier ID',
  `config` json NOT NULL COMMENT 'Model supplier configuration',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Supplier configuration created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Supplier configuration updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Supplier configuration status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Model Supplier Configuration Data Table';

INSERT INTO `supplier_configurations` (`id`, `team_id`, `supplier_id`, `config`, `created_time`, `updated_time`, `status`) VALUES
(1, 1, 2, '{}', '2024-12-03 10:30:33', NULL, 1);

CREATE TABLE `teams` (
  `id` int NOT NULL COMMENT 'Team ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Team name',
  `config` json DEFAULT NULL COMMENT 'Team config',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Team created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Team updated time',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT 'Team status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Team Data Table';

INSERT INTO `teams` (`id`, `name`, `config`, `created_time`, `updated_time`, `status`) VALUES
(1, 'Organization', NULL, '2024-11-26 17:01:33', NULL, 1);

CREATE TABLE `tool_authorizations` (
  `id` int NOT NULL COMMENT 'Provider ID',
  `team_id` int DEFAULT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `provider` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Provider Name',
  `encrypted_credentials` json DEFAULT NULL COMMENT 'Provider Config',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Provider created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Provider updated time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tool Authorization Data Table';

CREATE TABLE `upload_files` (
  `id` int NOT NULL COMMENT 'File ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'File name',
  `path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Local path relative to project root path',
  `size` int NOT NULL COMMENT 'File size',
  `extension` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'File extension',
  `mime_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'File uploaded time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Upload File Data Table';

CREATE TABLE `users` (
  `id` int NOT NULL COMMENT 'User ID',
  `team_id` int NOT NULL DEFAULT '0' COMMENT 'Team ID',
  `role` tinyint(1) NOT NULL DEFAULT '2' COMMENT 'Team role 1: Administrator 2: Ordinary Member',
  `inviter_id` int NOT NULL DEFAULT '0' COMMENT 'Inviter ID',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'User''s nickname',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'User''s mobile phone number',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'User''s email',
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'User login password',
  `password_salt` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'User login password encryption salt value',
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'User''s avatar',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'User created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'The user''s most recent updated time',
  `last_login_time` datetime DEFAULT NULL COMMENT 'The time the user last logged in',
  `last_login_ip` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'The IP address of the user''s last login',
  `language` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'en' COMMENT 'Current language',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'User status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='User Data Table';

INSERT INTO `users` (`id`, `team_id`, `role`, `inviter_id`, `nickname`, `phone`, `email`, `password`, `password_salt`, `avatar`, `created_time`, `updated_time`, `last_login_time`, `last_login_ip`, `language`, `status`) VALUES
(1, 1, 1, 0, 'administrator', NULL, 'administrator@gmail.com', 'a2ca31480dde5591eea0a5eb9569fdf5', '1732612122', NULL, '2024-11-26 17:11:42', NULL, NULL, NULL, 'en', 1);

CREATE TABLE `workflows` (
  `id` int NOT NULL COMMENT 'Workflow ID',
  `team_id` int NOT NULL COMMENT 'Team ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `app_id` int NOT NULL COMMENT 'App ID',
  `graph` json DEFAULT NULL COMMENT 'Workflow graphical data',
  `features` json DEFAULT NULL COMMENT 'Workflow features',
  `publish_status` tinyint(1) DEFAULT '0' COMMENT 'Workflow publish status 0: Draft 1: Published',
  `published_time` datetime DEFAULT NULL COMMENT 'Workflow published time',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Workflow created time',
  `updated_time` datetime DEFAULT NULL COMMENT 'Workflow updated time',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Workflow status 1: Normal 2: Disabled 3: Deleted'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Workflow Data Table';


ALTER TABLE `agents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `status` (`status`),
  ADD KEY `model_id` (`model_config_id`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `publish_status` (`publish_status`);

ALTER TABLE `agent_abilities`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `agent_id` (`agent_id`),
  ADD KEY `status` (`status`);

ALTER TABLE `agent_dataset_relation`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `agent_database_id` (`agent_id`,`dataset_id`);

ALTER TABLE `apps`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `api_token` (`api_token`) USING BTREE,
  ADD KEY `user_id` (`user_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `mode` (`mode`),
  ADD KEY `status` (`status`),
  ADD KEY `is_public` (`is_public`),
  ADD KEY `publish_status` (`publish_status`),
  ADD KEY `name` (`name`);

ALTER TABLE `app_node_executions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `workflow_id` (`workflow_id`),
  ADD KEY `type` (`type`),
  ADD KEY `status` (`status`),
  ADD KEY `app_run_id` (`app_run_id`) USING BTREE,
  ADD KEY `chatroom_id` (`chatroom_id`),
  ADD KEY `pre_node_id` (`pre_node_id`),
  ADD KEY `node_id` (`node_id`),
  ADD KEY `node_type` (`node_type`),
  ADD KEY `output_type` (`output_type`),
  ADD KEY `condition_id` (`condition_id`),
  ADD KEY `correct_output` (`correct_output`) USING BTREE,
  ADD KEY `edge_id` (`edge_id`),
  ADD KEY `level` (`level`),
  ADD KEY `need_human_confirm` (`need_human_confirm`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `child_level` (`child_level`);

ALTER TABLE `app_node_user_relation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `app_run_id` (`app_run_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `node_id` (`node_id`) USING BTREE;

ALTER TABLE `app_runs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `workflow_id` (`workflow_id`),
  ADD KEY `type` (`type`),
  ADD KEY `status` (`status`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `agent_id` (`agent_id`),
  ADD KEY `tool_id` (`tool_id`),
  ADD KEY `dataset_id` (`dataset_id`),
  ADD KEY `need_human_confirm` (`need_human_confirm`),
  ADD KEY `chatroom_id` (`chatroom_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `need_correct_llm` (`need_correct_llm`);

ALTER TABLE `app_workflow_relation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `workflow_id` (`workflow_id`),
  ADD KEY `workflow_app_id` (`workflow_app_id`);

ALTER TABLE `chatrooms`
  ADD PRIMARY KEY (`id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `status` (`status`),
  ADD KEY `active` (`active`);

ALTER TABLE `chatroom_agent_relation`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `chatroom_agent_id` (`chatroom_id`,`agent_id`),
  ADD KEY `active` (`active`);

ALTER TABLE `chatroom_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chatroom_id` (`chatroom_id`),
  ADD KEY `app_run_id` (`app_run_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `agent_id` (`agent_id`),
  ADD KEY `is_read` (`is_read`);

ALTER TABLE `custom_tools`
  ADD PRIMARY KEY (`id`),
  ADD KEY `status` (`status`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `publish_status` (`publish_status`),
  ADD KEY `output_type` (`output_type`);

ALTER TABLE `datasets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `embedding_model_id` (`embedding_model_config_id`),
  ADD KEY `status` (`status`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `process_rule_id` (`process_rule_id`);

ALTER TABLE `dataset_process_rules`
  ADD PRIMARY KEY (`id`),
  ADD KEY `status` (`status`);

ALTER TABLE `documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `dataset_id` (`dataset_id`),
  ADD KEY `status` (`status`),
  ADD KEY `upload_file_id` (`upload_file_id`),
  ADD KEY `dataset_process_rule_id` (`dataset_process_rule_id`);

ALTER TABLE `document_segments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `document_id` (`document_id`),
  ADD KEY `hit_count` (`hit_count`),
  ADD KEY `status` (`status`),
  ADD KEY `indexing_status` (`indexing_status`);

ALTER TABLE `document_segment_rag_records`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD KEY `rag_record_id` (`rag_record_id`) USING BTREE,
  ADD KEY `dataset_id` (`dataset_id`) USING BTREE,
  ADD KEY `document_id` (`document_id`) USING BTREE,
  ADD KEY `segment_id` (`segment_id`) USING BTREE;

ALTER TABLE `models`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_id` (`supplier_id`),
  ADD KEY `type` (`type`),
  ADD KEY `status` (`status`),
  ADD KEY `mode` (`mode`);

ALTER TABLE `model_configurations`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `team_id` (`team_id`,`model_id`),
  ADD KEY `status` (`status`);

ALTER TABLE `rag_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `agent_id` (`agent_id`),
  ADD KEY `workflow_id` (`workflow_id`),
  ADD KEY `type` (`type`),
  ADD KEY `status` (`status`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `status` (`status`,`mode`) USING BTREE;

ALTER TABLE `supplier_configurations`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `team_id` (`team_id`,`supplier_id`),
  ADD KEY `status` (`status`);

ALTER TABLE `teams`
  ADD PRIMARY KEY (`id`),
  ADD KEY `status` (`status`);

ALTER TABLE `tool_authorizations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `provider` (`provider`) USING BTREE,
  ADD KEY `team_id` (`team_id`) USING BTREE;

ALTER TABLE `upload_files`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD KEY `phone` (`phone`),
  ADD KEY `email` (`email`),
  ADD KEY `status` (`status`),
  ADD KEY `inviter_id` (`inviter_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `role` (`role`);

ALTER TABLE `workflows`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `status` (`status`),
  ADD KEY `publish_status` (`publish_status`);


ALTER TABLE `agents`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Agent ID';

ALTER TABLE `agent_abilities`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Ability ID';

ALTER TABLE `agent_dataset_relation`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Agent dataset relation ID';

ALTER TABLE `apps`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'App ID', AUTO_INCREMENT=949;

ALTER TABLE `app_node_executions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Node execution ID';

ALTER TABLE `app_node_user_relation`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'App node user relation ID';

ALTER TABLE `app_runs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Run ID';

ALTER TABLE `app_workflow_relation`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'App workflow relation ID';

ALTER TABLE `chatrooms`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Chatroom ID';

ALTER TABLE `chatroom_agent_relation`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Chatroom agent relation ID';

ALTER TABLE `chatroom_messages`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Chatroom message ID';

ALTER TABLE `custom_tools`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Tool ID', AUTO_INCREMENT=200;

ALTER TABLE `datasets`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Dataset ID';

ALTER TABLE `dataset_process_rules`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Rule ID', AUTO_INCREMENT=2;

ALTER TABLE `documents`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Document ID';

ALTER TABLE `document_segments`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Segment ID';

ALTER TABLE `document_segment_rag_records`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Document segment RAG record ID';

ALTER TABLE `models`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Model ID', AUTO_INCREMENT=10;

ALTER TABLE `model_configurations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Model supplier ID', AUTO_INCREMENT=10;

ALTER TABLE `rag_records`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'RAG record ID';

ALTER TABLE `suppliers`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Model supplier ID', AUTO_INCREMENT=3;

ALTER TABLE `supplier_configurations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Model supplier ID', AUTO_INCREMENT=2;

ALTER TABLE `teams`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Team ID', AUTO_INCREMENT=2;

ALTER TABLE `tool_authorizations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Provider ID';

ALTER TABLE `upload_files`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'File ID';

ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'User ID', AUTO_INCREMENT=2;

ALTER TABLE `workflows`
  MODIFY `id` int NOT NULL AUTO_INCREMENT COMMENT 'Workflow ID';
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
