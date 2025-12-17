-- Elite Defense Academy: Security & RBAC Policies
-- Date: 2026-01-16

-- 1. Create Roles
-- Application User (Read/Write)
CREATE ROLE app_user WITH LOGIN PASSWORD 'app_secure_pass';

-- Analyst (Read Only)
CREATE ROLE analyst_viewer WITH LOGIN PASSWORD 'analyst_secure_pass';

-- 2. Grant Permissions
-- App User needs access to all operational tables
GRANT CONNECT ON DATABASE elite_defense_academy TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Analyst needs read-only access for reporting
GRANT CONNECT ON DATABASE elite_defense_academy TO analyst_viewer;
GRANT USAGE ON SCHEMA public TO analyst_viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_viewer;

-- 3. Row Level Security (RLS) Example
-- Ensure Cadets can only be deleted by Superusers (Postgres default)
ALTER TABLE cadets ENABLE ROW LEVEL SECURITY;

-- Policy: Only Admins can delete
CREATE POLICY admin_delete_only ON cadets
    FOR DELETE
    TO app_user
    USING (false); -- Effectively blocks app_user from deleting, requires superuser override

-- Policy: Everyone can view
CREATE POLICY all_view ON cadets
    FOR SELECT
    USING (true);
