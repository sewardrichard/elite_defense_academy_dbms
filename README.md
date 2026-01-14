# Elite Defense Academy DBMS

## Project Overview
The **Elite Defense Academy Dictionary Management System (DBMS)** is a specialized Student Record Management System designed for military academy operations. It manages the full lifecycle of a recruit's training, including:
- **Student Profiles**: Personal details, rank, and company assignment.
- **Academic Enrollment**: Course registration across multiple departments (Tactics, Engineering, Leadership, etc.).
- **Performance Tracking**: Detailed grading for exams, quizzes, and assignments.
- **Attendance Monitoring**: Daily muster rolls and attendance rate calculations.
- **Analytics**: Automated GPA calculation, attrition risk assessment, and performance summaries.

## Project Lifecycle & Completion Checklist

This project was executed in a phased approach, migrating from initial design to a fully deployed application.

### Phase 1: Requirements & Schema Design
- [x] Identified key entities: Students, Companies, Courses, Enrollments, Grades, Attendance.
- [x] Designed Entity-Relationship Diagram (ERD).
- [x] Normalized schema to 3NF.
- [x] Defined data integrity rules and constraints.

### Phase 2: Database Implementation
- [x] Configured PostgreSQL database (`student_records_db`).
- [x] Implemented schema with tables, keys, and constraints (`database/02_create_tables.sql`).
- [x] Created performance indexes (`database/03_create_indexes.sql`).
- [x] Configured user permissions (`database/04_user_permissions.sql`).

### Phase 3: Data Generation & ETL
- [x] Developed Python scripts for synthetic data generation (`scripts/generate_sample_data.py`).
- [x] Built ETL pipeline for ensuring data quality (`scripts/etl_pipeline.py`).
- [x] Loaded 500+ students, 30+ courses, and thousands of grade/attendance records.

### Phase 4: Advanced Logic & Reporting
- [x] developed SQL views for rosters and reports (`database/10_views_reports.sql`).
- [x] Implemented stored procedures for business logic (`database/11_stored_procs.sql`).
- [x] Created complex queries for identifying at-risk students.

### Phase 5: Application Development
- [x] Built CLI for interacting with the database (`main.py`).
- [x] Implemented features: Add Student, Enroll, Grade, Mark Attendance.
- [x] Integrated PDF and CSV reporting features.
- [x] Added robust error handling and CLI arguments.

### Phase 6: Testing & Deployment
- [x] Validated data integrity and constraints.
- [x] Consolidated project structure for professional deployment.
- [x] Verified all workflows and generated documentation.

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.8+
- PostgreSQL
- Dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Database Initialization
Ensure PostgreSQL is running and your `.env` file is configured (see `.env.example`).
Run the SQL scripts in order:

```bash
# Example using psql (adjust user/db as needed)
psql -U your_user -d student_records_db -f database/01_database_init.sql
psql -U your_user -d student_records_db -f database/02_create_tables.sql
psql -U your_user -d student_records_db -f database/03_create_indexes.sql
psql -U your_user -d student_records_db -f database/04_user_permissions.sql
psql -U your_user -d student_records_db -f database/10_views_reports.sql
psql -U your_user -d student_records_db -f database/11_stored_procs.sql
psql -U your_user -d student_records_db -f database/12_grants.sql
```

### 3. Data Generation (Optional)
To populate the database with sample data:

```bash
# Generate fresh sample data (clears existing data)
python scripts/generate_sample_data.py --clean

# Or run the ETL pipeline to load from raw files
python scripts/etl_pipeline.py
```

### 4. Application Usage (CLI)
The application is accessed via the command line interface from the project root.

**Run the CLI help:**
```bash
python main.py --help
```

**Common Commands:**

*   **Add a Student**:
    ```bash
    python main.py add-student --first "John" --last "Doe" --email "john.doe@example.com" --dob "2000-01-01" --gender "Male"
    ```

*   **Enroll**:
    ```bash
    python main.py enroll --email "john.doe@example.com" --course "TAC-101" --date "2023-01-15"
    ```

*   **Mark Attendance**:
    ```bash
    python main.py attendance --email "john.doe@example.com" --course "TAC-101" --status "Present"
    ```

*   **Generate Report**:
    ```bash
    # Generates specific report in the /reports folder
    python main.py report --type roster --format pdf
    ```

### 5. Running Tests
Run the unit and integration tests to verify system stability:

```bash
python -m unittest discover tests
```

---

## Directory Structure
- `/src`: Core application logic (controllers, models, utils).
- `/database`: SQL scripts for schema, views, and migrations.
- `/scripts`: Data generation and ETL utilities.
- `/tests`: Unit and integration tests.
- `/reports`: Generated output files.
- `/docs`: Project documentation and archival records.
