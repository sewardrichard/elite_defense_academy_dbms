-- =====================================================
-- Elite Defense Academy - Student Records Management System
-- Database Initialization Script
-- =====================================================
-- Run this script as a PostgreSQL superuser (postgres)
-- =====================================================

-- Drop database if exists (for clean setup)
-- WARNING: Uncomment only if you want to reset everything
-- DROP DATABASE IF EXISTS student_records_db;

-- Create the database
CREATE DATABASE student_records_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0
    CONNECTION LIMIT = -1;

-- Add a comment to describe the database
COMMENT ON DATABASE student_records_db IS 'Elite Defense Academy Student Records Management System (SRMS)';

-- =====================================================
-- After creating the database, connect to it and run
-- the remaining SQL scripts (02, 03, 04)
-- =====================================================
