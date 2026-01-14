-- Week 4 - Grants for views and functions
-- Apply after 10_views_reports.sql and 11_stored_procs.sql

-- Role assumed to exist: srms_user (single-app user)

-- Revoke defaults (optional tightening)
-- REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Views: allow instructors and readonly users to query
GRANT SELECT ON
    vw_course_students,
    vw_course_roster,
    vw_course_avg_grades,
    vw_low_attendance,
    vw_top_gpa,
    vw_course_enrollment_stats,
    vw_transcript,
    vw_attendance_report
TO srms_user;

-- Functions: allow instructors to execute operational procs
GRANT EXECUTE ON FUNCTION
    sp_enroll_student(INT, INT, DATE),
    sp_record_grade(INT, VARCHAR, NUMERIC, NUMERIC, DATE, TEXT),
    sp_mark_attendance(INT, INT, DATE, VARCHAR, TEXT),
    sp_refresh_performance_summary(INT),
    sp_refresh_all_performance()
TO srms_user;
