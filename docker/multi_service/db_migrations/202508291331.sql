-- UPDATE AI_TOOL_LLM_RECORDS TABLE AI_TOOL_TYPE FIELD COMMENT TO ADD WORKFLOW NODE GENERATOR TYPE
ALTER TABLE ai_tool_llm_records MODIFY COLUMN ai_tool_type tinyint(1) NOT NULL DEFAULT 0 COMMENT 'AI tool type 1: Agent generator 2: Skill generator 3: Round Table meeting summary generator 4: Round Table app target data generator 5: See the batch agent example 6: Workflow node generator';
