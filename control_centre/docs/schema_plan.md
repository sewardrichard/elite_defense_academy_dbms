# Database Schema Plan: Elite Defense Academy

## Overview
This document outlines the normalized (3NF) database schema for the **Elite Defense Academy** personnel management system. This system tracks cadet training, performance analytics, and attrition risk prediction.

---

## Core Operational Tables

### 1. Cadets
- **Table Name**: `cadets`
- **Description**: Core personnel records for all cadets.
- **Columns**:
  - `cadet_id` (PK, Serial): Unique identifier.
  - `service_number` (VARCHAR, Unique): Official service ID (e.g., "SN-2024-001").
  - `first_name` (VARCHAR, NOT NULL): Given name.
  - `last_name` (VARCHAR, NOT NULL): Family name.
  - `email` (VARCHAR, Unique, NOT NULL): Official communication channel.
  - `date_of_birth` (DATE, NOT NULL): Birth date.
  - `enrollment_date` (DATE, NOT NULL): Academy entry date.
  - `rank` (VARCHAR): Current military rank (Recruit, Private, Corporal).
  - `company_id` (FK → companies.company_id): Unit assignment.
  - `status` (VARCHAR): Active/Graduated/Discharged/Medical Leave.
  - `created_at`, `updated_at` (TIMESTAMP): Audit trail.

**Constraints**:
- `status` CHECK: IN ('Active', 'Graduated', 'Discharged', 'Medical Leave')
- `rank` CHECK: IN ('Recruit', 'Private', 'Corporal', 'Sergeant')

---

### 2. Companies
- **Table Name**: `companies`
- **Description**: Organizational units for cadet grouping.
- **Columns**:
  - `company_id` (PK, Serial): Unique identifier.
  - `company_code` (VARCHAR, Unique): Unit designation (e.g., "A-Company", "B-Company").
  - `company_name` (VARCHAR, NOT NULL): Full unit name.
  - `commanding_officer` (VARCHAR): CO name.
  - `max_strength` (INT): Maximum capacity.

**Purpose**: Enables unit-level analytics and reporting.

---

### 3. Training Modules
- **Table Name**: `training_modules`
- **Description**: Catalog of available training programs.
- **Columns**:
  - `module_id` (PK, Serial): Unique identifier.
  - `module_code` (VARCHAR, Unique): Course code (e.g., "CS-101", "CQC-200", "TAC-301").
  - `name` (VARCHAR, NOT NULL): Descriptive module name.
  - `credits` (INT, CHECK > 0): Credit hours/value.
  - `department` (VARCHAR): Cyber/Physical/Strategic/Tactical/Medical.
  - `difficulty_level` (VARCHAR): Basic/Advanced/Elite.
  - `total_sessions` (INT): Expected number of training sessions.

**Constraints**:
- `department` CHECK: IN ('Cyber', 'Physical', 'Strategic', 'Tactical', 'Medical')

---

### 4. Service Records
- **Table Name**: `service_records`
- **Description**: Junction table linking cadets to training modules (many-to-many).
- **Columns**:
  - `record_id` (PK, Serial): Unique key.
  - `cadet_id` (FK → cadets.cadet_id, NOT NULL): Enrolled cadet.
  - `module_id` (FK → training_modules.module_id, NOT NULL): Training module.
  - `start_date` (DATE, NOT NULL): Enrollment date.
  - `completion_date` (DATE): Module completion (NULL if active).
  - `status` (VARCHAR): Active/Completed/Dropped/Failed.
  - `final_score` (DECIMAL(5,2)): Calculated final score (0-100).
  - `grade_letter` (CHAR(1)): A/B/C/D/F.
  - `created_at`, `updated_at` (TIMESTAMP): Audit trail.

**Constraints**:
- `final_score` CHECK: >= 0 AND <= 100
- UNIQUE (cadet_id, module_id): Prevent duplicate enrollments.

---

### 5. Performance Evals
- **Table Name**: `performance_evals`
- **Description**: Individual assessments within modules.
- **Columns**:
  - `eval_id` (PK, Serial): Unique identifier.
  - `record_id` (FK → service_records.record_id, NOT NULL): Linked enrollment.
  - `assessment_type` (VARCHAR): Exam/Practical/Field Exercise/Physical Test.
  - `assessment_name` (VARCHAR, NOT NULL): Specific test name.
  - `score` (DECIMAL(5,2), CHECK 0-100): Raw score.
  - `weight` (DECIMAL(3,2)): Percentage weight (0.00-1.00).
  - `evaluation_date` (DATE, NOT NULL): Test date.
  - `evaluator_notes` (TEXT): Instructor feedback.
  - `evaluator_rank` (VARCHAR): Evaluator's rank.
  - `created_at` (TIMESTAMP): Audit trail.

