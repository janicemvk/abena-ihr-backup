-- Abena IHR Database Setup Script
-- Run this script as the postgres superuser

-- 1. Create the database
CREATE DATABASE abena_ihr;

-- 2. Create the user with encrypted password
CREATE USER abena_user WITH ENCRYPTED PASSWORD 'EKZz4h%*6yyH$WqK';

-- 3. Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE abena_ihr TO abena_user;

-- 4. Allow user to create databases (useful for testing)
ALTER USER abena_user CREATEDB;

-- 5. Connect to the new database and grant schema privileges
\c abena_ihr

-- Grant usage and create privileges on public schema
GRANT USAGE, CREATE ON SCHEMA public TO abena_user;

-- Grant all privileges on all tables in public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO abena_user;

-- Grant privileges on all sequences in public schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO abena_user;

-- Set default privileges for future tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO abena_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO abena_user;

-- Display success message
SELECT 'Database setup completed successfully!' AS status; 