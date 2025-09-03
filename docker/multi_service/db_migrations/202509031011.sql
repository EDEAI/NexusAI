-- Sync model configurations from team_id=1 to all other teams
-- This script will add missing model configurations for teams based on team_id=1 as the master template
-- It will check for missing combinations of (team_id, model_id) where status=1

-- Insert missing model configurations for all teams based on team_id=1 template
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
    WHERE team_id = 1 AND status = 1
) mc1
WHERE t.id != 1  -- Exclude team_id=1 as it's the source
AND t.status = 1  -- Only active teams
AND NOT EXISTS (
    SELECT 1 
    FROM model_configurations mc2 
    WHERE mc2.team_id = t.id 
    AND mc2.model_id = mc1.model_id 
    AND mc2.status = 1
);
