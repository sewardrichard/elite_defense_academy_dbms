-- =====================================================
-- 6. CALCULATE COURSE-LEVEL AVERAGE GRADES
-- =====================================================
-- Purpose: Determine the average final score and GPA impact for each course.
--          Useful for identifying difficult courses or grading anomalies.
-- =====================================================

SELECT 
    c.course_code,
    c.name AS course_name,
    c.department,
    COUNT(e.student_id) AS total_students,
    ROUND(AVG(e.final_score), 2) AS average_score,
    MAX(e.final_score) AS highest_score,
    MIN(e.final_score) AS lowest_score
FROM 
    courses c
JOIN 
    enrollments e ON c.course_id = e.course_id
WHERE 
    e.status IN ('Completed', 'Failed') -- Only count finished determinations
    AND e.final_score IS NOT NULL
GROUP BY 
    c.course_id, c.course_code, c.name, c.department
ORDER BY 
    average_score DESC;
