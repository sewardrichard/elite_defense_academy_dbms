-- Week 4 - Stored Procedures / Functions (PL/pgSQL)
-- Elite Defense Academy - Student Records Management System
-- Prereq: Week 2 schema & data

-- Safety drops for reruns
DROP FUNCTION IF EXISTS sp_enroll_student(INT, INT, DATE) CASCADE;
DROP FUNCTION IF EXISTS sp_record_grade(INT, VARCHAR, NUMERIC, NUMERIC, DATE, TEXT) CASCADE;
DROP FUNCTION IF EXISTS sp_mark_attendance(INT, INT, DATE, VARCHAR, TEXT) CASCADE;
DROP FUNCTION IF EXISTS sp_refresh_performance_summary(INT) CASCADE;
DROP FUNCTION IF EXISTS sp_refresh_all_performance() CASCADE;

-- Enroll a student in a course (respects unique constraint student/course/start_date)
CREATE OR REPLACE FUNCTION sp_enroll_student(
    p_student_id INT,
    p_course_id INT,
    p_start_date DATE
) RETURNS INT AS $$
DECLARE
    v_enrollment_id INT;
BEGIN
    -- Prevent duplicate enrollment for same course/start date
    SELECT enrollment_id INTO v_enrollment_id
    FROM enrollments
    WHERE student_id = p_student_id
      AND course_id = p_course_id
      AND start_date = p_start_date;

    IF FOUND THEN
        RETURN v_enrollment_id; -- already exists
    END IF;

    INSERT INTO enrollments (student_id, course_id, start_date, status)
    VALUES (p_student_id, p_course_id, p_start_date, 'In Progress')
    RETURNING enrollment_id INTO v_enrollment_id;

    RETURN v_enrollment_id;
END;
$$ LANGUAGE plpgsql;

-- Record a grade entry and update enrollment aggregates if provided
CREATE OR REPLACE FUNCTION sp_record_grade(
    p_enrollment_id INT,
    p_assessment_type VARCHAR,
    p_score NUMERIC,
    p_weight NUMERIC,
    p_assessment_date DATE DEFAULT CURRENT_DATE,
    p_remarks TEXT DEFAULT NULL
) RETURNS VOID AS $$
DECLARE
    v_weighted_score NUMERIC;
    v_total_weight NUMERIC;
    v_final_score NUMERIC;
BEGIN
    INSERT INTO grades (enrollment_id, assessment_type, score, weight, assessment_date, remarks)
    VALUES (p_enrollment_id, p_assessment_type, p_score, p_weight, p_assessment_date, p_remarks);

    -- Recompute weighted score for the enrollment
    SELECT SUM(score * weight), SUM(weight)
    INTO v_weighted_score, v_total_weight
    FROM grades
    WHERE enrollment_id = p_enrollment_id;

    IF v_total_weight IS NOT NULL AND v_total_weight > 0 THEN
        v_final_score := v_weighted_score / v_total_weight;
        UPDATE enrollments
        SET final_score = v_final_score,
            grade_letter = CASE 
                WHEN v_final_score >= 90 THEN 'A'
                WHEN v_final_score >= 80 THEN 'B'
                WHEN v_final_score >= 70 THEN 'C'
                WHEN v_final_score >= 60 THEN 'D'
                ELSE 'F'
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE enrollment_id = p_enrollment_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Mark attendance (upsert per student/course/date)
CREATE OR REPLACE FUNCTION sp_mark_attendance(
    p_student_id INT,
    p_course_id INT,
    p_muster_date DATE,
    p_status VARCHAR,
    p_remarks TEXT DEFAULT NULL
) RETURNS INT AS $$
DECLARE
    v_attendance_id INT;
BEGIN
    SELECT attendance_id INTO v_attendance_id
    FROM attendance
    WHERE student_id = p_student_id
      AND course_id = p_course_id
      AND muster_date = p_muster_date;

    IF FOUND THEN
        UPDATE attendance
        SET status = p_status,
            remarks = p_remarks,
            updated_at = CURRENT_TIMESTAMP
        WHERE attendance_id = v_attendance_id;
    ELSE
        INSERT INTO attendance (student_id, course_id, muster_date, status, remarks)
        VALUES (p_student_id, p_course_id, p_muster_date, p_status, p_remarks)
        RETURNING attendance_id INTO v_attendance_id;
    END IF;

    RETURN v_attendance_id;
END;
$$ LANGUAGE plpgsql;

-- Refresh performance summary for one student
CREATE OR REPLACE FUNCTION sp_refresh_performance_summary(
    p_student_id INT
) RETURNS VOID AS $$
DECLARE
    v_gpa NUMERIC;
    v_attendance_rate NUMERIC;
    v_total_credits INT;
    v_standing VARCHAR;
BEGIN
    -- GPA: convert final_score (0-100) to 4.0 scale by dividing by 25
    SELECT AVG(final_score / 25.0), SUM(c.credits)
    INTO v_gpa, v_total_credits
    FROM enrollments e
    JOIN courses c ON c.course_id = e.course_id
    WHERE e.student_id = p_student_id
      AND e.final_score IS NOT NULL;

    -- Attendance rate: present / total across courses
    SELECT SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100
    INTO v_attendance_rate
    FROM attendance
    WHERE student_id = p_student_id;

    -- Standing heuristic
    IF v_gpa IS NULL THEN
        v_standing := 'Good Standing';
    ELSIF v_gpa >= 3.5 THEN
        v_standing := 'Deans List';
    ELSIF v_gpa >= 3.0 THEN
        v_standing := 'Honor Roll';
    ELSIF v_gpa >= 2.0 THEN
        v_standing := 'Good Standing';
    ELSE
        v_standing := 'Probation';
    END IF;

    INSERT INTO performance_summary (student_id, gpa, attendance_rate, total_credits, current_standing, last_updated)
    VALUES (p_student_id, v_gpa, v_attendance_rate, COALESCE(v_total_credits, 0), v_standing, CURRENT_TIMESTAMP)
    ON CONFLICT (student_id)
    DO UPDATE SET gpa = EXCLUDED.gpa,
                  attendance_rate = EXCLUDED.attendance_rate,
                  total_credits = EXCLUDED.total_credits,
                  current_standing = EXCLUDED.current_standing,
                  last_updated = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Refresh performance for all students
CREATE OR REPLACE FUNCTION sp_refresh_all_performance()
RETURNS VOID AS $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN SELECT student_id FROM students LOOP
        PERFORM sp_refresh_performance_summary(rec.student_id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
