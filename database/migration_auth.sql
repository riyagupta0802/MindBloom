-- ============================================================================
-- MINDBLOOM DATABASE MIGRATION — AUTHENTICATION SYSTEM
-- Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
-- Description: Safely adds 'password_hash' column to 'users' table.
--              Existing demo accounts retain NULL password_hash and remain intact.
-- ============================================================================

USE mindbloom_db;

-- 1. Add password_hash column if not already present
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'mindbloom_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'password_hash';

SET @stmt = IF(@col_exists = 0, 
  'ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL DEFAULT NULL COMMENT "Bcrypt hashed password" AFTER user_type;', 
  'SELECT "Column password_hash already exists" AS message;');

PREPARE alter_stmt FROM @stmt;
EXECUTE alter_stmt;
DEALLOCATE PREPARE alter_stmt;
