# Elite Defense Academy - SQL Scripts

This directory contains the SQL scripts for setting up the **Student Records Management System (SRMS)** database.

## Scripts Overview

| Script | Purpose |
|:-------|:--------|
| `01_database_init.sql` | Creates the `student_records_db` database |
| `02_create_tables.sql` | Creates all 8 tables with constraints |
| `03_create_indexes.sql` | Adds performance indexes |
| `04_user_permissions.sql` | Sets up roles and users |

## Quick Start

### Prerequisites
- PostgreSQL 12+ installed and running
- Access to `psql` command-line tool
- Superuser privileges (postgres user)

### Installation Steps

```bash
# 1. Create the database (run as postgres superuser)
psql -U postgres -f 01_database_init.sql

# 2. Create all tables (connect to student_records_db)
psql -U postgres -d student_records_db -f 02_create_tables.sql

# 3. Create performance indexes
psql -U postgres -d student_records_db -f 03_create_indexes.sql

# 4. Set up users and permissions
psql -U postgres -d student_records_db -f 04_user_permissions.sql
```

> ⚠️ **IMPORTANT**: Change all default passwords in `04_user_permissions.sql` before running in production!

## Database Schema

### Tables (8 Total)

```
companies ─────────┬──> students ─────┬──> enrollments ──> grades
                   │                  │
                   │                  ├──> attendance
                   │                  │
                   │                  ├──> performance_summary
                   │                  │
courses ───────────┴──────────────────┴──> attrition_risk
```

### Relationships

| Parent | Child | Relationship | ON DELETE |
|:-------|:------|:-------------|:----------|
| companies | students | 1:N | RESTRICT |
| students | enrollments | 1:N | CASCADE |
| students | attendance | 1:N | CASCADE |
| students | performance_summary | 1:1 | CASCADE |
| students | attrition_risk | 1:N | CASCADE |
| courses | enrollments | 1:N | RESTRICT |
| courses | attendance | 1:N | RESTRICT |
| enrollments | grades | 1:N | CASCADE |

## Verification

After running all scripts, verify the setup:

```sql
-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Expected output:
-- attendance
-- attrition_risk
-- companies
-- courses
-- enrollments
-- grades
-- performance_summary
-- students
```

## User Roles

| Role | Access Level |
|:-----|:-------------|
| `srms_admin` | Full access to all operations |
| `srms_instructor` | Read all, Write enrollments/grades/attendance |
| `srms_readonly` | Read-only for analytics |

---

*Created for Week 2 - Phase 2: Database Setup & Table Creation*
