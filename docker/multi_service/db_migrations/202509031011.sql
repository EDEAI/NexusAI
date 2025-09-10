-- Sync model configurations from team_id=1 to teams with type=2
-- This script will add missing model configurations for type=2 teams based on team_id=1 as the master template
-- It will check for missing combinations of (team_id, model_id)

-- Insert missing model configurations for type=2 teams based on team_id=1 template
INSERT INTO model_configurations (
    team_id,
    model_id,
    config,
    default_used,
    sort_order,
    created_time,
    status
)
SELECT 
    t.id as team_id,
    mc1.model_id,
    mc1.config,
    mc1.default_used,
    mc1.sort_order,
    NOW() as created_time,
    1 as status
FROM teams t
CROSS JOIN (
    SELECT model_id, config, default_used, sort_order
    FROM model_configurations 
    WHERE team_id = 1
) mc1
WHERE t.type = 2  -- Only teams with type=2
AND NOT EXISTS (
    SELECT 1 
    FROM model_configurations mc2 
    WHERE mc2.team_id = t.id 
    AND mc2.model_id = mc1.model_id
);

-- Set gpt-4.1 model as default for type=2 teams
UPDATE model_configurations mc
SET mc.default_used = 1
WHERE mc.model_id = (
    SELECT m.id 
    FROM models m 
    WHERE m.name = 'gpt-4.1'
)
AND mc.team_id IN (
    SELECT t.id 
    FROM teams t 
    WHERE t.type = 2
);
