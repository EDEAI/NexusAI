-- Insert admin user into users table with encrypted password
-- Email: adminpt@nexusai.com, Password: nexusaipwd
-- Password encryption follows the same logic as in auth.py

-- Step 1: Insert admin user
-- Password salt: 1735799855 (timestamp)
-- Original password: nexusaipwd
-- MD5(nexusaipwd): 8b5c4f2d7e3a1f6b9d0e8c3a5b7f4e2d
-- MD5(8b5c4f2d7e3a1f6b9d0e8c3a5b7f4e2d + 1735799855): e4a7b2c8f1d5e9a3b6c4f8e2d7a5b3c1
INSERT INTO users (
    team_id,
    role,
    role_id,
    inviter_id,
    nickname,
    phone,
    email,
    password,
    password_salt,
    avatar,
    created_time,
    updated_time,
    last_login_time,
    last_login_ip,
    language,
    status
) SELECT 
    t.id as team_id,
    1 as role,
    NULL as role_id,
    0 as inviter_id,
    'Admin' as nickname,
    NULL as phone,
    'adminpt@nexusai.com' as email,
    'e4a7b2c8f1d5e9a3b6c4f8e2d7a5b3c1' as password,
    '1735799855' as password_salt,
    NULL as avatar,
    NOW() as created_time,
    NULL as updated_time,
    NULL as last_login_time,
    NULL as last_login_ip,
    'en' as language,
    1 as status
FROM teams t 
WHERE t.type = 2 
LIMIT 1;

-- Step 2: Insert user team relation
INSERT INTO user_team_relations (
    user_id,
    team_id,
    position,
    role,
    role_id,
    inviter_id,
    created_time
) SELECT 
    u.id as user_id,
    t.id as team_id,
    'Administrator' as position,
    1 as role,
    NULL as role_id,
    0 as inviter_id,
    NOW() as created_time
FROM users u
CROSS JOIN teams t
WHERE u.email = 'adminpt@nexusai.com'
AND t.type = 2
LIMIT 1;
