ALTER TABLE ai_tool_llm_records
ADD COLUMN ai_tool_type INT NOT NULL DEFAULT '0' COMMENT 'AI tool type 1: Agent generator 2: Skill generator 3: Round Table meeting summary generator 4: Round Table app target data generator' 
AFTER app_run_id;

ALTER TABLE ai_tool_llm_records
ADD INDEX `ai_tool_type` (`ai_tool_type`);

UPDATE ai_tool_llm_records r
JOIN app_runs a ON r.app_run_id = a.id
SET r.ai_tool_type = a.ai_tool_type;

ALTER TABLE app_runs
DROP COLUMN ai_tool_type;