**Purpose**: Enables granular performance tracking and weighted GPA calculations.

---

### 6. Muster Rolls
- **Table Name**: `muster_rolls`
- **Description**: Daily attendance logs.
- **Columns**:
  - `roll_id` (PK, Serial): Log identifier.
  - `cadet_id` (FK → cadets.cadet_id, NOT NULL): Cadet present/absent.
  - `module_id` (FK → training_modules.module_id, NOT NULL): Training session.
  - `muster_date` (DATE, NOT NULL): Date of muster.
  - `status` (VARCHAR): Present/Absent/Excused/Late/AWOL.
  - `check_in_time` (TIME): Arrival time.
  - `notes` (TEXT): Additional context.
  - `created_at` (TIMESTAMP): Audit trail.

**Constraints**:
- `status` CHECK: IN ('Present', 'Absent', 'Excused', 'Late', 'AWOL')
- UNIQUE (cadet_id, module_id, muster_date): One record per cadet per day per module.

---

## Analytics & Summary Tables

### 7. Cadet Performance Summary
- **Table Name**: `cadet_performance_summary`
- **Description**: Pre-calculated aggregate metrics per cadet (for dashboard/reporting efficiency).
- **Columns**:
  - `summary_id` (PK, Serial): Unique identifier.
  - `cadet_id` (FK → cadets.cadet_id, Unique): One summary per cadet.
  - `overall_gpa` (DECIMAL(3,2)): Calculated GPA (0.00-4.00).
  - `attendance_rate` (DECIMAL(5,2)): Percentage of sessions attended.
  - `total_modules_completed` (INT): Count of completed modules.
  - `total_modules_failed` (INT): Count of failed modules.
  - `avg_physical_score` (DECIMAL(5,2)): Average score in Physical department.
  - `avg_tactical_score` (DECIMAL(5,2)): Average score in Tactical department.
  - `avg_cyber_score` (DECIMAL(5,2)): Average score in Cyber department.
  - `performance_tier` (VARCHAR): Elite/High Performer/Standard/At-Risk.
  - `last_updated` (TIMESTAMP): Last calculation timestamp.

**Purpose**: 
- Enables fast dashboard queries without recalculating aggregates.
- Updated via scheduled ETL jobs or triggers.

**Constraints**:
- `overall_gpa` CHECK: >= 0.00 AND <= 4.00
- `attendance_rate` CHECK: >= 0 AND <= 100

---

### 8. Attrition Risk
- **Table Name**: `attrition_risk`
- **Description**: ML/analytics-driven predictions for cadet dropout risk.
- **Columns**:
  - `risk_id` (PK, Serial): Unique identifier.
  - `cadet_id` (FK → cadets.cadet_id, NOT NULL): Assessed cadet.
  - `risk_score` (DECIMAL(5,2), CHECK 0-100): Probability score (0=low, 100=critical).
  - `risk_level` (VARCHAR): Low/Medium/High/Critical.
  - `risk_factors` (JSON): Structured data with contributing factors:
    ```json
    {
      "attendance_issues": true,
      "low_gpa": false,
      "medical_flags": 2,
      "disciplinary_actions": 1
    }
    ```
  - `recommended_actions` (TEXT): Intervention suggestions.
  - `assessment_date` (DATE, NOT NULL): Date of risk calculation.
  - `next_review_date` (DATE): Scheduled re-assessment.

**Purpose**: 
- Supports proactive intervention for at-risk cadets.
- Populated via Python ML pipeline or SQL analytics queries.

**Constraints**:
- `risk_level` CHECK: IN ('Low', 'Medium', 'High', 'Critical')

---

## Relationships Summary

```
COMPANIES (1) ──< (M) CADETS
CADETS (1) ──< (M) SERVICE_RECORDS
TRAINING_MODULES (1) ──< (M) SERVICE_RECORDS
SERVICE_RECORDS (1) ──< (M) PERFORMANCE_EVALS
CADETS (1) ──< (M) MUSTER_ROLLS
TRAINING_MODULES (1) ──< (M) MUSTER_ROLLS
CADETS (1) ── (1) CADET_PERFORMANCE_SUMMARY
CADETS (1) ──< (M) ATTRITION_RISK
```

