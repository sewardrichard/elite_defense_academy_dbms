-- Verification Script for Phase 7
-- Run this to check for data anomalies or constraint violations that might have slipped through (though constraints should prevent them)

BEGIN;

-- 1. Check for orphaned enrollments (should be 0)
SELECT COUNT(*) AS orphaned_enrollments 
FROM enrollments e 
LEFT JOIN students s ON s.student_id = e.student_id 
WHERE s.student_id IS NULL;

-- 2. Check for invalid grades (should be 0)
SELECT COUNT(*) AS invalid_grades
FROM grades
WHERE score < 0 OR score > 100;

-- 3. Check for students with NO company assigned
SELECT count(*) as unassigned_students
FROM students 
WHERE company_id IS NULL;

-- 4. Check for duplicate active enrollments (same student, same course, In Progress)
SELECT student_id, course_id, COUNT(*) 
FROM enrollments 
WHERE status = 'In Progress' 
GROUP BY student_id, course_id 
HAVING COUNT(*) > 1;

-- 5. Validate Email formats (basic check)
SELECT email 
FROM students 
WHERE email NOT LIKE '%@%.%';

ROLLBACK;
