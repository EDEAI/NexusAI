-- Create user third party association table
CREATE TABLE user_three_parties (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key for user third party associations',
    user_id INT NOT NULL COMMENT 'Reference to user ID from users table',
    platform VARCHAR(50) NOT NULL COMMENT 'Third party platform name',
    openid VARCHAR(255) NOT NULL COMMENT 'Third party platform open ID',
    sundry VARCHAR(500) DEFAULT '' COMMENT 'Miscellaneous information',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Record update timestamp',
    INDEX idx_user_id (user_id) COMMENT 'Index on user_id for faster queries',
    UNIQUE KEY uk_user_platform_openid (user_id, platform, openid) COMMENT 'Unique constraint for user-platform-openid combination'
) COMMENT 'Table for storing user third party platform associations';

-- Initialize data from users table to user_three_parties table
INSERT INTO user_three_parties (user_id, platform, openid)
SELECT id, platform, openid 
FROM users 
WHERE platform IS NOT NULL AND openid IS NOT NULL;

-- Drop indexes on platform and openid columns in users table
DROP INDEX IF EXISTS idx_users_platform ON users;
DROP INDEX IF EXISTS idx_users_openid ON users;

-- Drop platform and openid columns from users table
ALTER TABLE users 
DROP COLUMN IF EXISTS platform,
DROP COLUMN IF EXISTS openid;