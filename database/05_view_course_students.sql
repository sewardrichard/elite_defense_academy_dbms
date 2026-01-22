-- =====================================================
-- 5. VIEW STUDENTS IN SPECIFIC COURSE
-- =====================================================
-- Purpose: Retrieve a list of all students currently enrolled in a specific course.
--          Replace 'TAC-101' with the desired course_code.
-- =====================================================

SELECT 
    s.service_number,
    s.first_name,
    s.last_name,
    s.rank,
    s.status AS student_status,
    e.start_date,
    e.status AS enrollment_status,
    e.final_score,
    e.grade_letter
FROM 
    students s
JOIN 
    enrollments e ON s.student_id = e.student_id
JOIN 
    courses c ON e.course_id = c.course_id
WHERE 
    c.course_code = 'TAC-101'  -- <-- Parameter to be replaced
ORDER BY 
    s.last_name, s.first_name;
