-- Elite Defense Academy: Database Schema
-- Version: 2.0 (User Defined)
-- Date: 2026-01-16

-- ==============================================
-- 1. COMPANIES (Units)
-- ==============================================
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_code VARCHAR(10) UNIQUE,
    company_name VARCHAR(100) NOT NULL,
    commanding_officer VARCHAR(100),
    max_strength INT
);

-- ==============================================
-- 2. CADETS (Core Personnel)
-- ==============================================
CREATE TABLE cadets (
    cadet_id SERIAL PRIMARY KEY,
    service_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    enrollment_date DATE NOT NULL,
    rank VARCHAR(20) CHECK (rank IN ('Recruit', 'Private', 'Corporal', 'Sergeant', 'Lieutenant')),
    company_id INT REFERENCES companies(company_id) ON DELETE SET NULL,
    status VARCHAR(20) CHECK (status IN ('Active', 'Graduated', 'Discharged', 'Medical Leave')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 3. TRAINING MODULES (Catalog)
-- ==============================================
CREATE TABLE training_modules (
    module_id SERIAL PRIMARY KEY,
    module_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    credits INT CHECK (credits > 0),
    department VARCHAR(50) CHECK (department IN ('Cyber', 'Physical', 'Strategic', 'Tactical', 'Medical')),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('Basic', 'Advanced', 'Elite')),
    total_sessions INT
);

-- ==============================================
-- 4. SERVICE RECORDS (Enrollments M:N)
-- ==============================================
CREATE TABLE service_records (
    record_id SERIAL PRIMARY KEY,
    cadet_id INT NOT NULL REFERENCES cadets(cadet_id) ON DELETE CASCADE,
    module_id INT NOT NULL REFERENCES training_modules(module_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    completion_date DATE,
    status VARCHAR(20) CHECK (status IN ('Active', 'Completed', 'Dropped', 'Failed')),
    final_score DECIMAL(5,2) CHECK (final_score >= 0 AND final_score <= 100),
    grade_letter CHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cadet_id, module_id)
);

-- ==============================================
-- 5. PERFORMANCE EVALS (Assessments)
-- ==============================================
CREATE TABLE performance_evals (
    eval_id SERIAL PRIMARY KEY,
    record_id INT NOT NULL REFERENCES service_records(record_id) ON DELETE CASCADE,
    assessment_type VARCHAR(50),
    assessment_name VARCHAR(100) NOT NULL,
    score DECIMAL(5,2) CHECK (score >= 0 AND score <= 100),
    weight DECIMAL(3,2),
    evaluation_date DATE NOT NULL,
    evaluator_notes TEXT,
    evaluator_rank VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 6. MUSTER ROLLS (Attendance)
-- ==============================================
CREATE TABLE muster_rolls (
    roll_id SERIAL PRIMARY KEY,
    cadet_id INT NOT NULL REFERENCES cadets(cadet_id) ON DELETE CASCADE,
    module_id INT NOT NULL REFERENCES training_modules(module_id),
    muster_date DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('Present', 'Absent', 'Excused', 'Late', 'AWOL')),
    check_in_time TIME,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cadet_id, module_id, muster_date)
);

-- ==============================================
-- 7. CADET PERFORMANCE SUMMARY (Analytics)
-- ==============================================
CREATE TABLE cadet_performance_summary (
    summary_id SERIAL PRIMARY KEY,
    cadet_id INT UNIQUE REFERENCES cadets(cadet_id) ON DELETE CASCADE,
    overall_gpa DECIMAL(3,2) CHECK (overall_gpa >= 0 AND overall_gpa <= 4.00),
    attendance_rate DECIMAL(5,2) CHECK (attendance_rate >= 0 AND attendance_rate <= 100),
    total_modules_completed INT,
    total_modules_failed INT,
    avg_physical_score DECIMAL(5,2),
    avg_tactical_score DECIMAL(5,2),
    avg_cyber_score DECIMAL(5,2),
    performance_tier VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 8. ATTRITION RISK (AI Predictions)
-- ==============================================
CREATE TABLE attrition_risk (
    risk_id SERIAL PRIMARY KEY,
    cadet_id INT NOT NULL REFERENCES cadets(cadet_id) ON DELETE CASCADE,
    risk_score DECIMAL(5,2) CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) CHECK (risk_level IN ('Low', 'Medium', 'High', 'Critical')),
    risk_factors JSON, -- Stores structured factors e.g. {"attendance": "low", "gpa": "warning"}
    recommended_actions TEXT,
    assessment_date DATE NOT NULL,
    next_review_date DATE
);

-- ==============================================
-- INDEXES FOR PERFORMANCE
-- ==============================================
CREATE INDEX idx_cadets_service_number ON cadets(service_number);
CREATE INDEX idx_service_records_status ON service_records(status);
CREATE INDEX idx_performance_evals_record ON performance_evals(record_id);
CREATE INDEX idx_muster_rolls_date ON muster_rolls(muster_date);
CREATE INDEX idx_attrition_risk_level ON attrition_risk(risk_level);
