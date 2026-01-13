# Elite Defense Academy — Student Records Management System

> 🎖️ A PostgreSQL-backed student records platform for cadet training, performance analytics, and attrition risk insights.

---

## 📋 Project Overview

The **Elite Defense Academy SRMS** manages the cadet lifecycle end to end:

- **Centralized Personnel Records** — Companies, cadets, and assignments
- **Training Catalog** — Courses with credits, difficulty, departments
- **Performance Tracking** — Assessments, weighted grades, GPA, transcripts
- **Attendance Monitoring** — Daily muster with Present/Absent/Late/AWOL
- **Analytics** — Attrition risk and performance summaries

---

## 🗂️ Project Structure

```
elite_defense_academy_dbms/
├── README.md
├── setup_db_user.sql          # Simple single-user grants script
├── .env.example               # DB connection placeholders (do NOT commit real secrets)
└── docs/
    ├── week_1/                # Business requirements
    ├── week_2/
    │   └── sql/               # 01–04: DB init, tables, indexes
    ├── week_3/                # ERD + sample data/ETL scripts (completed)
    └── week_4/
        └── sql/               # 10–12: advanced views, procs, grants
```

---

## 🗺️ Project Roadmap (current state)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **Phase 1** | Business Requirements | ✅ Complete |
| **Phase 2** | ERD | ✅ Complete |
| **Phase 3** | Database Schema (Week 2 SQL) | ✅ Complete |
| **Phase 4** | ETL & Sample Data (Week 3 scripts) | ✅ Complete |
| **Phase 5** | Advanced SQL Views & Procs (Week 4) | ✅ Complete |
| **Phase 6** | Application Interface (CLI) | ⏳ In progress |
| **Phase 7** | Deployment & Documentation | ⏳ Pending |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Database** | PostgreSQL 15+ |
| **Scripts** | psql + SQL (DDL/DCL/PLpgSQL) |
| **Automation** | PowerShell / shell (manual execution) |

---

## 🚀 Getting Started (Database Setup & Data Load)

Prereqs
- PostgreSQL running; `psql` available.
- Clone repo and stay at root.
- Copy `.env.example` → `.env`, set strong password (file is gitignored).

1) Create the database (superuser)
```bash
psql -U postgres -f docs/week_2/sql/01_database_init.sql
```

2) Create schema and indexes
```bash
psql -U postgres -d student_records_db -f docs/week_2/sql/02_create_tables.sql
psql -U postgres -d student_records_db -f docs/week_2/sql/03_create_indexes.sql
```

3) Create a single application user (simple grants)
Run with your chosen password (do not commit it):
```bash
psql -U postgres -d student_records_db \
  -v srms_user_pwd="your_strong_password" \
  -f docs/week_2/sql/04_user_permissions.sql
```
Then set your `.env` (for your app/runtime):
```
DB_USER=srms_user
DB_PASSWORD=your_strong_password
DB_NAME=student_records_db
DB_HOST=localhost
DB_PORT=5432
```

4) Generate raw files, sample data, and run ETL (Week 3 — required)
```bash
# Activate your venv with Faker/psycopg2 installed, then:
python docs/week_3/scripts/generate_raw_files.py     # builds raw CSV/JSON inputs
python docs/week_3/scripts/generate_sample_data.py   # populates DB: companies, students, enrollments, grades, attendance
python docs/week_3/scripts/etl_pipeline.py           # runs ETL/cleaning/loading into DB
```

5) Add advanced views, reports, and procs (Week 4 — required)
```bash
psql -U postgres -d student_records_db -f docs/week_4/sql/10_views_reports.sql
psql -U postgres -d student_records_db -f docs/week_4/sql/11_stored_procs.sql
psql -U postgres -d student_records_db -f docs/week_4/sql/12_grants.sql
```

6) Quick checks (after Week 4)
```sql
SELECT * FROM vw_course_students WHERE course_code = 'TAC-101';
SELECT course_code, avg_score, median_score FROM vw_course_avg_grades;
SELECT * FROM vw_low_attendance ORDER BY attendance_rate;
SELECT * FROM vw_top_gpa ORDER BY gpa_rank;
SELECT * FROM vw_course_enrollment_stats;
```

Notes
- `.env` is ignored by Git; keep real passwords there.
- Add `-h <host> -p <port>` to `psql` commands if not local.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Week 1 BRD](docs/week_1/business_requirements.md) | Entities, requirements, and use cases |
| Week 2 SQL | Core DDL and indexes (`docs/week_2/sql/01-03_*.sql`) |
| Week 4 SQL | Views, reports, functions, grants (`docs/week_4/sql/10-12_*.sql`) |

---

## 📝 License

This project is part of the Elite Defense Academy educational initiative.

---

> **Classification:** UNCLASSIFIED  
> **Last Updated:** 2026-01-13
