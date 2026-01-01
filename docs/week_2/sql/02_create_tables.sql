-- =====================================================
-- Elite Defense Academy - Student Records Management System
-- Table Creation Script
-- =====================================================
-- Run this script after connecting to student_records_db
-- Tables are created in dependency order
-- =====================================================

-- =====================================================
-- 1. COMPANIES TABLE (No dependencies)
-- =====================================================
-- Purpose: Group students into operational units (Platoons, Companies)
-- =====================================================

CREATE TABLE companies (
    company_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(100) NOT NULL,
    location        VARCHAR(200) NOT NULL,
    commanding_officer VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique Constraints
    CONSTRAINT uq_companies_name UNIQUE (company_name)
);

COMMENT ON TABLE companies IS 'Organizational units for grouping students (e.g., Platoons, Companies)';
COMMENT ON COLUMN companies.company_id IS 'Primary key - auto-generated company identifier';
COMMENT ON COLUMN companies.company_name IS 'Unique name of the company/platoon';
COMMENT ON COLUMN companies.location IS 'Physical location or barracks assignment';
COMMENT ON COLUMN companies.commanding_officer IS 'Name of the officer in charge';

-- =====================================================
-- 2. STUDENTS TABLE (Depends on: companies)
-- =====================================================
-- Purpose: Maintain official personnel records for all trainees
-- =====================================================

CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    company_id      INTEGER,
    service_number  VARCHAR(20) NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    date_of_birth   DATE NOT NULL,
    gender          VARCHAR(10),
    contact_number  VARCHAR(20),
    email           VARCHAR(100),
    address         TEXT,
    rank            VARCHAR(30) DEFAULT 'Recruit',
    status          VARCHAR(20) DEFAULT 'Active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique Constraints
    CONSTRAINT uq_students_service_number UNIQUE (service_number),
    CONSTRAINT uq_students_email UNIQUE (email),
    
    -- Check Constraints
    CONSTRAINT chk_students_gender CHECK (gender IN ('Male', 'Female', 'Other')),
    CONSTRAINT chk_students_status CHECK (status IN ('Active', 'Graduated', 'Discharged', 'AWOL', 'Suspended')),
    CONSTRAINT chk_students_dob CHECK (date_of_birth <= CURRENT_DATE),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_students_company 
        FOREIGN KEY (company_id) 
        REFERENCES companies(company_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

COMMENT ON TABLE students IS 'Official personnel records for all cadets/trainees';
COMMENT ON COLUMN students.student_id IS 'Primary key - auto-generated student identifier';
COMMENT ON COLUMN students.company_id IS 'Foreign key to companies table';
COMMENT ON COLUMN students.service_number IS 'Unique military/academy service number';
COMMENT ON COLUMN students.first_name IS 'Student first name';
COMMENT ON COLUMN students.last_name IS 'Student last name/surname';
COMMENT ON COLUMN students.date_of_birth IS 'Date of birth for age verification';
COMMENT ON COLUMN students.gender IS 'Gender identity (Male/Female/Other)';
COMMENT ON COLUMN students.status IS 'Current enrollment status';

-- =====================================================
-- 3. COURSES TABLE (No dependencies)
-- =====================================================
-- Purpose: Define the training curriculum catalog
-- =====================================================

CREATE TABLE courses (
    course_id       SERIAL PRIMARY KEY,
    course_code     VARCHAR(20) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    credits         INTEGER NOT NULL,
    department      VARCHAR(100) NOT NULL,
    difficulty_level VARCHAR(20) DEFAULT 'Basic',
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique Constraints
    CONSTRAINT uq_courses_code UNIQUE (course_code),
    
    -- Check Constraints
    CONSTRAINT chk_courses_credits CHECK (credits > 0 AND credits <= 20),
    CONSTRAINT chk_courses_difficulty CHECK (difficulty_level IN ('Basic', 'Intermediate', 'Advanced'))
);

COMMENT ON TABLE courses IS 'Training curriculum catalog with all available modules';
COMMENT ON COLUMN courses.course_id IS 'Primary key - auto-generated course identifier';
COMMENT ON COLUMN courses.course_code IS 'Unique course code (e.g., TAC-101, WPN-202)';
COMMENT ON COLUMN courses.name IS 'Full course/module name';
COMMENT ON COLUMN courses.credits IS 'Credit hours (1-20)';
COMMENT ON COLUMN courses.department IS 'Department offering the course';
COMMENT ON COLUMN courses.difficulty_level IS 'Course difficulty tier';

-- =====================================================
-- 4. ENROLLMENTS TABLE (Depends on: students, courses)
-- =====================================================
-- Purpose: Link students to courses (service records)
-- =====================================================

CREATE TABLE enrollments (
    enrollment_id   SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL,
    course_id       INTEGER NOT NULL,
    start_date      DATE NOT NULL,
    completion_date DATE,
    final_score     DECIMAL(5,2),
    grade_letter    CHAR(2),
    status          VARCHAR(20) DEFAULT 'In Progress',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Check Constraints
    CONSTRAINT chk_enrollments_dates CHECK (completion_date IS NULL OR completion_date >= start_date),
    CONSTRAINT chk_enrollments_score CHECK (final_score IS NULL OR (final_score >= 0.00 AND final_score <= 100.00)),
    CONSTRAINT chk_enrollments_grade CHECK (grade_letter IS NULL OR grade_letter IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')),
    CONSTRAINT chk_enrollments_status CHECK (status IN ('In Progress', 'Completed', 'Withdrawn', 'Failed')),
    
    -- Unique Constraint (prevent duplicate enrollments)
    CONSTRAINT uq_enrollments_student_course_date UNIQUE (student_id, course_id, start_date),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_enrollments_student 
        FOREIGN KEY (student_id) 
        REFERENCES students(student_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_enrollments_course 
        FOREIGN KEY (course_id) 
        REFERENCES courses(course_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

COMMENT ON TABLE enrollments IS 'Links students to courses - their service/training records';
COMMENT ON COLUMN enrollments.enrollment_id IS 'Primary key - auto-generated enrollment identifier';
COMMENT ON COLUMN enrollments.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN enrollments.course_id IS 'Foreign key to courses table';
COMMENT ON COLUMN enrollments.start_date IS 'Date enrollment began';
COMMENT ON COLUMN enrollments.completion_date IS 'Date of completion (NULL if in progress)';
COMMENT ON COLUMN enrollments.final_score IS 'Final calculated score (0-100)';
COMMENT ON COLUMN enrollments.grade_letter IS 'Final letter grade (A+ through F)';

-- =====================================================
-- 5. GRADES TABLE (Depends on: enrollments)
-- =====================================================
-- Purpose: Capture specific assessment results within enrollments
-- =====================================================

CREATE TABLE grades (
    grade_id        SERIAL PRIMARY KEY,
    enrollment_id   INTEGER NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    score           DECIMAL(5,2) NOT NULL,
    weight          DECIMAL(4,2) NOT NULL,
    assessment_date DATE DEFAULT CURRENT_DATE,
    remarks         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Check Constraints
    CONSTRAINT chk_grades_score CHECK (score >= 0.00 AND score <= 100.00),
    CONSTRAINT chk_grades_weight CHECK (weight > 0.00 AND weight <= 1.00),
    CONSTRAINT chk_grades_assessment_type CHECK (assessment_type IN ('Exam', 'Practical', 'Quiz', 'Assignment', 'Field Exercise', 'Final Exam')),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_grades_enrollment 
        FOREIGN KEY (enrollment_id) 
        REFERENCES enrollments(enrollment_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

COMMENT ON TABLE grades IS 'Individual assessment results (exams, practicals) within enrollments';
COMMENT ON COLUMN grades.grade_id IS 'Primary key - auto-generated grade identifier';
COMMENT ON COLUMN grades.enrollment_id IS 'Foreign key to enrollments table';
COMMENT ON COLUMN grades.assessment_type IS 'Type of assessment (Exam, Practical, Quiz, etc.)';
COMMENT ON COLUMN grades.score IS 'Raw score achieved (0-100)';
COMMENT ON COLUMN grades.weight IS 'Weight factor for final grade calculation (0.01-1.00)';

-- =====================================================
-- 6. ATTENDANCE TABLE (Depends on: students, courses)
-- =====================================================
-- Purpose: Track daily presence (muster rolls)
-- =====================================================

CREATE TABLE attendance (
    attendance_id   SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL,
    course_id       INTEGER NOT NULL,
    muster_date     DATE NOT NULL,
    status          VARCHAR(10) NOT NULL,
    remarks         TEXT,
    recorded_by     VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Check Constraints
    CONSTRAINT chk_attendance_status CHECK (status IN ('Present', 'Absent', 'Late', 'AWOL', 'Excused')),
    CONSTRAINT chk_attendance_date CHECK (muster_date <= CURRENT_DATE),
    
    -- Unique Constraint (one record per student/course/day)
    CONSTRAINT uq_attendance_student_course_date UNIQUE (student_id, course_id, muster_date),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_attendance_student 
        FOREIGN KEY (student_id) 
        REFERENCES students(student_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_attendance_course 
        FOREIGN KEY (course_id) 
        REFERENCES courses(course_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

COMMENT ON TABLE attendance IS 'Daily muster/attendance records for accountability';
COMMENT ON COLUMN attendance.attendance_id IS 'Primary key - auto-generated attendance identifier';
COMMENT ON COLUMN attendance.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN attendance.course_id IS 'Foreign key to courses table';
COMMENT ON COLUMN attendance.muster_date IS 'Date of attendance record';
COMMENT ON COLUMN attendance.status IS 'Attendance status (Present, Absent, Late, AWOL, Excused)';

-- =====================================================
-- 7. PERFORMANCE_SUMMARY TABLE (Depends on: students)
-- =====================================================
-- Purpose: Pre-calculated metrics for quick cadet standing access
-- =====================================================

CREATE TABLE performance_summary (
    summary_id      SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL,
    gpa             DECIMAL(3,2),
    attendance_rate DECIMAL(5,2),
    total_credits   INTEGER DEFAULT 0,
    current_standing VARCHAR(30) DEFAULT 'Good Standing',
    last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique Constraint (one summary per student)
    CONSTRAINT uq_performance_student UNIQUE (student_id),
    
    -- Check Constraints
    CONSTRAINT chk_performance_gpa CHECK (gpa IS NULL OR (gpa >= 0.00 AND gpa <= 4.00)),
    CONSTRAINT chk_performance_attendance CHECK (attendance_rate IS NULL OR (attendance_rate >= 0.00 AND attendance_rate <= 100.00)),
    CONSTRAINT chk_performance_credits CHECK (total_credits >= 0),
    CONSTRAINT chk_performance_standing CHECK (current_standing IN ('Good Standing', 'Academic Warning', 'Probation', 'Deans List', 'Honor Roll', 'Suspended')),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_performance_student 
        FOREIGN KEY (student_id) 
        REFERENCES students(student_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

COMMENT ON TABLE performance_summary IS 'Pre-calculated performance metrics for quick access';
COMMENT ON COLUMN performance_summary.summary_id IS 'Primary key - auto-generated summary identifier';
COMMENT ON COLUMN performance_summary.student_id IS 'Foreign key to students table (1:1 relationship)';
COMMENT ON COLUMN performance_summary.gpa IS 'Grade Point Average (0.00-4.00 scale)';
COMMENT ON COLUMN performance_summary.attendance_rate IS 'Overall attendance percentage (0-100)';
COMMENT ON COLUMN performance_summary.total_credits IS 'Total credits earned';
COMMENT ON COLUMN performance_summary.current_standing IS 'Current academic/disciplinary standing';

-- =====================================================
-- 8. ATTRITION_RISK TABLE (Depends on: students)
-- =====================================================
-- Purpose: ML-driven risk assessments for student dropout
-- =====================================================

CREATE TABLE attrition_risk (
    risk_id             SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL,
    assessment_date     DATE NOT NULL DEFAULT CURRENT_DATE,
    risk_score          DECIMAL(5,2) NOT NULL,
    risk_level          VARCHAR(20) NOT NULL,
    contributing_factors TEXT,
    model_version       VARCHAR(20),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Check Constraints
    CONSTRAINT chk_attrition_score CHECK (risk_score >= 0.00 AND risk_score <= 100.00),
    CONSTRAINT chk_attrition_level CHECK (risk_level IN ('Low', 'Medium', 'High', 'Critical')),
    CONSTRAINT chk_attrition_date CHECK (assessment_date <= CURRENT_DATE),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_attrition_student 
        FOREIGN KEY (student_id) 
        REFERENCES students(student_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

COMMENT ON TABLE attrition_risk IS 'ML-driven dropout risk assessments for students';
COMMENT ON COLUMN attrition_risk.risk_id IS 'Primary key - auto-generated risk assessment identifier';
COMMENT ON COLUMN attrition_risk.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN attrition_risk.assessment_date IS 'Date of risk assessment';
COMMENT ON COLUMN attrition_risk.risk_score IS 'Risk score from ML model (0-100)';
COMMENT ON COLUMN attrition_risk.risk_level IS 'Categorized risk level (Low/Medium/High/Critical)';
COMMENT ON COLUMN attrition_risk.contributing_factors IS 'JSON or text description of risk factors';

-- =====================================================
-- AUTO-UPDATE TRIGGER FOR updated_at COLUMNS
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at column
CREATE TRIGGER trg_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_students_updated_at 
    BEFORE UPDATE ON students 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_courses_updated_at 
    BEFORE UPDATE ON courses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_enrollments_updated_at 
    BEFORE UPDATE ON enrollments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VERIFICATION QUERY
-- =====================================================
-- Run this to verify all tables were created successfully:

-- SELECT table_name 
-- FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;

-- =====================================================
-- END OF TABLE CREATION SCRIPT
-- =====================================================
