-- =====================================================
-- 8. RANK TOP 10 STUDENTS BY GPA
-- =====================================================
-- Purpose: Identify the top performing cadets based on GPA.
-- =====================================================

SELECT 
    RANK() OVER (ORDER BY ps.gpa DESC) AS rank,
    s.service_number,
    s.first_name,
    s.last_name,
    c.company_name,
    ps.gpa,
    ps.total_credits
FROM 
    students s
JOIN 
    performance_summary ps ON s.student_id = ps.student_id
JOIN 
    companies c ON s.company_id = c.company_id
ORDER BY 
    ps.gpa DESC
LIMIT 10;
