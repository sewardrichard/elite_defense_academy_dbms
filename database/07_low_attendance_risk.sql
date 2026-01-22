-- =====================================================
-- 7. IDENTIFY STUDENTS WITH <75% ATTENDANCE
-- =====================================================
-- Purpose: Flag students who are below the critical attendance threshold.
--          Based on the performance_summary table for quick access.
-- =====================================================

SELECT 
    s.service_number,
    s.first_name,
    s.last_name,
    c.company_name,
    ps.attendance_rate,
    ps.current_standing
FROM 
    students s
JOIN 
    performance_summary ps ON s.student_id = ps.student_id
JOIN 
    companies c ON s.company_id = c.company_id
WHERE 
    ps.attendance_rate < 75.00
ORDER BY 
    ps.attendance_rate ASC;
