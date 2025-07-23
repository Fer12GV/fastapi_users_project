-- Database initialization script for FastAPI Users Project
-- This script runs automatically when the PostgreSQL container starts

-- Create custom schema for the application
CREATE SCHEMA IF NOT EXISTS fastapi_users;

-- Create application-specific user with limited privileges
-- Note: The main user is created by Docker, this is for application operations
DO $$
BEGIN
    -- Create role if it doesn't exist
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'fastapi_app_user') THEN
        CREATE ROLE fastapi_app_user WITH LOGIN PASSWORD 'app_secure_password_2024';
    END IF;
END
$$;

-- Grant necessary permissions to the application user
GRANT USAGE ON SCHEMA fastapi_users TO fastapi_app_user;
GRANT CREATE ON SCHEMA fastapi_users TO fastapi_app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA fastapi_users TO fastapi_app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA fastapi_users TO fastapi_app_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA fastapi_users GRANT ALL ON TABLES TO fastapi_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA fastapi_users GRANT ALL ON SEQUENCES TO fastapi_app_user;

-- Set search path for the application user
ALTER ROLE fastapi_app_user SET search_path = fastapi_users, public;

-- Create extension for UUID generation (if needed in the future)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log the initialization
-- INSERT INTO pg_catalog.pg_stat_statements_info (dealloc) VALUES (0) ON CONFLICT DO NOTHING;
