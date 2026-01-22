# Interactive CLI Revamp Plan (Textual TUI)

## 1. Objective
Refactor the existing argument-based CLI into a rich, interactive Terminal User Interface (TUI) using the **Textual** framework. This will provide a dashboard-like experience with menus, forms, and data tables.

## 2. Technology Stack
- **Framework**: [Textual](https://textual.textualize.io/) (Python)
- **Database Access**: `psycopg2` (Existing)
- **Data Handling**: `pandas` (Existing) for complex data manipulation if needed.

## 3. Architecture & Features

### A. Main Dashboard (App Container)
- **Sidebar / Navigation Menu**:
    - **Home**: Overview / Welcome
    - **Student Management**: Add, View, Enroll
    - **Academic Records**: Grading, Attendance
    - **Reports & Analytics**: The 5 Advanced SQL Queries
    - **System**: Exit

### B. Functional Modules (Screens/Tabs)

#### 1. Student Management
- **Add Student Form**: Input fields for first name, last name, DOB, etc.
- **Enroll Student**: Dropdown to select Student and Course.

#### 2. Academic Records
- **Record Grades**: Form to select Enrollment and input Grade.
- **Mark Attendance**: Form to select Course and Date, then list students to toggle Present/Absent.

#### 3. Analytics Dashboard (DataTables)
These views directly correspond to the advanced SQL queries in `database/`:
- **Course Rosters** (`05_view_course_students.sql`): Select a course -> View Table of students.
- **Course Performance** (`06_course_avg_grades.sql`): Table of courses with average grades.
- **At-Risk Students** (`07_low_attendance_risk.sql`): Highlight students with <75% attendance.
- **Honor Roll** (`08_top_student_ranking.sql`): Top 10 students by GPA.
- **Enrollment Stats** (`09_enrollment_stats.sql`): Bar chart or Table of enrollment counts.

## 4. Implementation Steps
1.  **Dependencies**: Add `textual` to `requirements.txt`.
2.  **Prototype**: Create a basic `tui.py` with the layout and navigation.
3.  **Database Integration**: Connect the TUI widgets to the existing database functions.
4.  **SQL Integration**: Implement methods to execute the stored SQL files (`05` to `09`) and populate DataTables.
5.  **Polishing**: Add CSS styling for a "Command Center" aesthetic.

## 5. Timeline
- **Phase 1**: UI Skeleton & Navigation (1 day)
- **Phase 2**: Forms & CRUD operations (1 day)
- **Phase 3**: Analytics & Reporting (1 day)
...
