-- =====================================================
-- Elite Defense Academy - Student Records Management System
-- User Permissions Script
-- =====================================================
-- Run this script to set up database users and roles
-- Run as PostgreSQL superuser (postgres)
-- =====================================================

-- =====================================================
-- ROLE DEFINITIONS
-- =====================================================

-- Create roles (groups) for permission management
-- Roles can be assigned to multiple users

-- Admin role: Full access to all operations
CREATE ROLE srms_admin;

-- Instructor role: Read/Write for day-to-day operations
CREATE ROLE srms_instructor;

-- Read-only role: For analytics and reporting
CREATE ROLE srms_readonly;

-- =====================================================
-- GRANT PERMISSIONS TO ROLES
-- =====================================================

-- Connect to the database first
\c student_records_db;

-- ----- ADMIN ROLE -----
-- Full access to everything
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO srms_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO srms_admin;
GRANT USAGE, CREATE ON SCHEMA public TO srms_admin;

-- ----- INSTRUCTOR ROLE -----
-- Read access to all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO srms_instructor;

-- Write access to operational tables
GRANT INSERT, UPDATE, DELETE ON 
    enrollments, 
    grades, 
    attendance, 
    performance_summary 
TO srms_instructor;

-- Sequence usage for inserting records
GRANT USAGE ON SEQUENCE 
    enrollments_enrollment_id_seq, 
    grades_grade_id_seq, 
    attendance_attendance_id_seq,
    performance_summary_summary_id_seq
TO srms_instructor;

-- ----- READONLY ROLE -----
-- Read-only access to all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO srms_readonly;

-- =====================================================
-- CREATE APPLICATION USERS
-- =====================================================

-- Admin user (for system administration)
CREATE USER srms_admin_user WITH PASSWORD 'CHANGE_THIS_PASSWORD_ADMIN';
GRANT srms_admin TO srms_admin_user;

-- Instructor user (for instructors/trainers)
CREATE USER srms_instructor_user WITH PASSWORD 'CHANGE_THIS_PASSWORD_INSTRUCTOR';
GRANT srms_instructor TO srms_instructor_user;

-- Read-only user (for analytics/reporting)
CREATE USER srms_report_user WITH PASSWORD 'CHANGE_THIS_PASSWORD_REPORT';
GRANT srms_readonly TO srms_report_user;

-- Application service user (for backend API)
CREATE USER srms_app_user WITH PASSWORD 'CHANGE_THIS_PASSWORD_APP';
GRANT srms_instructor TO srms_app_user;

-- =====================================================
-- FUTURE GRANTS (for tables created later)
-- =====================================================

-- Ensure future tables inherit permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL ON TABLES TO srms_admin;
    
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO srms_instructor;
    
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO srms_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL ON SEQUENCES TO srms_admin;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT USAGE ON SEQUENCES TO srms_instructor;

-- =====================================================
-- ROW-LEVEL SECURITY (Optional - Enable if needed)
-- =====================================================
-- Uncomment these to enable row-level security
-- This allows restricting which rows users can see

-- ALTER TABLE students ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE grades ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify permissions:

-- List all roles:
-- SELECT rolname FROM pg_roles WHERE rolname LIKE 'srms_%';

-- List all users:
-- SELECT usename FROM pg_user WHERE usename LIKE 'srms_%';

-- Check table permissions:
-- SELECT grantee, table_name, privilege_type 
-- FROM information_schema.table_privileges 
-- WHERE grantee LIKE 'srms_%'
-- ORDER BY grantee, table_name;

-- =====================================================
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
