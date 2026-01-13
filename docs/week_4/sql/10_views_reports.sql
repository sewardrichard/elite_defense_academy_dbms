-- Week 4 - Advanced Views & Reports
-- Elite Defense Academy - Student Records Management System
-- Prereq: Week 2 schema & data

DROP VIEW IF EXISTS vw_attendance_report CASCADE;
DROP VIEW IF EXISTS vw_transcript CASCADE;
DROP VIEW IF EXISTS vw_course_enrollment_stats CASCADE;
DROP VIEW IF EXISTS vw_top_gpa CASCADE;
DROP VIEW IF EXISTS vw_low_attendance CASCADE;
DROP VIEW IF EXISTS vw_course_avg_grades CASCADE;
DROP VIEW IF EXISTS vw_course_roster CASCADE;
DROP VIEW IF EXISTS vw_course_students CASCADE;

-- Students per course (roster)
CREATE OR REPLACE VIEW vw_course_students AS
SELECT
    c.course_id,
    c.course_code,
    c.name AS course_name,
    e.enrollment_id,
    e.status AS enrollment_status,
    e.start_date,
    e.completion_date,
    s.student_id,
    s.service_number,
    s.first_name,
    s.last_name,
    s.email,
    s.rank,
    s.status AS student_status,
    co.company_name
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses c  ON c.course_id  = e.course_id
LEFT JOIN companies co ON co.company_id = s.company_id;

CREATE OR REPLACE VIEW vw_course_roster AS
SELECT cs.*, s.contact_number, s.gender, s.date_of_birth
FROM vw_course_students cs
JOIN students s ON s.student_id = cs.student_id;

-- Course-level average grades (uses final_score or weighted grades)
CREATE OR REPLACE VIEW vw_course_avg_grades AS
WITH grade_totals AS (
    SELECT g.enrollment_id,
           SUM(g.score * g.weight) / NULLIF(SUM(g.weight), 0) AS weighted_score
    FROM grades g
    GROUP BY g.enrollment_id
)
SELECT
    c.course_id,
    c.course_code,
    c.name AS course_name,
    COUNT(e.enrollment_id) AS enrollments,
    SUM(CASE WHEN e.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
    AVG(COALESCE(e.final_score, gt.weighted_score)) AS avg_score,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY COALESCE(e.final_score, gt.weighted_score)) AS median_score,
    SUM(CASE WHEN COALESCE(e.final_score, gt.weighted_score) >= 90 THEN 1 ELSE 0 END) AS a_bucket,
    SUM(CASE WHEN COALESCE(e.final_score, gt.weighted_score) BETWEEN 80 AND 89.999 THEN 1 ELSE 0 END) AS b_bucket,
    SUM(CASE WHEN COALESCE(e.final_score, gt.weighted_score) BETWEEN 70 AND 79.999 THEN 1 ELSE 0 END) AS c_bucket,
    SUM(CASE WHEN COALESCE(e.final_score, gt.weighted_score) < 70 THEN 1 ELSE 0 END) AS d_f_bucket
FROM enrollments e
JOIN courses c ON c.course_id = e.course_id
LEFT JOIN grade_totals gt ON gt.enrollment_id = e.enrollment_id
GROUP BY c.course_id, c.course_code, c.name;

-- Students with attendance rate < 75% per course
CREATE OR REPLACE VIEW vw_low_attendance AS
WITH attendance_calc AS (
    SELECT a.student_id, a.course_id,
           SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100 AS attendance_rate,
           COUNT(*) AS total_sessions
    FROM attendance a
    GROUP BY a.student_id, a.course_id
)
SELECT
    c.course_id,
    c.course_code,
    c.name AS course_name,
    s.student_id,
    s.service_number,
    s.first_name,
    s.last_name,
    ac.attendance_rate,
    ac.total_sessions
FROM attendance_calc ac
JOIN students s ON s.student_id = ac.student_id
JOIN courses c ON c.course_id = ac.course_id
WHERE ac.attendance_rate < 75;

-- Top 10 students by GPA
CREATE OR REPLACE VIEW vw_top_gpa AS
SELECT * FROM (
    SELECT
        ps.student_id,
        s.service_number,
        s.first_name,
        s.last_name,
        ps.gpa,
        ps.total_credits,
        ps.attendance_rate,
        ps.current_standing,
        ROW_NUMBER() OVER (
            ORDER BY ps.gpa DESC NULLS LAST,
                     ps.total_credits DESC,
                     s.last_name, s.first_name
        ) AS gpa_rank
    FROM performance_summary ps
    JOIN students s ON s.student_id = ps.student_id
    WHERE ps.gpa IS NOT NULL
) ranked
WHERE gpa_rank <= 10;

-- Course enrollment statistics
CREATE OR REPLACE VIEW vw_course_enrollment_stats AS
SELECT
    c.course_id,
    c.course_code,
    c.name AS course_name,
    COUNT(*) AS total_enrollments,
    SUM(CASE WHEN e.status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_count,
    SUM(CASE WHEN e.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
    SUM(CASE WHEN e.status = 'Withdrawn' THEN 1 ELSE 0 END) AS withdrawn_count,
    SUM(CASE WHEN e.status = 'Failed' THEN 1 ELSE 0 END) AS failed_count
FROM enrollments e
JOIN courses c ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.name;

-- Transcript view (per enrollment)
CREATE OR REPLACE VIEW vw_transcript AS
WITH grade_totals AS (
    SELECT g.enrollment_id,
           SUM(g.score * g.weight) / NULLIF(SUM(g.weight), 0) AS weighted_score
    FROM grades g
    GROUP BY g.enrollment_id
)
SELECT
    s.student_id,
    s.service_number,
    s.first_name,
    s.last_name,
    c.course_code,
    c.name AS course_name,
    c.credits,
    e.enrollment_id,
    e.start_date,
    e.completion_date,
    e.status AS enrollment_status,
    COALESCE(e.final_score, gt.weighted_score) AS final_score,
    e.grade_letter,
    COALESCE(e.final_score, gt.weighted_score) / 25.0 AS gpa_like_score
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses c ON c.course_id = e.course_id
LEFT JOIN grade_totals gt ON gt.enrollment_id = e.enrollment_id;

-- Attendance report (daily roll-up per course)
CREATE OR REPLACE VIEW vw_attendance_report AS
SELECT
    a.course_id,
    c.course_code,
    c.name AS course_name,
    a.muster_date,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) AS late_count,
    SUM(CASE WHEN a.status = 'AWOL' THEN 1 ELSE 0 END) AS awol_count,
    SUM(CASE WHEN a.status = 'Excused' THEN 1 ELSE 0 END) AS excused_count,
    COUNT(*) AS total_records
FROM attendance a
JOIN courses c ON c.course_id = a.course_id
GROUP BY a.course_id, c.course_code, c.name, a.muster_date;
