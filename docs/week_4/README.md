# Week 4 — Advanced SQL & Automation

Prerequisite: Week 2 schema, indexes, and roles (`srms_admin`, `srms_instructor`, `srms_readonly`) are already created in `student_records_db`.

## Scripts (run in order)
1) `sql/10_views_reports.sql` — analytical views for rosters, grades, attendance, GPA, transcripts, and enrollment stats.
2) `sql/11_stored_procs.sql` — PL/pgSQL helpers for enrollment, grades, attendance upsert, and refreshing performance summaries.
3) `sql/12_grants.sql` — grants SELECT on views to reporting roles and EXECUTE on helper functions.

### Quick run
```bash
psql -U postgres -d student_records_db -f docs/week_4/sql/10_views_reports.sql
psql -U postgres -d student_records_db -f docs/week_4/sql/11_stored_procs.sql
psql -U postgres -d student_records_db -f docs/week_4/sql/12_grants.sql
```

## Views delivered
- `vw_course_students`, `vw_course_roster`
- `vw_course_avg_grades`
- `vw_low_attendance`
- `vw_top_gpa`
- `vw_course_enrollment_stats`
- `vw_transcript`
- `vw_attendance_report`

## Functions delivered
- `sp_enroll_student(p_student_id, p_course_id, p_start_date)`
- `sp_record_grade(p_enrollment_id, p_assessment_type, p_score, p_weight, p_assessment_date?, p_remarks?)`
- `sp_mark_attendance(p_student_id, p_course_id, p_muster_date, p_status, p_remarks?)`
- `sp_refresh_performance_summary(p_student_id)`
- `sp_refresh_all_performance()`

## Sample checklist queries
```sql
-- Students in a specific course
SELECT * FROM vw_course_students WHERE course_code = 'TAC-101';

-- Course-level average grades
SELECT course_code, avg_score, median_score FROM vw_course_avg_grades;

-- Students with <75% attendance
SELECT * FROM vw_low_attendance ORDER BY attendance_rate;

-- Top 10 students by GPA
SELECT * FROM vw_top_gpa ORDER BY gpa_rank;

-- Enrollment stats
SELECT * FROM vw_course_enrollment_stats;
```
