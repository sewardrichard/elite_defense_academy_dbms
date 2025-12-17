# Business Requirements Document
## Elite Defense Academy — Student Records Management System (SRMS)

| **Document Version** | 1.0 |
|----------------------|-----|
| **Date** | 2025-12-17 |
| **Status** | Draft |
| **Security Classification** | UNCLASSIFIED |
| **Author** | Elite Defense Academy Project Team |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [Business Objectives](#3-business-objectives)
4. [Stakeholder Analysis](#4-stakeholder-analysis)
5. [Core Entity Requirements](#5-core-entity-requirements)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Business Rules & Constraints](#8-business-rules--constraints)
9. [Use Cases](#9-use-cases)
10. [Data Dictionary](#10-data-dictionary)
11. [Appendix](#11-appendix)

---

## 1. Executive Summary

### 1.1 Purpose

This document defines the comprehensive business requirements for the **Elite Defense Academy Student Records Management System (SRMS)**—a database-driven solution designed to manage cadet training, academic performance, attendance, and predictive attrition analytics for a military defense training institution.

### 1.2 Problem Statement

The Elite Defense Academy currently lacks a centralized, normalized database system to:
- Track cadet enrollment, training progress, and academic performance
- Monitor daily attendance (muster rolls) across training modules
- Identify at-risk cadets through data-driven attrition analysis
- Generate performance reports for commanding officers and administrators

### 1.3 Proposed Solution

Implement a PostgreSQL-based relational database system that:
- Maintains **normalized (3NF)** personnel and training records
- Provides real-time attendance and performance dashboards
- Integrates AI/ML pipelines for attrition risk prediction
- Enables comprehensive reporting at cadet, company, and academy levels

### 1.4 Key Benefits

| Benefit | Description |
|---------|-------------|
| **Centralized Data** | Single source of truth for all cadet records |
| **Data Integrity** | Enforced through constraints, relationships, and normalization |
| **Predictive Insights** | Early identification of at-risk cadets for intervention |
| **Operational Efficiency** | Automated attendance tracking and grade calculations |
| **Compliance** | Complete audit trails and security controls |

---

## 2. Project Overview

### 2.1 System Name

**Elite Defense Academy — Student Records Management System (SRMS)**

### 2.2 System Description

The SRMS is a comprehensive database management system designed to handle all aspects of cadet lifecycle management within a military defense training academy. The system tracks personnel from enrollment through graduation or discharge, capturing training performance, attendance, and behavioral data to support operational and strategic decision-making.

### 2.3 Scope

#### In Scope
- Cadet personnel record management
- Company/unit organizational structure
- Training module catalog and enrollment
- Performance evaluations and grading
- Attendance/muster roll tracking
- Performance summary analytics
- Attrition risk prediction
- Reporting and data export capabilities

#### Out of Scope
- Financial/billing systems
- External API integrations (Phase 1)
- Mobile application development
- Physical access control systems
- Weapons/equipment inventory

### 2.4 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        ELITE DEFENSE ACADEMY                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│   │  Admissions  │    │  Training    │    │  Analytics   │      │
│   │    Staff     │    │  Officers    │    │    Team      │      │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│          │                   │                   │               │
│          ▼                   ▼                   ▼               │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                         SRMS                            │    │
│   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌───────┐ │    │
│   │  │ Cadets │ │Training│ │ Grades │ │Attend. │ │ Risk  │ │    │
│   │  │        │ │Modules │ │        │ │        │ │ AI/ML │ │    │
│   │  └────────┘ └────────┘ └────────┘ └────────┘ └───────┘ │    │
│   └────────────────────────────────────────────────────────┘    │
│          │                   │                   │               │
│          ▼                   ▼                   ▼               │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│   │   Reports    │    │  Dashboards  │    │  Alerts &    │      │
│   │              │    │              │    │  Predictions │      │
│   └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Business Objectives

### 3.1 Primary Objectives

| ID | Objective | Success Metric |
|----|-----------|----------------|
| **BO-01** | Centralize cadet records management | 100% of active cadets in system |
| **BO-02** | Track training enrollments and completions | Real-time enrollment status visibility |
| **BO-03** | Automate grade calculations and GPA tracking | <1 hour to generate performance reports |
| **BO-04** | Monitor attendance compliance | Daily attendance rates available by 0800 |
| **BO-05** | Predict attrition risk | 80% accuracy in identifying at-risk cadets |
| **BO-06** | Enable unit-level performance comparisons | Company rankings updated weekly |

### 3.2 Strategic Alignment

The SRMS directly supports the Academy's mission to:
- **Train Elite Personnel**: By tracking and optimizing training outcomes
- **Maximize Retention**: Through early intervention for at-risk cadets
- **Maintain Accountability**: Via comprehensive attendance and performance tracking
- **Data-Driven Decisions**: Enabling leadership with actionable analytics

---

## 4. Stakeholder Analysis

### 4.1 Stakeholder Matrix

| Stakeholder | Role | Interest/Need | Access Level |
|-------------|------|---------------|--------------|
| **Academy Commandant** | Executive Sponsor | High-level analytics, retention rates | Dashboard (Read) |
| **Commanding Officers (COs)** | Unit Leaders | Company performance, cadet issues | Company-level (Read/Write) |
| **Training Officers** | Instructors | Module grades, attendance | Module-level (Read/Write) |
| **Admissions Staff** | Data Entry | Cadet enrollment, status updates | Cadet records (Read/Write) |
| **Data Analysts** | Analytics Team | ETL, reporting, ML models | Full database (Read) |
| **System Administrators** | IT Support | Database maintenance, security | Full access (Admin) |
| **Cadets** | End Users | Personal records, grades | Self-service (Read) |

### 4.2 Key Decision Makers

- **Academy Commandant** — Final approval on system capabilities and reports
- **Chief Data Officer** — Database architecture and analytics strategy
- **Head of Training** — Module structure and grading policies

---

## 5. Core Entity Requirements

This section documents the business requirements for each entity within the SRMS.

---

### 5.1 COMPANIES (Organizational Units)

> **Business Purpose**: Segment cadets into tactical units for organizational structure, unit-level reporting, and competitive performance tracking.

#### 5.1.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **CO-01** | Each company must have a unique designation code (e.g., "A-CO", "B-CO") | High |
| **CO-02** | Each company must have an assigned Commanding Officer | High |
| **CO-03** | Maximum strength (capacity) must be defined per company | Medium |
| **CO-04** | Company full names must be meaningful (e.g., "Alpha Company") | Medium |
| **CO-05** | System must support 5+ companies initially, with capacity to expand | Low |

#### 5.1.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Company ID | Unique identifier | Integer (Auto) | Primary Key |
| Company Code | Unit designation | VARCHAR(10) | Unique, NOT NULL |
| Company Name | Full unit name | VARCHAR(100) | NOT NULL |
| Commanding Officer | CO name | VARCHAR(100) | — |
| Max Strength | Personnel capacity | Integer | > 0 |

#### 5.1.3 Business Rules

- A company can have **0 to many** cadets assigned
- Company codes must follow pattern: `{Letter}-CO` (e.g., A-CO, B-CO)
- Commanding Officer can be updated without affecting cadet assignments

---

### 5.2 CADETS (Personnel Records)

> **Business Purpose**: Core personnel records for all trainees, capturing personal information, rank progression, unit assignment, and current service status.

#### 5.2.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **CA-01** | Every cadet must have a unique service number | High |
| **CA-02** | Personal details (name, DOB, email) are required at enrollment | High |
| **CA-03** | Each cadet must be assigned to exactly one company | High |
| **CA-04** | Cadet rank must be tracked and updatable | High |
| **CA-05** | Status changes must be captured (Active, Graduated, Discharged, Medical Leave) | High |
| **CA-06** | Enrollment date must be recorded for all cadets | Medium |
| **CA-07** | Age at enrollment must be between 18 and 24 years | Medium |
| **CA-08** | Each cadet must have a unique email address | Medium |
| **CA-09** | Full audit trail (created/updated timestamps) must be maintained | Medium |

#### 5.2.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Cadet ID | Unique identifier | Integer (Auto) | Primary Key |
| Service Number | Official ID | VARCHAR(20) | Unique, NOT NULL |
| First Name | Given name | VARCHAR(50) | NOT NULL |
| Last Name | Family name | VARCHAR(50) | NOT NULL |
| Email | Official email | VARCHAR(100) | Unique, NOT NULL |
| Date of Birth | Birth date | DATE | NOT NULL |
| Enrollment Date | Academy entry | DATE | NOT NULL |
| Rank | Military rank | VARCHAR(20) | Enum values |
| Company ID | Unit assignment | Integer | FK → Companies |
| Status | Service status | VARCHAR(20) | Enum values |
| Created At | Record creation | TIMESTAMP | Auto-generated |
| Updated At | Last modification | TIMESTAMP | Auto-updated |

#### 5.2.3 Business Rules

- **Service Number Format**: `SN-YYYY-NNN` (e.g., SN-2025-001)
- **Email Format**: `{firstname.lastname}@elite.mil`
- **Valid Ranks**: Recruit → Private → Corporal → Sergeant
- **Valid Statuses**: Active, Graduated, Discharged, Medical Leave
- **Rank Progression**: Must follow hierarchical order (no skipping ranks)
- **Status Transitions**:
  - Active → Graduated | Discharged | Medical Leave
  - Medical Leave → Active | Discharged
  - Graduated/Discharged → No further transitions (terminal states)

---

### 5.3 TRAINING MODULES (Course Catalog)

> **Business Purpose**: Define the training curriculum catalog with course codes, departments, credit values, and difficulty classifications.

#### 5.3.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **TM-01** | Each module must have a unique course code | High |
| **TM-02** | Modules must be categorized by department | High |
| **TM-03** | Credit value must be assigned to each module | High |
| **TM-04** | Difficulty level must be classified | Medium |
| **TM-05** | Expected number of sessions must be defined | Medium |
| **TM-06** | Module names must be descriptive and unique | Medium |

#### 5.3.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Module ID | Unique identifier | Integer (Auto) | Primary Key |
| Module Code | Course code | VARCHAR(15) | Unique, NOT NULL |
| Name | Module title | VARCHAR(100) | NOT NULL |
| Credits | Credit hours | Integer | > 0, NOT NULL |
| Department | Training category | VARCHAR(30) | Enum values |
| Difficulty Level | Complexity tier | VARCHAR(20) | Enum values |
| Total Sessions | Expected class count | Integer | > 0 |

#### 5.3.3 Business Rules

- **Module Code Format**: `{DEPT}-{NNN}` (e.g., CYB-101, TAC-201)
- **Valid Departments**: Cyber, Physical, Strategic, Tactical, Medical
- **Valid Difficulty Levels**: Basic, Advanced, Elite
- **Credit Range**: 1–6 credits per module
- **Elite modules** require Basic prerequisites (enforced by enrollment, not DB)

---

### 5.4 SERVICE RECORDS (Enrollments)

> **Business Purpose**: Track cadet enrollments in training modules, establishing the many-to-many relationship between cadets and courses, with completion status and final grades.

#### 5.4.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **SR-01** | A cadet can enroll in multiple modules | High |
| **SR-02** | A module can have multiple cadets enrolled | High |
| **SR-03** | Each cadet can only enroll once per module | High |
| **SR-04** | Start date must be captured for each enrollment | High |
| **SR-05** | Completion date is recorded upon module finish | Medium |
| **SR-06** | Final score (0–100) must be calculated and stored | High |
| **SR-07** | Grade letter (A–F) must be assigned based on score | High |
| **SR-08** | Enrollment status must be tracked | High |

#### 5.4.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Record ID | Unique identifier | Integer (Auto) | Primary Key |
| Cadet ID | Enrolled cadet | Integer | FK → Cadets, NOT NULL |
| Module ID | Training module | Integer | FK → Training Modules, NOT NULL |
| Start Date | Enrollment date | DATE | NOT NULL |
| Completion Date | Finish date | DATE | NULL allowed |
| Status | Enrollment status | VARCHAR(20) | Enum values |
| Final Score | Calculated score | DECIMAL(5,2) | 0.00–100.00 |
| Grade Letter | Letter grade | CHAR(1) | A, B, C, D, F |
| Created At | Record creation | TIMESTAMP | Auto-generated |
| Updated At | Last modification | TIMESTAMP | Auto-updated |

#### 5.4.3 Business Rules

- **Unique Constraint**: One enrollment per (cadet_id, module_id) pair
- **Completion Date**: Must be ≥ Start Date
- **Status Values**: Active, Completed, Dropped, Failed
- **Grade Calculation**:
  | Score Range | Grade |
  |-------------|-------|
  | 90–100 | A |
  | 80–89 | B |
  | 70–79 | C |
  | 60–69 | D |
  | 0–59 | F |
- **Status Transitions**:
  - Active → Completed | Dropped | Failed
  - Completed/Dropped/Failed → No changes (terminal)

---

### 5.5 PERFORMANCE EVALUATIONS (Grades/Assessments)

> **Business Purpose**: Capture individual assessments (exams, practicals, drills) within each service record, enabling weighted grade calculations and detailed performance tracking.

#### 5.5.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **PE-01** | Multiple evaluations can exist per service record | High |
| **PE-02** | Each evaluation must have a type (Exam, Practical, etc.) | High |
| **PE-03** | Raw score (0–100) must be recorded | High |
| **PE-04** | Weight factor must be assigned for final score calculation | High |
| **PE-05** | Evaluation date must be captured | High |
| **PE-06** | Evaluator notes/feedback should be optionally stored | Medium |
| **PE-07** | Weights for all evals in a module must sum to 1.0 | Medium |

#### 5.5.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Eval ID | Unique identifier | Integer (Auto) | Primary Key |
| Record ID | Parent service record | Integer | FK → Service Records, NOT NULL |
| Assessment Type | Evaluation category | VARCHAR(30) | Enum values |
| Assessment Name | Specific test name | VARCHAR(100) | NOT NULL |
| Score | Raw score | DECIMAL(5,2) | 0.00–100.00 |
| Weight | Importance factor | DECIMAL(3,2) | 0.00–1.00 |
| Evaluation Date | Assessment date | DATE | NOT NULL |
| Evaluator Notes | Instructor feedback | TEXT | NULL allowed |
| Evaluator Rank | Instructor rank | VARCHAR(20) | NULL allowed |
| Created At | Record creation | TIMESTAMP | Auto-generated |

#### 5.5.3 Business Rules

- **Assessment Types**: Exam, Practical, Field Exercise, Physical Test, Drill
- **Weight Validation**: All evals within a service record should total ≤ 1.0
- **Final Score Calculation**: `SUM(score × weight)` across all evaluations
- **Minimum Evaluations**: At least 1 evaluation required for grade assignment

---

### 5.6 MUSTER ROLLS (Attendance)

> **Business Purpose**: Track daily attendance for each training session, capturing present/absent status and check-in times for accountability and discipline tracking.

#### 5.6.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **MR-01** | Attendance must be recorded daily per cadet per module | High |
| **MR-02** | Only one attendance record per cadet per module per day | High |
| **MR-03** | Status must capture Present, Absent, Excused, Late, or AWOL | High |
| **MR-04** | Check-in time should be recorded when present/late | Medium |
| **MR-05** | Notes field for exceptional circumstances | Low |
| **MR-06** | Late threshold is 10 minutes past scheduled start | Medium |
| **MR-07** | AWOL status requires commanding officer notification | High |

#### 5.6.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Roll ID | Unique identifier | Integer (Auto) | Primary Key |
| Cadet ID | Attendee | Integer | FK → Cadets, NOT NULL |
| Module ID | Training session | Integer | FK → Training Modules, NOT NULL |
| Muster Date | Attendance date | DATE | NOT NULL |
| Status | Attendance status | VARCHAR(20) | Enum values |
| Check-in Time | Arrival time | TIME | NULL allowed |
| Notes | Exceptional notes | TEXT | NULL allowed |
| Created At | Record creation | TIMESTAMP | Auto-generated |

#### 5.6.3 Business Rules

- **Unique Constraint**: One record per (cadet_id, module_id, muster_date)
- **Status Values**: Present, Absent, Excused, Late, AWOL
- **Late Definition**: Check-in > 10 minutes after scheduled session start
- **AWOL Definition**: Unexcused absence for 2+ consecutive days
- **Attendance Rate Calculation**: `(Present + Late) / Total Sessions × 100`
- **Pass Threshold**: 75% attendance required for module completion

---

### 5.7 CADET PERFORMANCE SUMMARY (Analytics)

> **Business Purpose**: Pre-calculated aggregate metrics per cadet for dashboard efficiency, updated via scheduled ETL jobs.

#### 5.7.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **PS-01** | One summary record per cadet | High |
| **PS-02** | Overall GPA (0.00–4.00) must be calculated | High |
| **PS-03** | Attendance rate percentage must be tracked | High |
| **PS-04** | Module completion counts must be maintained | Medium |
| **PS-05** | Department-specific averages should be tracked | Medium |
| **PS-06** | Performance tier classification must be assigned | High |
| **PS-07** | Summary must be refreshed on a scheduled basis | Medium |

#### 5.7.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Summary ID | Unique identifier | Integer (Auto) | Primary Key |
| Cadet ID | Subject cadet | Integer | FK → Cadets, Unique |
| Overall GPA | Grade point average | DECIMAL(3,2) | 0.00–4.00 |
| Attendance Rate | Attendance percentage | DECIMAL(5,2) | 0–100 |
| Total Modules Completed | Completed count | Integer | ≥ 0 |
| Total Modules Failed | Failed count | Integer | ≥ 0 |
| Avg Physical Score | Physical dept avg | DECIMAL(5,2) | 0–100 |
| Avg Tactical Score | Tactical dept avg | DECIMAL(5,2) | 0–100 |
| Avg Cyber Score | Cyber dept avg | DECIMAL(5,2) | 0–100 |
| Performance Tier | Classification | VARCHAR(20) | Enum values |
| Last Updated | Refresh timestamp | TIMESTAMP | Auto-updated |

#### 5.7.3 Business Rules

- **Performance Tier Classification**:
  | Tier | GPA | Attendance | Criteria |
  |------|-----|------------|----------|
  | Elite | ≥ 3.5 | ≥ 95% | Top 10% performers |
  | High Performer | ≥ 3.0 | ≥ 85% | Above average |
  | Standard | ≥ 2.0 | ≥ 75% | Meeting requirements |
  | At-Risk | < 2.0 | < 75% | Intervention needed |
- **GPA Calculation**: Based on letter grades (A=4.0, B=3.0, C=2.0, D=1.0, F=0.0)
- **Update Frequency**: Daily refresh via scheduled ETL job

---

### 5.8 ATTRITION RISK (Predictive Analytics)

> **Business Purpose**: ML/analytics-driven predictions for cadet dropout risk, enabling proactive intervention for at-risk personnel.

#### 5.8.1 Business Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| **AR-01** | Risk score (0–100) must be calculated per cadet | High |
| **AR-02** | Risk level classification must be assigned | High |
| **AR-03** | Contributing risk factors must be stored (JSON) | Medium |
| **AR-04** | Recommended intervention actions should be suggested | Medium |
| **AR-05** | Assessment date must be recorded | High |
| **AR-06** | Next review date scheduling must be supported | Low |
| **AR-07** | Multiple historical risk assessments per cadet allowed | Medium |

#### 5.8.2 Key Attributes

| Attribute | Description | Data Type | Constraints |
|-----------|-------------|-----------|-------------|
| Risk ID | Unique identifier | Integer (Auto) | Primary Key |
| Cadet ID | Assessed cadet | Integer | FK → Cadets, NOT NULL |
| Risk Score | Probability (0–100) | DECIMAL(5,2) | 0.00–100.00 |
| Risk Level | Classification | VARCHAR(20) | Enum values |
| Risk Factors | Contributing factors | JSON | Flexible structure |
| Recommended Actions | Intervention suggestions | TEXT | NULL allowed |
| Assessment Date | Calculation date | DATE | NOT NULL |
| Next Review Date | Scheduled reassessment | DATE | NULL allowed |

#### 5.8.3 Business Rules

- **Risk Level Classification**:
  | Score Range | Level | Action |
  |-------------|-------|--------|
  | 0–25 | Low | Routine monitoring |
  | 26–50 | Medium | Increased check-ins |
  | 51–75 | High | CO intervention required |
  | 76–100 | Critical | Immediate command review |
- **Risk Factors (JSON Schema)**:
  ```json
  {
    "attendance_issues": boolean,
    "low_gpa": boolean,
    "medical_flags": integer,
    "disciplinary_actions": integer,
    "motivation_score": number (0-10),
    "peer_integration": string ("Good"|"Neutral"|"Poor")
  }
  ```
- **Review Frequency**: Critical = Weekly, High = Bi-weekly, Medium = Monthly

---

## 6. Functional Requirements

### 6.1 Core CRUD Operations

| Req ID | Function | Description | Priority |
|--------|----------|-------------|----------|
| **FR-01** | Create Cadet | Register new cadet with personal details and company assignment | High |
| **FR-02** | Update Cadet | Modify rank, status, or company assignment | High |
| **FR-03** | View Cadet | Retrieve full cadet profile with all related records | High |
| **FR-04** | Enroll Cadet | Create service record linking cadet to training module | High |
| **FR-05** | Record Grade | Add performance evaluation to service record | High |
| **FR-06** | Record Attendance | Log daily muster status for cadet/module | High |
| **FR-07** | Create Company | Add new organizational unit with code, name, and CO | High |
| **FR-08** | View Company | Retrieve company details with assigned cadets and stats | High |
| **FR-09** | Update Company | Modify CO, max strength, or company name | Medium |
| **FR-10** | Delete Company | Remove company (reassign cadets first) | Low |
| **FR-11** | Add Module | Create new training module in catalog | Medium |

### 6.2 Reporting Requirements

| Req ID | Report | Description | Frequency |
|--------|--------|-------------|-----------|
| **FR-12** | Company Roster | List all cadets in a company with status | On-demand |
| **FR-13** | Module Enrollment | Cadets enrolled in specific module | On-demand |
| **FR-14** | Performance Dashboard | GPA, attendance, tier by company | Daily |
| **FR-15** | At-Risk Report | Cadets with High/Critical attrition risk | Weekly |
| **FR-16** | Attendance Summary | Attendance rates by module/company | Weekly |
| **FR-17** | Academic Transcript | Full grade history per cadet | On-demand |
| **FR-18** | Company Rankings | Comparative performance across companies | Monthly |

### 6.3 Automated Processing

| Req ID | Process | Description | Trigger |
|--------|---------|-------------|---------|
| **FR-19** | Calculate Final Score | Aggregate weighted evaluation scores | Grade entry |
| **FR-20** | Assign Grade Letter | Derive letter from final score | Score calculation |
| **FR-21** | Update Performance Summary | Recalculate GPA and attendance | Daily ETL |
| **FR-22** | Calculate Attrition Risk | Run risk prediction model | Weekly ETL |
| **FR-23** | Flag AWOL Status | Identify 2+ consecutive absences | Daily |

---

## 7. Non-Functional Requirements

### 7.1 Performance

| Req ID | Requirement | Target |
|--------|-------------|--------|
| **NF-01** | Query response time for dashboards | < 2 seconds |
| **NF-02** | Bulk data import (500 records) | < 30 seconds |
| **NF-03** | Concurrent user support | 50+ users |
| **NF-04** | Database size capacity | 100,000+ records |

### 7.2 Security

| Req ID | Requirement | Details |
|--------|-------------|---------|
| **NF-05** | Role-based access control (RBAC) | Admin, Officer, Instructor, Viewer |
| **NF-06** | Data encryption at rest | Sensitive PII fields |
| **NF-07** | Audit logging | All create/update/delete operations |
| **NF-08** | Password requirements | Minimum 12 characters, complexity rules |

### 7.3 Reliability

| Req ID | Requirement | Target |
|--------|-------------|--------|
| **NF-09** | System availability | 99.5% uptime |
| **NF-10** | Data backup frequency | Daily automated backups |
| **NF-11** | Recovery time objective (RTO) | < 4 hours |
| **NF-12** | Recovery point objective (RPO) | < 24 hours |

### 7.4 Scalability

| Req ID | Requirement | Details |
|--------|-------------|---------|
| **NF-13** | Horizontal scaling support | Database replication ready |
| **NF-14** | Initial cadet capacity | 500 cadets |
| **NF-15** | Future capacity expansion | 2,000+ cadets |

---

## 8. Business Rules & Constraints

### 8.1 Data Integrity Rules

| Rule ID | Rule | Implementation |
|---------|------|----------------|
| **BR-01** | Cadet must be Active to enroll in modules | Check constraint/trigger |
| **BR-02** | Completion date must be ≥ Start date | Check constraint |
| **BR-03** | Grade letter must match score range | Trigger |
| **BR-04** | Final score must be 0–100 | Check constraint |
| **BR-05** | GPA must be 0.00–4.00 | Check constraint |
| **BR-06** | Attendance rate must be 0–100% | Check constraint |
| **BR-07** | Weight factors must be 0.00–1.00 | Check constraint |
| **BR-08** | One cadet per service number | Unique constraint |

### 8.2 Referential Integrity

| Relationship | On Delete Action |
|--------------|------------------|
| Companies → Cadets | SET NULL (preserve cadet, clear assignment) |
| Cadets → Service Records | CASCADE (remove all enrollments) |
| Service Records → Performance Evals | CASCADE (remove evaluations) |
| Cadets → Muster Rolls | CASCADE (remove attendance records) |
| Cadets → Performance Summary | CASCADE (remove summary) |
| Cadets → Attrition Risk | CASCADE (remove predictions) |

### 8.3 Workflow Constraints

| Constraint | Description |
|------------|-------------|
| **WF-01** | Cadet must complete all Basic modules before Elite enrollments |
| **WF-02** | 75% attendance required for module completion |
| **WF-03** | Failed modules must be re-enrolled, not updated |
| **WF-04** | Graduated cadets cannot have new enrollments |
| **WF-05** | Discharged status is irreversible |

---

## 9. Use Cases

### 9.1 UC-01: Enroll New Cadet

| Field | Value |
|-------|-------|
| **Actor** | Admissions Staff |
| **Precondition** | Applicant has passed entry requirements |
| **Steps** | 1. Enter personal details (name, DOB, email)<br>2. Generate service number<br>3. Assign to company<br>4. Set initial rank (Recruit)<br>5. Set status (Active)<br>6. Save record |
| **Postcondition** | Cadet record exists, empty service records |
| **Exception** | Duplicate email/service number → Error |

### 9.2 UC-02: Record Daily Attendance

| Field | Value |
|-------|-------|
| **Actor** | Training Officer |
| **Precondition** | Training session scheduled |
| **Steps** | 1. Select module and date<br>2. Call roll for each cadet<br>3. Mark Present/Absent/Late/AWOL<br>4. Record check-in times for present/late<br>5. Submit muster roll |
| **Postcondition** | Attendance recorded, summary updated |
| **Exception** | AWOL flag triggers CO notification |

### 9.3 UC-03: Submit Performance Evaluation

| Field | Value |
|-------|-------|
| **Actor** | Training Officer |
| **Precondition** | Cadet is enrolled in module (Active) |
| **Steps** | 1. Select cadet and module (service record)<br>2. Enter assessment type and name<br>3. Record raw score (0–100)<br>4. Assign weight factor<br>5. Add evaluator notes (optional)<br>6. Submit evaluation |
| **Postcondition** | Evaluation saved, final score recalculated |
| **Exception** | Weight total > 1.0 → Warning |

### 9.4 UC-04: Generate At-Risk Report

| Field | Value |
|-------|-------|
| **Actor** | Commanding Officer |
| **Precondition** | Performance summaries and risk scores calculated |
| **Steps** | 1. Navigate to reports<br>2. Select "At-Risk Cadets"<br>3. Filter by company (optional)<br>4. View cadets with High/Critical risk<br>5. Review risk factors and recommendations<br>6. Export report (PDF) |
| **Postcondition** | Report generated for review |
| **Exception** | No at-risk cadets → Empty report |

### 9.5 UC-05: Promote Cadet

| Field | Value |
|-------|-------|
| **Actor** | Commanding Officer |
| **Precondition** | Cadet meets promotion criteria (GPA, attendance, time-in-grade) |
| **Steps** | 1. Search for cadet<br>2. Review performance summary<br>3. Update rank field<br>4. Add promotion notes<br>5. Save changes |
| **Postcondition** | Rank updated, audit trail recorded |
| **Exception** | Invalid rank progression → Error |

### 9.6 UC-06: Create New Company

| Field | Value |
|-------|-------|
| **Actor** | System Administrator |
| **Precondition** | Administrator has Create Company permission |
| **Steps** | 1. Navigate to Company Management<br>2. Click "Add New Company"<br>3. Enter company code (e.g., F-CO)<br>4. Enter company name (e.g., "Foxtrot Company")<br>5. Assign Commanding Officer<br>6. Set max strength capacity<br>7. Save company |
| **Postcondition** | New company available for cadet assignment |
| **Exception** | Duplicate company code → Error |

---

## 10. Data Dictionary

### 10.1 Enumeration Values

#### Cadet Status
| Value | Description |
|-------|-------------|
| Active | Currently enrolled and training |
| Graduated | Successfully completed program |
| Discharged | Removed from program (involuntary) |
| Medical Leave | Temporary absence for medical reasons |

#### Cadet Rank
| Value | Description |
|-------|-------------|
| Recruit | Initial entry rank |
| Private | After completion of basic training |
| Corporal | Junior NCO |
| Sergeant | NCO leadership position |

#### Department
| Value | Description |
|-------|-------------|
| Cyber | Cybersecurity and digital operations |
| Physical | Physical fitness and conditioning |
| Strategic | Military strategy and planning |
| Tactical | Combat and field operations |
| Medical | First aid and medical training |

#### Difficulty Level
| Value | Description |
|-------|-------------|
| Basic | Foundational courses |
| Advanced | Intermediate complexity |
| Elite | Highest difficulty, requires prerequisites |

#### Enrollment Status
| Value | Description |
|-------|-------------|
| Active | Currently undertaking module |
| Completed | Successfully finished module |
| Dropped | Withdrew before completion |
| Failed | Did not meet passing criteria |

#### Attendance Status
| Value | Description |
|-------|-------------|
| Present | On time for session |
| Absent | Did not attend (unexcused) |
| Excused | Approved absence |
| Late | Arrived after start time |
| AWOL | Absent Without Leave (2+ days) |

#### Performance Tier
| Value | Description |
|-------|-------------|
| Elite | Top performers (GPA ≥ 3.5, Attendance ≥ 95%) |
| High Performer | Above average (GPA ≥ 3.0, Attendance ≥ 85%) |
| Standard | Meeting requirements (GPA ≥ 2.0, Attendance ≥ 75%) |
| At-Risk | Needs intervention (Below Standard thresholds) |

#### Risk Level
| Value | Description |
|-------|-------------|
| Low | Minimal attrition risk (0–25) |
| Medium | Moderate concern (26–50) |
| High | Significant risk (51–75) |
| Critical | Immediate attention required (76–100) |

### 10.2 Foreign Key Relationships

```
┌─────────────────┐
│   COMPANIES     │
│  (company_id)   │
└────────┬────────┘
         │ 1:M
         ▼
┌─────────────────┐       ┌──────────────────────────┐
│     CADETS      │──────▶│ CADET_PERFORMANCE_SUMMARY│
│   (cadet_id)    │  1:1  │       (summary_id)       │
└────────┬────────┘       └──────────────────────────┘
         │
    ┌────┴────┬──────────────┐
    │ 1:M     │ 1:M          │ 1:M
    ▼         ▼              ▼
┌────────┐ ┌────────────┐ ┌──────────────┐
│SERVICE │ │ MUSTER     │ │ ATTRITION    │
│RECORDS │ │ ROLLS      │ │ RISK         │
│(rec_id)│ │ (roll_id)  │ │ (risk_id)    │
└────┬───┘ └────────────┘ └──────────────┘
     │ 1:M
     ▼
┌─────────────────┐
│  PERFORMANCE    │
│    EVALS        │
│   (eval_id)     │
└─────────────────┘

    ┌─────────────────┐
    │TRAINING_MODULES │
    │  (module_id)    │
    └────────┬────────┘
             │ 1:M
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐    ┌────────────┐
│SERVICE  │    │ MUSTER     │
│RECORDS  │    │ ROLLS      │
└─────────┘    └────────────┘
```

---

## 11. Appendix

### 11.1 Glossary

| Term | Definition |
|------|------------|
| **Cadet** | Trainee enrolled at the Elite Defense Academy |
| **CO** | Commanding Officer of a company |
| **GPA** | Grade Point Average (0.00–4.00 scale) |
| **Muster** | Daily attendance/roll call |
| **AWOL** | Absent Without Leave |
| **ETL** | Extract, Transform, Load (data pipeline) |
| **3NF** | Third Normal Form (database normalization) |
| **PK** | Primary Key |
| **FK** | Foreign Key |
| **SRMS** | Student Records Management System |

### 11.2 Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-17 | Project Team | Initial draft |

### 11.3 Related Documents

| Document | Location |
|----------|----------|
| Schema Plan | `control_centre/docs/schema_plan.md` |
| ERD Diagram | `control_centre/img/erdiagram_elite.svg` |
| Project Tracker | `control_centre/mission_command.html` |
| Tech Stack | `control_centre/tech_stack.html` |

---

> **CLASSIFICATION**: UNCLASSIFIED  
> **DISTRIBUTION**: Limited to Elite Defense Academy Project Team  
> **NEXT REVIEW**: Upon completion of Phase 1 implementation