---

## Normalization (3NF) Verification

### 1st Normal Form (1NF)
✅ All columns contain atomic values.  
✅ No repeating groups or arrays (except JSON in `risk_factors` for flexibility).

### 2nd Normal Form (2NF)
✅ All non-key attributes fully depend on the primary key.  
✅ Example: `score` in `performance_evals` depends on `eval_id`, not partial key.

### 3rd Normal Form (3NF)
✅ No transitive dependencies.  
✅ Example: `company_name` is in `companies` table, not duplicated in `cadets`.  
✅ Summary tables are intentionally denormalized for performance but clearly marked as analytics tables.

---

## Data Integrity Rules

### Foreign Key Constraints
- `cadets.company_id` → `companies.company_id` ON DELETE SET NULL
- `service_records.cadet_id` → `cadets.cadet_id` ON DELETE CASCADE
- `service_records.module_id` → `training_modules.module_id` ON DELETE CASCADE
- `performance_evals.record_id` → `service_records.record_id` ON DELETE CASCADE
- `muster_rolls.cadet_id` → `cadets.cadet_id` ON DELETE CASCADE

### Check Constraints
- Scores: 0-100 range
- Dates: `completion_date` >= `start_date`
- Status values: Enum-like validation
- GPA: 0.00-4.00 range

### Unique Constraints
- `cadets.service_number`
- `cadets.email`
- `training_modules.module_code`
- `companies.company_code`

### Indexes (Performance)
```sql
CREATE INDEX idx_service_records_cadet ON service_records(cadet_id);
CREATE INDEX idx_service_records_module ON service_records(module_id);
CREATE INDEX idx_performance_evals_record ON performance_evals(record_id);
CREATE INDEX idx_muster_rolls_cadet_date ON muster_rolls(cadet_id, muster_date);
CREATE INDEX idx_attrition_risk_level ON attrition_risk(risk_level);
```

---

## ETL Pipeline Considerations

### Data Sources
- **CSV**: Bulk cadet imports, historical records
- **JSON**: API feeds for risk assessments, external systems
- **Excel**: Training module catalogs, company rosters

### Transformation Logic
1. **Clean**: Remove duplicates, standardize ranks/statuses
2. **Validate**: Email formats, date ranges, score boundaries
3. **Enrich**: Calculate GPA, attendance rates
4. **Aggregate**: Populate `cadet_performance_summary` nightly

### Scheduled Jobs
- **Daily**: Update `muster_rolls`, refresh `cadet_performance_summary`
- **Weekly**: Recalculate `attrition_risk` scores
- **Monthly**: Archive completed service records

---

## Key SQL Queries (Examples)

### High-Risk Cadets
```sql
SELECT c.service_number, c.first_name, c.last_name, ar.risk_level, ar.risk_score
FROM cadets c
JOIN attrition_risk ar ON c.cadet_id = ar.cadet_id
WHERE ar.risk_level IN ('High', 'Critical')
ORDER BY ar.risk_score DESC;
```

### Top Performers by Department
```sql
SELECT c.service_number, cps.avg_cyber_score, cps.performance_tier
FROM cadets c
JOIN cadet_performance_summary cps ON c.cadet_id = cps.cadet_id
WHERE cps.avg_cyber_score >= 90
ORDER BY cps.avg_cyber_score DESC
LIMIT 10;
```

### Attendance Below Threshold
```sql
SELECT c.service_number, cps.attendance_rate
FROM cadets c
JOIN cadet_performance_summary cps ON c.cadet_id = cps.cadet_id
WHERE cps.attendance_rate < 75
  AND c.status = 'Active';
```

---

## Deployment Notes

### Cloud Database Options
- **Render** (Free PostgreSQL tier)
- **Railway** (Free trial)
- **Supabase** (PostgreSQL with built-in APIs)

### Environment Variables
```
DB_HOST=your-host.render.com
DB_PORT=5432
DB_NAME=elite_defense_academy
DB_USER=academy_admin
DB_PASSWORD=<secure_password>
```

### Security
- Use role-based access control (RBAC)
- Encrypt sensitive data (email, service_number)
- Implement row-level security for company-based access

---

## Future Enhancements
- Add `disciplinary_actions` table for conduct tracking
- Implement `certifications` table for specialized qualifications
- Create `training_schedules` for session planning
- Build `deployment_history` for post-graduation tracking