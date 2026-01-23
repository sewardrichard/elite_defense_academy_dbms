# Elite Defense Academy DBMS

**Technical Documentation for Student Records Management System**

A PostgreSQL-based database management system engineered for military academy operations. Implements normalized schema design (3NF), automated ETL pipeline, stored procedures for business logic, and interactive Python CLI with comprehensive reporting capabilities.

---

## Table of Contents

- [Database Schema](#database-schema)
- [Sample Data Generation](#sample-data-generation)
- [ETL Pipeline](#etl-pipeline)
- [SQL & Procedures](#sql--procedures)
- [Python CLI](#python-cli)
- [Local Setup](#local-setup)
- [Remote Setup (Render)](#remote-setup-render)
- [Dependency Audit](#dependency-audit)

---

## Database Schema

### Entity-Relationship Model

The database implements an 8-table normalized schema optimized for military academy workflows:

**Core Tables:**
- `companies` - Organizational units (platoons, companies)
- `students` - Personnel records with service numbers
- `courses` - Training curriculum catalog
- `enrollments` - Student-course registrations
- `grades` - Individual assessment results
- `attendance` - Daily muster rolls

**Analytics Tables:**
- `performance_summary` - Pre-calculated GPA and metrics
- `attrition_risk` - Dropout risk assessments

**ERD Diagram:**

![ERD Diagram](./docs/week_1/ERD.png)

### Key Constraints

| Constraint Type | Implementation |
|-----------------|----------------|
| **Referential Integrity** | `ON DELETE CASCADE` for student data, `RESTRICT` for courses |
| **Unique Constraints** | Service numbers, emails, enrollment combinations |
| **Check Constraints** | Gender values, status enums, score ranges (0-100), GPA scale (0-4.0) |
| **Triggers** | Auto-update `updated_at` timestamps |

### Schema Files

```
database/
├── 01_database_init.sql       # Database creation
├── 02_create_tables.sql       # Table definitions with constraints
├── 03_create_indexes.sql      # Performance indexes
├── 04_user_permissions.sql    # Role-based access control
├── 10_views_reports.sql       # Reporting views
├── 11_stored_procs.sql        # Business logic procedures
└── 12_grants.sql              # Permission grants
```

---

## Sample Data Generation

### Script: `scripts/generate_sample_data.py`

**Purpose:** Generates realistic synthetic data using Faker library for testing and demonstration.

**Implementation Logic:**
1. **Companies:** Creates 10 military units with commanding officers
2. **Students:** Generates 500+ cadets with service numbers, demographics, and rank assignments
3. **Courses:** Populates 30+ courses across departments (Tactics, Weapons, Engineering, Leadership)
4. **Enrollments:** Randomly assigns students to 2-5 courses with realistic date ranges
5. **Grades:** Creates weighted assessments (Exams: 0.4, Quizzes: 0.2, Practicals: 0.3, etc.)
6. **Attendance:** Generates daily muster records with status distribution (90% Present, 5% Absent, 3% Late, 2% AWOL)
7. **Performance Summaries:** Computes GPA and standing for all students
8. **Attrition Risk:** Flags at-risk students based on low GPA (\<2.0) or attendance (\<70%)

**Execution:**

```bash
# Generate fresh dataset (clears existing data)
python scripts/generate_sample_data.py --clean

# Append to existing data
python scripts/generate_sample_data.py
```

**Parameters:**

| Argument | Description | Default |
|----------|-------------|---------|
| `--clean` | Drop and recreate all data | False (append mode) |

**Output:** Console logs showing record counts per table.

---

## ETL Pipeline

### Script: `scripts/etl_pipeline.py`

**Purpose:** Extract-Transform-Load pipeline for processing external raw data files into the database.

### Architecture

```
Extract → Transform → Load
  ↓         ↓          ↓
 CSV     Validate   Batch
 JSON    Clean      Insert
         Enrich     Upsert
```

### Implementation Flow

#### **Phase 1: Extract**
- Reads from `docs/data/raw/`:
  - `students_raw.csv` - Personnel records
  - `courses_catalog.json` - Course definitions
  - `grades_raw.csv` - Assessment scores
  - `attendance_raw.csv` - Muster logs
- Converts JSON to pandas DataFrame
- Validates file existence

#### **Phase 2: Transform**
Data cleaning operations:
- **Date Standardization:** Converts all date formats to `YYYY-MM-DD`
- **Email Validation:** Regex pattern matching, lowercasing, deduplication
- **Name Formatting:** Title-case conversion, first/last name split
- **GPA Calculation:** Weighted score averaging, 4.0 scale conversion
- **Attendance Categorization:** Present/Late = positive, Absent/AWOL = negative
- **Standing Determination:**
  - ≥90% → Honor Roll
  - ≥70% → Good Standing
  - \<70% → Academic Warning

#### **Phase 3: Load**
- **Batch Inserts:** Uses `psycopg2.extras.execute_batch()` for performance
- **Conflict Handling:** `ON CONFLICT DO NOTHING` for idempotency
- **Foreign Key Resolution:** Email-to-student_id mapping
- **Transaction Management:** Full rollback on error

### Raw File Generation

**Script:** `scripts/generate_raw_files.py`

Creates intentionally "messy" raw data files for ETL testing:
- Missing values
- Invalid formats
- Duplicate records
- Inconsistent casing

**Execution:**

```bash
# Generate raw files
python scripts/generate_raw_files.py

# Run ETL pipeline
python scripts/etl_pipeline.py
```

---

## SQL & Procedures

### Stored Procedures

Location: `database/11_stored_procs.sql`

| Procedure | Signature | Description |
|-----------|-----------|-------------|
| `sp_enroll_student` | `(student_id, course_id, start_date) → enrollment_id` | Enrolls student in course with duplicate prevention |
| `sp_record_grade` | `(enrollment_id, assessment_type, score, weight, date, remarks) → void` | Records grade and recalculates enrollment final_score/letter |
| `sp_mark_attendance` | `(student_id, course_id, muster_date, status, remarks) → attendance_id` | Upserts daily attendance record |
| `sp_refresh_performance_summary` | `(student_id) → void` | Recomputes GPA, attendance rate, standing for one student |
| `sp_refresh_all_performance` | `() → void` | Batch refresh for all students |

**Grade Calculation Logic:**

```sql
final_score = SUM(score × weight) / SUM(weight)

Letter Grade:
  ≥90 → A
  ≥80 → B
  ≥70 → C
  ≥60 → D
  <60 → F
```

### Views and Reports

Location: `database/10_views_reports.sql`

| View | Purpose |
|------|---------|
| `vw_transcript` | Official student transcripts (courses, grades, credits) |
| `vw_attendance_report` | Daily muster roll-up by course/date |
| `vw_low_attendance` | Students with \<70% attendance |
| `vw_course_avg_grades` | Course-level grade distributions (A/B/C/D-F buckets) |
| `vw_course_enrollment_stats` | Enrollment counts, pass/fail rates |

### Key Queries

**Top Students by GPA:**
```sql
SELECT service_number, first_name, last_name, gpa
FROM students s
JOIN performance_summary ps ON s.student_id = ps.student_id
WHERE gpa IS NOT NULL
ORDER BY gpa DESC
LIMIT 10;
```

**At-Risk Students:**
```sql
SELECT s.service_number, s.first_name, s.last_name, ar.risk_level, ar.contributing_factors
FROM attrition_risk ar
JOIN students s ON s.student_id = ar.student_id
WHERE risk_level IN ('High', 'Critical')
ORDER BY risk_score DESC;
```

---

## Python CLI

### Entry Point

**File:** `main.py`

```bash
python main.py
```

### Architecture

```
main.py
  └─> src/cli.py (Main Menu)
       ├── Student Management (CRUD)
       ├── Course Management (CRUD + Enrollment/Grading)
       ├── Reports (PDF/CSV)
       └── Stored Procedures (Views & Analytics)
```

### Interactive Menu System

The CLI is organized into four main functional areas:

#### 1. Student Management
Dedicated module for managing student personnel records.

- **Add Student:** Interactive wizard for creating new profiles (validates email, DOB, rank).
- **List Students:** Paginated view (10 per page) with search functionality.
- **Update/Delete:** Modify or remove student records via email lookup or list selection.

#### 2. Course Management & Academic Operations
Central hub for all academic workflows. Users first select a course from the global catalog to access specific operations for that course.

**Course-Level Actions:**
1.  **View Enrolled Students:** Roster with rank and email.
2.  **Enroll Student:** Add a student to the course (prevent duplicates).
3.  **Unenroll Student:** Remove a student from the roster.
4.  **Record Grade:**
    *   Select student from roster
    *   Choose assessment type (Exam, Quiz, Practical, etc.)
    *   Enter score (0-100) and optional remarks
    *   *Features automatic grade re-calculation*
5.  **Mark Attendance:**
    *   Select student
    *   Log status (Present, Absent, Late, AWOL, Excused)
6.  **Update/Delete Course:** Modify credits/dept or remove course entirely.

#### 3. Generate Reports
Producing official documentation and high-level summaries.

- **Official Transcript:** Generates PDF transcript for a selected student.
- **Company Readiness Ledger:** Company-level performance metrics.

#### 4. Stored Procedures & Views
Direct access to advanced database analytics.

- **View Students in Course:** Raw roster view.
- **Course Average Grades:** Analytics on pass rates and grade distributions (Paginated).
- **Low Attendance Risk:** List of students below 75% attendance threshold.
- **Top Student Ranking:** Dynamic ranking by GPA (User defines 'N').
- **Enrollment Stats:** Pass/Fail/Withdrawal counts per course.

---

### Navigation & UX Features

- **Pagination:** Large lists (students, courses) are split into pages.
- **Search:** Filter lists by name, code, or ID (`[s] Search`).
- **Persistent Workflows:** Grading and Attendance flows loop to allow rapid data entry for multiple students.
- **Validation:** email regex, date formats, and score ranges are strictly enforced.
- **Rich Output:** Uses `rich` library for formatted tables, panels, and colored output.

**Alternative TUI:**

```bash
python tui.py
```

Launches Textual-based Terminal User Interface (advanced interactive mode).

---

## Local Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd elite_defense_academy_dbms
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create `.env` file in project root:

```env
DB_NAME=student_records_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Reference: `.env.example`

### Step 4: Initialize Database

**Option A: Using psql**

```bash
psql -U postgres -f database/01_database_init.sql
psql -U postgres -d student_records_db -f database/02_create_tables.sql
psql -U postgres -d student_records_db -f database/03_create_indexes.sql
psql -U postgres -d student_records_db -f database/04_user_permissions.sql
psql -U postgres -d student_records_db -f database/10_views_reports.sql
psql -U postgres -d student_records_db -f database/11_stored_procs.sql
psql -U postgres -d student_records_db -f database/12_grants.sql
```

**Option B: Single Command**

```bash
for file in database/{01,02,03,04,10,11,12}*.sql; do
  psql -U postgres -d student_records_db -f "$file"
done
```

### Step 5: Generate Sample Data

```bash
python scripts/generate_sample_data.py --clean
```

**Expected Output:**
```
Created 10 companies.
Created 500 students.
Created 30 courses.
Created 1500 enrollments.
Created 4500 grades.
Created 12000 attendance records.
Performance summaries refreshed for 500 students.
Attrition risk assessments created for 75 students.
```

### Step 6: Run CLI

```bash
python main.py
```

### Optional: Generate ETL Source Files

```bash
python scripts/generate_raw_files.py
python scripts/etl_pipeline.py
```

---

## Remote Setup (Render)

### Deployment Environment

**Platform:** [Render.com](https://render.com) PostgreSQL

**Configuration:**
- Plan: Free Tier (sufficient for 500+ students)
- Version: PostgreSQL 16
- Region: Choose nearest to your location

### Step 1: Create PostgreSQL Instance

1. Navigate to Render Dashboard → **New** → **PostgreSQL**
2. Name: `elite-defense-academy-db`
3. Database: `student_records_db`
4. User: Auto-generated
5. Plan: Free
6. Click **Create Database**

### Step 2: Retrieve Connection String

From database dashboard, copy:
- **Internal Database URL** (use this if app is on Render)
- **External Database URL** (use for local psql)

Format:
```
postgres://user:password@host:port/database
```

Parse into `.env`:
```env
DB_HOST=dpg-xxxxxx-a.oregon-postgres.render.com
DB_PORT=5432
DB_USER=student_records_db_user
DB_PASSWORD=xxxxxxxxxxxxx
DB_NAME=student_records_db
```

### Step 3: Execute Schema Scripts

**From Local Machine:**

```bash
# Set environment variable
export DATABASE_URL="postgres://user:password@host:port/database"

# Run scripts
psql $DATABASE_URL -f database/02_create_tables.sql
psql $DATABASE_URL -f database/03_create_indexes.sql
psql $DATABASE_URL -f database/04_user_permissions.sql
psql $DATABASE_URL -f database/10_views_reports.sql
psql $DATABASE_URL -f database/11_stored_procs.sql
psql $DATABASE_URL -f database/12_grants.sql
```



### Step 4: Populate Data

**Update `.env` for Render:**

```env
DB_HOST=dpg-xxxxxx-a.oregon-postgres.render.com
DB_PORT=5432
DB_USER=student_records_db_user
DB_PASSWORD=xxxxxxxxxxxxx
DB_NAME=student_records_db
```

**Run Data Generator:**

```bash
python scripts/generate_sample_data.py --clean
```

**Verify Data:**

```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM students;"
```

Expected: `500`

### Step 5: Run CLI Against Render

CLI automatically uses `.env` configuration. No code changes needed.

```bash
python main.py
```

All operations (CRUD, reports) now execute against Render database.

### Render Execution Notes

**Connection Limits:**
- Free tier: 100 connections
- CLI uses connection pooling (1-2 connections)

**SSL:**
- Render enforces SSL by default
- `psycopg2` auto-handles SSL negotiation

**Idle Disconnect:**
- Free databases sleep after 15 minutes inactivity
- First query after sleep may take 30-60 seconds
- CLI will retry connection automatically

**Backups:**
- Render does NOT backup free tier databases
- Recommendation: Export data weekly:
  ```bash
  pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
  ```

---

## Dependency Audit

### Complete Dependency Matrix

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| `faker` | 40.1.0 | Synthetic data generation | `scripts/generate_sample_data.py`, `scripts/generate_raw_files.py` |
| `psycopg2-binary` | 2.9.9 | PostgreSQL adapter | `src/database.py`, `scripts/etl_pipeline.py`, `scripts/generate_sample_data.py` |
| `pandas` | 2.2.0 | ETL data transformation | `scripts/etl_pipeline.py` |
| `openpyxl` | 3.1.2 | Excel I/O (pandas backend) | Indirect (pandas dependency) |
| `textual` | 0.79.1 | Terminal UI framework | `src/tui_app.py`, `tui.py` |
| `reportlab` | ≥3.6.12 | PDF generation | `src/reports.py` (all PDF functions) |
| `rich` | ≥13.0.0 | Console formatting (tables, panels) | `src/cli.py`, `tests/tables.py` |

**Standard Library Imports:** No additional third-party libraries required.

---

## Testing

### Run Unit Tests

```bash
python -m unittest discover tests
```

### Test Coverage

- SQL integrity constraints (`tests/test_sql_integrity.py`)
- CLI validation functions (`tests/test_cli.py`)
- Database connection handling

---

## Project Structure

```
elite_defense_academy_dbms/
├── database/               # SQL schema and migrations
│   ├── 01_database_init.sql
│   ├── 02_create_tables.sql
│   ├── 03_create_indexes.sql
│   ├── 04_user_permissions.sql
│   ├── 10_views_reports.sql
│   ├── 11_stored_procs.sql
│   └── 12_grants.sql
├── docs/                   # Documentation and archives
│   ├── data/raw/          # ETL source files
│   └── week_*/            # Project deliverables by phase
├── scripts/               # Data generation and ETL
│   ├── generate_sample_data.py
│   ├── generate_raw_files.py
│   └── etl_pipeline.py
├── src/                   # Application source
│   ├── cli.py            # Main CLI loop
│   ├── controllers.py    # CRUD operations
│   ├── database.py       # Connection management
│   ├── reports.py        # Report generation (PDF/CSV)
│   ├── tui_app.py        # Textual TUI
│   └── utils.py          # Validation helpers
├── tests/                 # Unit and integration tests
├── reports/               # Generated output files
├── main.py                # CLI entry point
├── tui.py                 # TUI entry point
├── requirements.txt       # Python dependencies
└── .env                   # Environment configuration (git-ignored)
```

---

## License

This project is for educational purposes.

## Author

Built as a comprehensive database systems project demonstrating schema design, ETL architecture, stored procedure development, and application integration.
