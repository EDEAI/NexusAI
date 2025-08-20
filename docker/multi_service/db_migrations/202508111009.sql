-- Add position field to users table after nickname field
ALTER TABLE users ADD COLUMN position VARCHAR(100) DEFAULT NULL COMMENT 'User position' AFTER nickname;