-- =====================================================
-- Elite Defense Academy - Simple User Setup
-- =====================================================
-- Run as superuser: psql -U postgres -d student_records_db -f docs/week_2/sql/04_user_permissions.sql
-- Then connect with: psql -U srms_user -d student_records_db -W
-- =====================================================

\set ON_ERROR_STOP on

\if :{?srms_user_pwd}
\else
\echo 'ERROR: Set -v srms_user_pwd=... when invoking psql.'
\quit
\endif

-- Create a single application user (password supplied at runtime)
CREATE USER srms_user WITH PASSWORD :'srms_user_pwd';

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO srms_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO srms_user;
GRANT USAGE, CREATE ON SCHEMA public TO srms_user;

-- Future tables will inherit these permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO srms_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO srms_user;

\echo 'User created: srms_user'
\echo 'Update the password in your .env file'
-- SELECT grantee, table_name, privilege_type 
-- FROM information_schema.table_privileges 
-- WHERE grantee LIKE 'srms_%'
-- ORDER BY grantee, table_name;
-- IMPORTANT SECURITY NOTES
-- =====================================================
-- 1. CHANGE ALL DEFAULT PASSWORDS before production use
-- 2. Use strong, unique passwords for each user
-- 3. Consider using environment variables for passwords
-- 4. Regularly audit user access and permissions
-- 5. Remove unused user accounts promptly
-- =====================================================

-- =====================================================
-- END OF USER PERMISSIONS SCRIPT
-- =====================================================
