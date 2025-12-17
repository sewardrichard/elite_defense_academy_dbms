# Elite Defense Academy — Student Records Management System

> 🎖️ A comprehensive database management system for tracking cadet training, performance analytics, and attrition risk prediction at a military defense training institution.

---

## 📋 Project Overview

The **Elite Defense Academy SRMS** is a PostgreSQL-based relational database system designed to manage all aspects of cadet lifecycle management. The system provides:

- **Centralized Personnel Records** — Track cadets from enrollment through graduation
- **Training Module Management** — Comprehensive course catalog with departments and difficulty levels
- **Performance Tracking** — Weighted evaluations, GPA calculations, and academic transcripts
- **Attendance Monitoring** — Daily muster rolls with Present/Absent/Late/AWOL tracking
- **Predictive Analytics** — AI/ML-powered attrition risk prediction for early intervention
- **Company Management** — Organizational unit structuring with commanding officer assignments

---

## 🗂️ Project Structure

```
elite_defense_academy/
├── README.md                 # Project overview (this file)
├── docs/
│   └── business_requirements.md   # Comprehensive BRD (8 entities, 23 functional requirements)
└── control_centre/           # Project planning & visualization dashboard
    ├── docs/                 # Technical documentation
    │   └── schema_plan.md    # Database schema specifications
    ├── sql/                  # SQL scripts (DDL, DML)
    ├── etl/                  # Data generation & ETL pipelines
    └── *.html                # Interactive project dashboard
```

---

## 📊 Business Requirements Summary

The system manages **8 core entities** to support the Academy's operations:

| Entity | Purpose |
|--------|---------|
| **Companies** | Organizational units (Alpha, Bravo, Charlie...) |
| **Cadets** | Personnel records with ranks, status, assignments |
| **Training Modules** | Course catalog (Cyber, Tactical, Medical...) |
| **Service Records** | Cadet ↔ Module enrollments |
| **Performance Evals** | Weighted assessments and grades |
| **Muster Rolls** | Daily attendance tracking |
| **Performance Summary** | Pre-calculated analytics per cadet |
| **Attrition Risk** | ML-driven dropout predictions |

### Key Functional Requirements

- **23 Functional Requirements** covering CRUD, reporting, and automation
- **15 Non-Functional Requirements** for performance, security, and scalability
- **6 Use Cases** documenting core workflows
- **Complete Data Dictionary** with enum values and relationships

📄 **Full Details:** [docs/business_requirements.md](docs/business_requirements.md)

---

## 🗺️ Project Roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **Phase 1** | Business Requirements Document | ✅ Complete |
| **Phase 2** | Entity Relationship Diagram (ERD) | 🔄 Next |
| **Phase 3** | Database Schema (DDL) | ⏳ Pending |
| **Phase 4** | ETL Pipeline & Sample Data | ⏳ Pending |
| **Phase 5** | SQL Queries & Views | ⏳ Pending |
| **Phase 6** | Deployment & Documentation | ⏳ Pending |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Database** | PostgreSQL 15+ |
| **ETL/Scripts** | Python (Faker, Pandas, psycopg2) |
| **Containerization** | Docker & Docker Compose |
| **Visualization** | Interactive HTML Dashboard |
| **Deployment** | Render / Railway / Supabase |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Business Requirements](docs/business_requirements.md) | Comprehensive BRD with entities, requirements, and use cases |
| Schema Plan | Database schema specifications (in control_centre) |
| ERD Diagram | Visual entity relationships (coming soon) |

---

## 🚀 Getting Started

*Coming in Phase 3 — Database setup and local development instructions*

---

## 📝 License

This project is part of the Elite Defense Academy educational initiative.

---

> **Classification:** UNCLASSIFIED  
> **Last Updated:** 2025-12-17
