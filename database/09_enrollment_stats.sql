-- =====================================================
-- 9. GENERATE COURSE ENROLLMENT STATS
-- =====================================================
-- Purpose: Summary of enrollments per course, broken down by status.
-- =====================================================

SELECT 
    c.course_code,
    c.name AS course_name,
    COUNT(e.student_id) AS total_enrolled,
    COUNT(CASE WHEN e.status = 'In Progress' THEN 1 END) AS in_progress,
    COUNT(CASE WHEN e.status = 'Completed' THEN 1 END) AS completed,
    COUNT(CASE WHEN e.status = 'Failed' THEN 1 END) AS failed,
    COUNT(CASE WHEN e.status = 'Withdrawn' THEN 1 END) AS withdrawn
FROM 
    courses c
LEFT JOIN 
    enrollments e ON c.course_id = e.course_id
GROUP BY 
    c.course_id, c.course_code, c.name
ORDER BY 
    total_enrolled DESC;
