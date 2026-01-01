-- =====================================================
-- Elite Defense Academy - Student Records Management System
-- Performance Indexes Script
-- =====================================================
-- Run this script after creating all tables
-- Indexes optimize query performance for common operations
-- =====================================================

-- =====================================================
-- STUDENTS TABLE INDEXES
-- =====================================================

-- Index for company-based lookups (list students in a company)
CREATE INDEX idx_students_company 
    ON students(company_id);

-- Index for filtering by status (active students, graduated, etc.)
CREATE INDEX idx_students_status 
    ON students(status);

-- Index for name searches (last name, first name for sorting)
CREATE INDEX idx_students_name 
    ON students(last_name, first_name);

-- Index for email lookups (login, contact)
CREATE INDEX idx_students_email 
    ON students(email) 
    WHERE email IS NOT NULL;

-- =====================================================
-- ENROLLMENTS TABLE INDEXES
-- =====================================================

-- Index for student enrollment history
CREATE INDEX idx_enrollments_student 
    ON enrollments(student_id);

-- Index for course enrollment lists
CREATE INDEX idx_enrollments_course 
    ON enrollments(course_id);

-- Index for date-based queries (current semester, historical)
CREATE INDEX idx_enrollments_dates 
    ON enrollments(start_date, completion_date);

-- Index for enrollment status filtering
CREATE INDEX idx_enrollments_status 
    ON enrollments(status);

-- Composite index for student-course lookups
CREATE INDEX idx_enrollments_student_course 
    ON enrollments(student_id, course_id);

-- =====================================================
-- GRADES TABLE INDEXES
-- =====================================================

-- Index for enrollment-based grade lookups
CREATE INDEX idx_grades_enrollment 
    ON grades(enrollment_id);

-- Index for assessment date queries
CREATE INDEX idx_grades_date 
    ON grades(assessment_date);

-- Index for assessment type filtering
CREATE INDEX idx_grades_type 
    ON grades(assessment_type);

-- =====================================================
-- ATTENDANCE TABLE INDEXES
-- =====================================================

-- Index for student attendance history
CREATE INDEX idx_attendance_student 
    ON attendance(student_id);

-- Index for course attendance records
CREATE INDEX idx_attendance_course 
    ON attendance(course_id);

-- Index for date-based queries (daily muster)
CREATE INDEX idx_attendance_date 
    ON attendance(muster_date);

-- Composite index for student attendance by date
CREATE INDEX idx_attendance_student_date 
    ON attendance(student_id, muster_date);

-- Composite index for course attendance by date (daily roster)
CREATE INDEX idx_attendance_course_date 
    ON attendance(course_id, muster_date);

-- Index for attendance status filtering
CREATE INDEX idx_attendance_status 
    ON attendance(status);

-- =====================================================
-- PERFORMANCE_SUMMARY TABLE INDEXES
-- =====================================================

-- Index for standing-based queries (at-risk students)
CREATE INDEX idx_performance_standing 
    ON performance_summary(current_standing);

-- Index for GPA-based filtering
CREATE INDEX idx_performance_gpa 
    ON performance_summary(gpa);

-- =====================================================
-- ATTRITION_RISK TABLE INDEXES
-- =====================================================

-- Index for student risk lookups
CREATE INDEX idx_attrition_student 
    ON attrition_risk(student_id);

-- Index for risk assessment date (time-series analysis)
CREATE INDEX idx_attrition_date 
    ON attrition_risk(assessment_date);

-- Index for risk level filtering (high-risk students)
CREATE INDEX idx_attrition_level 
    ON attrition_risk(risk_level);

-- Composite index for recent risk by student
CREATE INDEX idx_attrition_student_date 
    ON attrition_risk(student_id, assessment_date DESC);

-- =====================================================
-- COURSES TABLE INDEXES
-- =====================================================

-- Index for department-based filtering
CREATE INDEX idx_courses_department 
    ON courses(department);

-- Index for difficulty level filtering
CREATE INDEX idx_courses_difficulty 
    ON courses(difficulty_level);

-- =====================================================
-- COMPANIES TABLE INDEXES
-- =====================================================

-- Index for location-based queries
CREATE INDEX idx_companies_location 
    ON companies(location);

-- =====================================================
-- VERIFICATION QUERY
-- =====================================================
-- Run this to verify all indexes were created:

-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE schemaname = 'public' 
-- ORDER BY tablename, indexname;

-- =====================================================
-- END OF INDEX CREATION SCRIPT
-- =====================================================
