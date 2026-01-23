import sys
import math
from datetime import date
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.controllers import (
    add_student, enroll_student, record_grade, mark_attendance, 
    update_student, delete_student, get_student_id_by_email, get_student_details,
    get_students_in_course,
    get_student_enrollments, get_student_grades, get_student_attendance,
    update_grade, delete_grade, update_attendance, delete_attendance,
    get_all_courses, add_course, update_course, delete_course, unenroll_student
)
from src.database import execute_query
from src.reports import (
    generate_official_transcript,
    generate_company_readiness_ledger,
    generate_attrition_watchlist_report,
    generate_course_grit_report,
    generate_daily_muster_report,
)
from src.utils import get_user_input, validate_email, validate_date, validate_score
# Create a global console for rich output
console = Console()


def print_header():
    console.rule("ELITE DEFENSE ACADEMY DBMS", style="bold cyan")


def render_menu(title, options):
    """Render a simple menu using Rich Table."""
    console.print(Panel(f"{title}", style="bold cyan"))
    table = Table(show_header=False, box=None)
    table.add_column("option", style="bold green")
    for opt in options:
        table.add_row(opt)
    console.print(table)

def perform_add_student():
    print("\n--- Add New Student ---")
    
    first = get_user_input("First Name")
    if first is None: return

    last = get_user_input("Last Name")
    if last is None: return

    email = get_user_input("Email", validator=validate_email)
    if email is None: return

    dob = get_user_input("Date of Birth (YYYY-MM-DD)", validator=validate_date)
    if dob is None: return

    while True:
        gender_input = get_user_input("Gender (M/F)")
        if gender_input is None: return
        g_map = {'m': 'Male', 'f': 'Female'}
        gender = g_map.get(gender_input.lower()[0]) if gender_input else None
        if gender:
            break
        print("Invalid selection. Please enter 'M' or 'F'.")

    # Rank selection menu
    ranks = ["Recruit", "Cadet", "Officer Cadet", "Lieutenant", "Captain"]
    print("\nSelect Rank:")
    for i, r in enumerate(ranks, 1):
        print(f"{i}. {r}")
    
    while True:
        r_sel = get_user_input("Rank Choice (1-5)", required=False)
        if r_sel is None: return # Cancel
        if r_sel == "":
            rank = "Recruit" # Default
            break
        try:
            ridx = int(r_sel) - 1
            if 0 <= ridx < len(ranks):
                rank = ranks[ridx]
                break
            print("Invalid number.")
        except:
            print("Invalid input.")

    print(f"\nAdding student: {first} {last}...")
    add_student(first, last, email, dob, gender, rank)
    input("Press Enter to continue...")

def perform_update_student():
    print("\n--- Update Student ---")
    email = get_user_input("Enter Student Email to search")
    if email is None: return
    
    sid = get_student_id_by_email(email)
    if not sid:
        print("Student not found.")
        input("Press Enter to continue...")
        return
        
    details = get_student_details(sid)
    if details:
        print(f"\n--- Current Details for {details.get('first_name')} {details.get('last_name')} ---")
        print(f"ID: {details.get('student_id')}")
        print(f"Name: {details.get('first_name')} {details.get('last_name')}")
        print(f"Email: {details.get('email')}")
        print(f"DOB: {details.get('date_of_birth')}")
        print(f"Gender: {details.get('gender')}")
        print(f"Rank: {details.get('rank')}")
        print("-----------------------------------")
    
    print("Leave fields blank to keep current value.")
    
    c_first = f" [{details['first_name']}]" if details else ""
    first = get_user_input(f"First Name{c_first}", required=False)
    if first is None: return
    
    c_last = f" [{details['last_name']}]" if details else ""
    last = get_user_input(f"Last Name{c_last}", required=False)
    if last is None: return
    
    c_email = f" [{details['email']}]" if details else ""
    new_email = get_user_input(f"New Email{c_email}", validator=validate_email, required=False)
    if new_email is None: return
    
    c_dob = f" [{details['date_of_birth']}]" if details else ""
    dob = get_user_input(f"Date of Birth (YYYY-MM-DD){c_dob}", validator=validate_date, required=False)
    if dob is None: return
    
    c_gender = f" [{details['gender']}]" if details else ""
    gender = None
    while True:
        gender_input = get_user_input(f"Gender (M/F){c_gender}", required=False)
        if gender_input is None: return
        if not gender_input:
            break
        
        g_val = gender_input.lower()[0]
        if g_val == 'm':
            gender = 'Male'
            break
        elif g_val == 'f':
            gender = 'Female'
            break
        else:
            print("Invalid selection. Only 'Male' and 'Female' are accepted.")
    
    c_rank = f" [{details['rank']}]" if details else ""
    rank = get_user_input(f"Rank{c_rank}", required=False)
    if rank is None: return
    
    update_student(sid, first, last, new_email, dob, gender, rank)
    input("Press Enter to continue...")

def perform_delete_student():
    print("\n--- Delete Student ---")
    email = get_user_input("Enter Student Email to delete")
    if email is None: return
    
    sid = get_student_id_by_email(email)
    if not sid:
        print("Student not found.")
        input("Press Enter to continue...")
        return
    
    details = get_student_details(sid)
    if details:
        print(f"\n--- Student Details ---")
        print(f"ID: {sid}")
        print(f"Name: {details.get('first_name')} {details.get('last_name')}")
        print(f"Email: {details.get('email')}")
        print(f"Gender: {details.get('gender')}")
        print(f"Rank: {details.get('rank')}")
        print("-----------------------")
    else:
        print(f"Student ID: {sid}")
        
    confirm = get_user_input(f"Are you sure you want to delete this student? (y/n)")
    if confirm and confirm.lower() == 'y':
        delete_student(sid)
    else:
        print("Deletion cancelled.")
    input("Press Enter to continue...")

def menu_student_management():
    while True:
        options = [
            "1. Add Student (Create)",
            "2. List Students (Read)",
            "3. Update Student",
            "4. Delete Student",
            "q. Back",
        ]
        render_menu("Student Management (CRUD)", options)
        choice = input("Select Option: ").strip().lower()
        
        if choice == '1':
            perform_add_student()
        elif choice == '2':
            # Pagination & Search Logic
            offset = 0
            limit = 10
            search_term = None
            
            while True:
                params = []
                base_query = "SELECT student_id, first_name, last_name, email, rank FROM students"
                count_query = "SELECT COUNT(*) as cnt FROM students"
                
                if search_term:
                    where_clause = " WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s OR rank ILIKE %s OR CAST(student_id AS TEXT) ILIKE %s"
                    base_query += where_clause
                    count_query += where_clause
                    p = f"%{search_term}%"
                    params = [p, p, p, p, p]
                    header_prefix = f"Search Results for '{search_term}'"
                else:
                    header_prefix = "All Students"
                
                # Get total count first
                count_res = execute_query(count_query, tuple(params), fetch=True)
                total_items = count_res[0]['cnt'] if count_res else 0
                total_pages = math.ceil(total_items / limit)
                current_page = (offset // limit) + 1
                
                query = base_query + f" ORDER BY student_id LIMIT {limit} OFFSET {offset}"
                
                print(f"\n--- {header_prefix} (Page {current_page} of {max(1, total_pages)}) ---")
                res = execute_query(query, tuple(params), fetch=True)
                
                if res:
                    print_results(res)
                else:
                    if offset == 0:
                        print("No records found.")
                    else:
                        print("No more records.")
                
                # Navigation Menu
                nav_opts = ["[s] Search"]
                if current_page < total_pages:
                    nav_opts.append("[Enter] Next Page")
                    
                nav_opts.append("[q] Back")
                
                if search_term:
                    nav_opts.insert(1, "[c] Clear Search")
                
                console.print("Options:", style="bold")
                console.print(" | ".join(nav_opts), style="red", markup=False)
                nav = input("Select Action: ").strip().lower()
                
                if nav == 'q':
                    break
                elif nav == 's':
                    term = input("Enter search term: ").strip()
                    if term:
                        search_term = term
                        offset = 0
                elif nav == 'c' and search_term:
                    search_term = None
                    offset = 0
                elif nav == '':
                    # Next page request
                    if offset + limit < total_items:
                        offset += limit
                    elif total_items > 0:
                        # Optionally loop back or stay
                         offset = 0
                         print("Restarting list...")
                else:
                    pass # Just refresh
                
        elif choice == '3':
            perform_update_student()
        elif choice == '4':
            perform_delete_student()
        elif choice == 'q':
            return
        else:
            print("Invalid selection.")

def menu_reports():
    while True:
        options = ["1. Official Transcript", "2. Company Readiness & Performance Ledger", "q. Back"]
        render_menu("Generate Reports", options)
        choice = input("Select Report: ").strip().lower()

        if choice == 'q':
            return

        if choice == '1':
            print("\nSelect Student for Official Transcript:")
            student = select_student_for_enrollment()
            if not student:
                input("No student selected. Press Enter to continue...")
                continue
            generate_official_transcript(student.get('student_id'))
            input("Press Enter to continue...")
            continue

        if choice == '2':
            # Generate Company Readiness & Performance Ledger
            generate_company_readiness_ledger()
            input("Press Enter to continue...")
            continue

        print("Invalid selection.")

def get_sql_content(filename):
    """Read SQL content from database directory."""
    try:
        # Resolve path relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, 'database', filename)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading SQL file {filename}: {e}")
        return None

def print_results(results):
    """Helper to print list of dicts as a basic table."""
    if not results:
        print("No results found.")
        return
    headers = list(results[0].keys())
    table = Table(show_header=True, header_style="bold magenta")
    for h in headers:
        table.add_column(h)

    for row in results:
        values = [str(row.get(h, "")) for h in headers]
        table.add_row(*values)

    console.print(table)
    console.print(f"({len(results)} rows)", style="dim")

def menu_stored_procedures():
    while True:
        options = [
            "1. View Students in Course (05)",
            "2. Course Average Grades (06)",
            "3. Low Attendance Risk (07)",
            "4. Top Student Ranking (08)",
            "5. Enrollment Stats (09)",
            "q. Back",
        ]
        render_menu("Stored Procedures & Views", options)
        choice = input("Select Option: ").strip().lower()
        
        if choice == 'q': return
        
        sql_file = None
        params = None
        
        if choice == '1':
            course_code = select_course_for_proc()
            if course_code is None:
                continue

            raw_sql = get_sql_content("05_view_course_students.sql")
            if raw_sql:
                # Replace hardcoded value in file with parameter placeholder
                sql_file = raw_sql.replace("'TAC-101'", "%s")
                params = (course_code,)
                
        elif choice == '2':
            # Launch interactive paginated view for course average grades
            view_course_avg_paginated()
            continue
        elif choice == '3':
            view_low_attendance_paginated()
            continue
        elif choice == '4':
            view_top_students()
            continue
        elif choice == '5':
            view_enrollment_stats_paginated()
            continue
        else:
            print("Invalid selection.")
            continue

        if sql_file:
            print("\nExecuting query...")
            results = execute_query(sql_file, params, fetch=True)
            print_results(results)
        
        input("Press Enter to continue...")

def select_from_list(options, prompt_text):
    """Helper to display a numbered list and get selection."""
    opts = [f"{i}. {opt}" for i, opt in enumerate(options, 1)]
    render_menu(prompt_text, opts)
        
    while True:
        choice = get_user_input(f"Select (1-{len(options)})", required=False)
        if choice is None: return None # User cancelled or empty (if allowed)
        # If user enters nothing for optional updates, we handle it outside or here?
        # For Add, we usually need selection. For Update, empty means no change.
        # Let's assumes this returns the string selected or None.
        if choice == "": return "" 
        
        try:
            auth_idx = int(choice) - 1
            if 0 <= auth_idx < len(options):
                return options[auth_idx]
            else:
                console.print("Invalid number.", style="red")
        except ValueError:
            console.print("Invalid input.", style="red")


def select_course_for_proc():
    """Paginated course selector for stored-proc flows. Returns course_code or None."""
    offset = 0
    limit = 10

    # total count
    res_count = execute_query("SELECT COUNT(*) as cnt FROM courses", fetch=True)
    total_items = res_count[0]['cnt'] if res_count else 0
    total_pages = math.ceil(total_items / limit) if total_items else 1

    while True:
        current_page = (offset // limit) + 1
        query = f"SELECT course_id, course_code, name, credits FROM courses ORDER BY course_id LIMIT {limit} OFFSET {offset}"
        courses = execute_query(query, fetch=True)

        console.print(Panel(f"Select Course (Page {current_page} of {max(1, total_pages)})", style="cyan"))
        if courses:
            tbl = Table(show_header=True, header_style="bold magenta")
            tbl.add_column("No.")
            tbl.add_column("Code", style="cyan")
            tbl.add_column("Name", style="green")
            tbl.add_column("Credits", style="yellow")
            for i, c in enumerate(courses, 1):
                tbl.add_row(str(i), c.get('course_code', ''), c.get('name', ''), str(c.get('credits', '')))
            console.print(tbl)
        else:
            if offset == 0:
                console.print("No courses found.")
            else:
                console.print("No more courses.")

        console.print("Options:", style="bold")
        console.print(" - Enter Number to select")
        console.print(" - [s] Search", style="red", markup=False)
        if current_page < total_pages:
            console.print(" - [Enter] Next Page", style="red", markup=False)
        console.print(" - [q] Back", style="red", markup=False)

        choice = input("Select: ").strip()
        if choice.lower() == 'q':
            return None

        if choice.lower() == 's':
            term = get_user_input("Search term (course code or name)")
            if term is None:
                continue
            search_sql = "SELECT course_id, course_code, name, credits FROM courses WHERE course_code ILIKE %s OR name ILIKE %s ORDER BY course_id LIMIT 10"
            results = execute_query(search_sql, (f"%{term}%", f"%{term}%"), fetch=True)
            if not results:
                console.print("No matches found.", style="red")
                continue

            tbl = Table(show_header=True, header_style="bold magenta")
            tbl.add_column("No.")
            tbl.add_column("Code", style="cyan")
            tbl.add_column("Name", style="green")
            tbl.add_column("Credits", style="yellow")
            for i, c in enumerate(results, 1):
                tbl.add_row(str(i), c.get('course_code', ''), c.get('name', ''), str(c.get('credits', '')))
            console.print(tbl)

            sel = get_user_input(f"Select (1-{len(results)})", required=False)
            if sel is None or sel == '':
                continue
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(results):
                    return results[idx].get('course_code')
            except ValueError:
                console.print("Invalid selection.", style="red")
            continue

        if choice == '':
            if offset + limit < total_items:
                offset += limit
            elif total_items > 0:
                offset = 0
                console.print("Restarting list...")
            continue

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(courses):
                return courses[idx].get('course_code')
            else:
                console.print("Invalid selection.", style="red")
        except ValueError:
            console.print("Invalid input.", style="red")

DEPARTMENTS = [
    "Tactics", "Intelligence", "Engineering", "Leadership", 
    "Weapons", "Cyber Warfare", "Logistics", "Medical", "General"
]

DIFFICULTIES = ["Basic", "Intermediate", "Advanced"]


def view_course_avg_paginated():
    """Show course average grades paginated (10 per page), with search and 'all' option."""
    offset = 0
    limit = 10
    search_term = None

    while True:
        params = []
        base_query = (
            "SELECT c.course_code, c.name as course_name, c.department, "
            "COUNT(e.student_id) as total_students, ROUND(AVG(e.final_score),2) as average_score, "
            "MAX(e.final_score) as highest_score, MIN(e.final_score) as lowest_score "
            "FROM courses c JOIN enrollments e ON c.course_id = e.course_id "
            "WHERE e.status IN ('Completed','Failed') AND e.final_score IS NOT NULL "
        )

        if search_term:
            base_query += " AND (c.course_code ILIKE %s OR c.name ILIKE %s) "
            p = f"%{search_term}%"
            params.extend([p, p])

        group_order = "GROUP BY c.course_id, c.course_code, c.name, c.department ORDER BY average_score DESC"

        # Compute total distinct courses for pagination (more robust than subquery count)
        count_query = (
            "SELECT COUNT(DISTINCT c.course_id) as cnt "
            "FROM courses c JOIN enrollments e ON c.course_id = e.course_id "
            "WHERE e.status IN ('Completed','Failed') AND e.final_score IS NOT NULL "
        )
        count_params = []
        if search_term:
            count_query += " AND (c.course_code ILIKE %s OR c.name ILIKE %s)"
            count_params = [f"%{search_term}%", f"%{search_term}%"]

        count_res = execute_query(count_query, tuple(count_params) if count_params else None, fetch=True)
        total_items = count_res[0]['cnt'] if count_res else 0
        total_pages = math.ceil(total_items / limit) if total_items else 1
        current_page = (offset // limit) + 1

        # Fetch either a page or all depending on special flag
        query = base_query + group_order + f" LIMIT {limit} OFFSET {offset}"

        console.print(Panel(f"Course Average Grades (Page {current_page} of {max(1,total_pages)})", style="cyan"))
        results = execute_query(query, tuple(params) if params else None, fetch=True)

        # Defensive: ensure we only display up to `limit` rows
        displayed = results[:limit] if results else []

        if displayed:
            tbl = Table(show_header=True, header_style="bold magenta")
            tbl.add_column("No.")
            tbl.add_column("Code", style="cyan")
            tbl.add_column("Name", style="green")
            tbl.add_column("Dept", style="magenta")
            tbl.add_column("Students", style="yellow")
            tbl.add_column("Avg", style="bright_blue")
            tbl.add_column("High")
            tbl.add_column("Low")
            start = offset + 1
            for i, r in enumerate(displayed, start):
                tbl.add_row(str(i), r.get('course_code',''), r.get('course_name',''), r.get('department',''),
                            str(r.get('total_students','')), str(r.get('average_score','')),
                            str(r.get('highest_score','')), str(r.get('lowest_score','')))
            console.print(tbl)
        else:
            console.print("No results found.")

        console.print("Options:", style="bold")
        console.print(" - [s] Search", style="red", markup=False)
        console.print(" - [a] Show All", style="red", markup=False)
        console.print(" - [Enter] Next Page", style="red", markup=False)
        console.print(" - [q] Back", style="red", markup=False)

        choice = input("Select: ").strip().lower()
        if choice == 'q':
            return
        if choice == 's':
            term = get_user_input("Search term (course code or name)")
            if term is None:
                continue
            search_term = term
            offset = 0
            continue
        if choice == 'a':
            # show all matching courses
            all_query = base_query + group_order
            all_res = execute_query(all_query, tuple(count_params) if count_params else None, fetch=True)
            if all_res:
                print_results(all_res)
            else:
                console.print("No results found.")
            input("Press Enter to continue...")
            return
        if choice == '':
            # next page
            if offset + limit < total_items:
                offset += limit
            elif total_items > 0:
                offset = 0
                console.print("Restarting list...")
            continue
        # otherwise loop


def view_low_attendance_paginated():
    """Paginated view for students below attendance threshold with search."""
    offset = 0
    limit = 10
    search_term = None

    while True:
        params = []
        base_query = (
            "SELECT s.service_number, s.first_name, s.last_name, c.company_name, "
            "ps.attendance_rate, ps.current_standing "
            "FROM students s "
            "JOIN performance_summary ps ON s.student_id = ps.student_id "
            "JOIN companies c ON s.company_id = c.company_id "
            "WHERE ps.attendance_rate < 75.00 "
        )

        if search_term:
            base_query += " AND (s.first_name ILIKE %s OR s.last_name ILIKE %s OR s.service_number ILIKE %s OR c.company_name ILIKE %s) "
            p = f"%{search_term}%"
            params.extend([p, p, p, p])

        order_clause = "ORDER BY ps.attendance_rate ASC"

        # Compute total rows for pagination (robust count)
        count_query = (
            "SELECT COUNT(*) as cnt "
            "FROM students s "
            "JOIN performance_summary ps ON s.student_id = ps.student_id "
            "JOIN companies c ON s.company_id = c.company_id "
            "WHERE ps.attendance_rate < 75.00 "
        )
        count_params = []
        if search_term:
            count_query += " AND (s.first_name ILIKE %s OR s.last_name ILIKE %s OR s.service_number ILIKE %s OR c.company_name ILIKE %s) "
            p = f"%{search_term}%"
            count_params = [p, p, p, p]

        count_res = execute_query(count_query, tuple(count_params) if count_params else None, fetch=True)
        total_items = count_res[0]['cnt'] if count_res else 0
        total_pages = math.ceil(total_items / limit) if total_items else 1
        current_page = (offset // limit) + 1

        query = base_query + order_clause + f" LIMIT {limit} OFFSET {offset}"

        console.print(Panel(f"Low Attendance Risk (Page {current_page} of {max(1,total_pages)})", style="cyan"))
        results = execute_query(query, tuple(params) if params else None, fetch=True)

        # Defensive: only display up to `limit` rows
        displayed = results[:limit] if results else []

        if displayed:
            tbl = Table(show_header=True, header_style="bold magenta")
            tbl.add_column("No.")
            tbl.add_column("Service#", style="cyan")
            tbl.add_column("First", style="green")
            tbl.add_column("Last", style="green")
            tbl.add_column("Company", style="magenta")
            tbl.add_column("Attendance", style="yellow")
            tbl.add_column("Standing", style="red")
            start = offset + 1
            for i, r in enumerate(displayed, start):
                tbl.add_row(str(i), r.get('service_number',''), r.get('first_name',''), r.get('last_name',''),
                            r.get('company_name',''), str(r.get('attendance_rate','')), r.get('current_standing',''))
            console.print(tbl)
        else:
            console.print("No results found.")

        console.print("Options:", style="bold")
        console.print(" - [s] Search", style="red", markup=False)
        console.print(" - [Enter] Next Page", style="red", markup=False)
        console.print(" - [q] Back", style="red", markup=False)

        choice = input("Select: ").strip().lower()
        if choice == 'q':
            return
        if choice == 's':
            term = get_user_input("Search term (name, service number, or company)")
            if term is None:
                continue
            search_term = term
            offset = 0
            continue
        if choice == '':
            if offset + limit < total_items:
                offset += limit
            elif total_items > 0:
                offset = 0
                console.print("Restarting list...")
            continue
        # otherwise invalid input -> loop


def view_enrollment_stats_paginated():
    """Paginated view for enrollment stats (10 rows/page) with search and next-page navigation."""
    offset = 0
    limit = 10
    search_term = None

    while True:
        params = []
        base_query = (
            "SELECT c.course_code, c.name as course_name, "
            "COUNT(e.student_id) as total_enrolled, "
            "COUNT(CASE WHEN e.status = 'In Progress' THEN 1 END) as in_progress, "
            "COUNT(CASE WHEN e.status = 'Completed' THEN 1 END) as completed, "
            "COUNT(CASE WHEN e.status = 'Failed' THEN 1 END) as failed, "
            "COUNT(CASE WHEN e.status = 'Withdrawn' THEN 1 END) as withdrawn "
            "FROM courses c LEFT JOIN enrollments e ON c.course_id = e.course_id "
            "WHERE 1=1 "
        )

        if search_term:
            base_query += " AND (c.course_code ILIKE %s OR c.name ILIKE %s) "
            p = f"%{search_term}%"
            params.extend([p, p])

        group_order = "GROUP BY c.course_id, c.course_code, c.name ORDER BY total_enrolled DESC"

        # count total matching rows
        count_query = "SELECT COUNT(*) as cnt FROM (" + base_query + group_order + ") sub"
        count_res = execute_query(count_query, tuple(params) if params else None, fetch=True)
        total_items = count_res[0]['cnt'] if count_res else 0
        total_pages = math.ceil(total_items / limit) if total_items else 1
        current_page = (offset // limit) + 1

        # fetch page
        query = base_query + group_order + f" LIMIT {limit} OFFSET {offset}"
        results = execute_query(query, tuple(params) if params else None, fetch=True)

        displayed = results[:limit] if results else []

        console.print(Panel(f"Enrollment Stats (Page {current_page} of {max(1,total_pages)})", style="cyan"))
        if displayed:
            tbl = Table(show_header=True, header_style="bold magenta")
            tbl.add_column("No.")
            tbl.add_column("Code", style="cyan")
            tbl.add_column("Name", style="green")
            tbl.add_column("Total", style="yellow")
            tbl.add_column("InProgress")
            tbl.add_column("Completed")
            tbl.add_column("Failed")
            tbl.add_column("Withdrawn")
            start = offset + 1
            for i, r in enumerate(displayed, start):
                tbl.add_row(str(i), r.get('course_code',''), r.get('course_name',''),
                            str(r.get('total_enrolled','')), str(r.get('in_progress','')),
                            str(r.get('completed','')), str(r.get('failed','')), str(r.get('withdrawn','')))
            console.print(tbl)
        else:
            console.print("No results found.")

        console.print("Options:", style="bold")
        console.print(" - [s] Search", style="red", markup=False)
        console.print(" - [a] Show All", style="red", markup=False)
        console.print(" - [Enter] Next Page", style="red", markup=False)
        console.print(" - [q] Back", style="red", markup=False)

        choice = input("Select: ").strip().lower()
        if choice == 'q':
            return
        if choice == 's':
            term = get_user_input("Search term (course code or name)")
            if term is None:
                continue
            search_term = term
            offset = 0
            continue
        if choice == 'a':
            all_query = base_query + group_order
            all_res = execute_query(all_query, tuple(params) if params else None, fetch=True)
            if all_res:
                print_results(all_res)
            else:
                console.print("No results found.")
            input("Press Enter to continue...")
            return
        if choice == '':
            if offset + limit < total_items:
                offset += limit
            elif total_items > 0:
                offset = 0
                console.print("Restarting list...")
            continue
        # otherwise loop


def view_top_students():
    """Show top N students by GPA (default 10). User may enter custom N."""
    while True:
        num_in = get_user_input("Number of top students to show (default 10)", required=False)
        if num_in is None:
            return
        if num_in == "":
            n = 10
        else:
            try:
                n = int(num_in)
                if n <= 0:
                    print("Please enter a positive integer.")
                    continue
            except ValueError:
                print("Invalid number. Please enter a positive integer.")
                continue

        query = f"""
SELECT
    RANK() OVER (ORDER BY ps.gpa DESC) AS rank,
    s.service_number,
    s.first_name,
    s.last_name,
    c.company_name,
    ps.gpa,
    ps.total_credits
FROM
    students s
JOIN
    performance_summary ps ON s.student_id = ps.student_id
JOIN
    companies c ON s.company_id = c.company_id
ORDER BY
    ps.gpa DESC
LIMIT {n};
"""

        results = execute_query(query, fetch=True)
        if not results:
            console.print("No students found.")
            input("Press Enter to continue...")
            return

        tbl = Table(show_header=True, header_style="bold magenta")
        tbl.add_column("Rank", style="cyan")
        tbl.add_column("Service#", style="cyan")
        tbl.add_column("First", style="green")
        tbl.add_column("Last", style="green")
        tbl.add_column("Company", style="magenta")
        tbl.add_column("GPA", style="bright_blue")
        tbl.add_column("Credits", style="yellow")

        for r in results:
            tbl.add_row(str(r.get('rank','')), r.get('service_number',''), r.get('first_name',''),
                        r.get('last_name',''), r.get('company_name',''), str(r.get('gpa','')), str(r.get('total_credits','')))

        console.print(tbl)
        input("Press Enter to continue...")
        return

def perform_add_course():
    print("\n--- Add New Course ---")
    
    code = get_user_input("Course Code (e.g. WPN-202)")
    if code is None: return
    
    name = get_user_input("Course Name")
    if name is None: return
    
    credits_in = get_user_input("Credits (1-20)")
    if credits_in is None: return
    try:
        credits = int(credits_in)
    except:
        print("Invalid credits.")
        return
        
    dept = select_from_list(DEPARTMENTS, "Select Department")
    if not dept: return
    
    diff = select_from_list(DIFFICULTIES, "Select Difficulty")
    if not diff: diff = "Basic"
    
    desc = get_user_input("Description", required=False)
    
    if add_course(code, name, credits, dept, diff, desc):
        print("\nCourse successfully added to database.")
    input("Press Enter to continue...")

def perform_manage_course(course):
    """Sub-menu for a specific course."""
    cid = course['course_id']
    ccode = course['course_code']
    
    while True:
        console.print(Panel(f"Managing Course: {ccode} - {course['name']}", style="cyan"))

        tbl = Table(show_header=True, header_style="bold magenta")
        tbl.add_column("No.")
        tbl.add_column("Action", style="green")
        tbl.add_row("1", "View Enrolled Students")
        tbl.add_row("2", "Enroll Student")
        tbl.add_row("3", "Unenroll Student")
        tbl.add_row("4", "Record Grade")
        tbl.add_row("5", "Mark Attendance")
        tbl.add_row("6", "Update Course Details")
        tbl.add_row("7", "Delete Course")
        console.print(tbl)

        console.print("Options:", style="bold")
        console.print(" - [q] Back", style="red", markup=False)

        choice = input("\nSelect Option: ").strip().lower()
        
        if choice == '1':
            perform_view_enrolled_students(ccode, course['name'])
        elif choice == '2':
            student = select_student_for_enrollment()
            if student:
                date_str = str(date.today())
                if enroll_student(student['email'], ccode, date_str):
                    print(f"\nSUCCESS: Enrolled {student['first_name']} {student['last_name']} ({student['rank']})")
                    print(f"Details: ID={student['student_id']}, Email={student['email']}, Course={ccode}")
                input("Press Enter to continue...")
        elif choice == '3':
            # Unenroll with selector and confirmation
            student = select_enrolled_student(ccode, "Unenroll")
            if student:
                 print(f"\n--- Confirm Unenrollment ---")
                 print(f"Student: {student['first_name']} {student['last_name']} (ID: {student['student_id']})")
                 print(f"Rank:    {student.get('rank', 'N/A')}")
                 print(f"Email:   {student['email']}")
                 print(f"Course:  {ccode} - {course['name']}")
                 
                 confirm = get_user_input("Are you sure you want to unenroll this student? (y/n)")
                 if confirm and confirm.lower() == 'y':
                     unenroll_student(student['email'], ccode)
                 else:
                     print("Aborted.")
                 input("Press Enter to continue...")
        elif choice == '4':
            manage_grades_workflow(ccode, course['name'])
        elif choice == '5':
            manage_attendance_workflow(ccode, course['name'])
        elif choice == '6':
             print(f"Update {ccode}. Leave blank to keep current.")
             n_name = get_user_input(f"Name [{course['name']}]", required=False)
             
             n_credits = None
             c_in = get_user_input(f"Credits [{course.get('credits', '')}]", required=False)
             if c_in:
                 try: n_credits = int(c_in)
                 except: print("Invalid credits ignored.")
             
             print(f"Current Department: {course.get('department')}")
             n_dept = select_from_list(DEPARTMENTS, "New Department (Enter to skip)")
             if n_dept == "": n_dept = None
             
             print(f"Current Difficulty: {course.get('difficulty_level')}")
             n_diff = select_from_list(DIFFICULTIES, "New Difficulty (Enter to skip)")
             if n_diff == "": n_diff = None
             
             n_desc = get_user_input(f"Description [{course.get('description','')}]", required=False)
             
             if update_course(cid, n_name, n_credits, n_dept, n_diff, n_desc):
                 # Update local view
                 if n_name: course['name'] = n_name
                 if n_credits: course['credits'] = n_credits
                 if n_dept: course['department'] = n_dept
                 if n_diff: course['difficulty_level'] = n_diff
                 if n_desc: course['description'] = n_desc
             input("Press Enter to continue...")
        elif choice == '7':
            confirm = get_user_input(f"Delete course {ccode}? This cannot be undone. (y/n)")
            if confirm and confirm.lower() == 'y':
                if delete_course(cid):
                    input("Deleted. Press Enter...")
                    return # Exit management view as course is gone
            else:
                print("Cancelled.")
        elif choice == 'q':
            return
        else:
            print("Invalid.")
def select_enrolled_student(course_code, prompt_action="Select"):
    """Interactively select a student enrolled in `course_code`.
    Returns the student dict (with id, first, last, email, rank) or None.
    """
    students = get_students_in_course(course_code)
    if not students:
        print("No students enrolled in this course.")
        return None

    offset = 0
    limit = 10
    total_items = len(students)
    total_pages = math.ceil(total_items / limit)

    while True:
        # Slice for pagination
        page_items = students[offset:offset+limit]
        current_page = (offset // limit) + 1

        console.print(Panel(f"Select Student to {prompt_action} (Page {current_page} of {total_pages})", style="cyan"))
        tbl = Table(show_header=True, header_style="bold magenta")
        tbl.add_column("Student ID", style="cyan")
        tbl.add_column("Name", style="green")
        tbl.add_column("Rank", style="yellow")
        for s in page_items:
            tbl.add_row(str(s.get('student_id', '')), f"{s.get('first_name','')} {s.get('last_name','')}", str(s.get('rank','')))
        console.print(tbl)

        console.print("Options:", style="bold")
        console.print(" - Enter Student ID to Select")
        if current_page < total_pages:
            console.print(" - [Enter] Next Page", style="red", markup=False)
        if current_page > 1:
            console.print(" - [p] Previous Page", style="red", markup=False)
        console.print(" - [q] Back", style="red", markup=False)

        choice = input("Choice: ").strip()

        if choice.lower() == 'q':
            return None

        if choice == "":
            if offset + limit < total_items:
                offset += limit
            elif offset > 0:
                offset = 0
                print("Restarting list...")
            continue
        elif choice.lower() == 'p':
            if offset >= limit:
                offset -= limit
            continue

        # Try to match ID
        try:
            sid_input = int(choice)
            selected_student = next((s for s in students if s['student_id'] == sid_input), None)
            if selected_student:
                return selected_student
            else:
                print("Invalid Student ID from list.")
        except ValueError:
            print("Invalid input.")

def perform_view_enrolled_students(course_code, course_name):
    """View all students enrolled in a course with pagination."""
    students = get_students_in_course(course_code)
    if not students:
        print("No students enrolled in this course.")
        return

    offset = 0
    limit = 10
    total_items = len(students)
    total_pages = math.ceil(total_items / limit)
    
    while True:
        page_items = students[offset:offset+limit]
        current_page = (offset // limit) + 1

        console.print(Panel(f"Enrolled Students: {course_code} (Page {current_page} of {total_pages})", style="cyan"))
        tbl = Table(show_header=True, header_style="bold magenta")
        tbl.add_column("ID", style="cyan")
        tbl.add_column("Rank", style="yellow")
        tbl.add_column("Name", style="green")
        tbl.add_column("Email", style="blue")
        for s in page_items:
            tbl.add_row(str(s.get('student_id','')), str(s.get('rank','')), f"{s.get('first_name','')} {s.get('last_name','')}", s.get('email',''))
        console.print(tbl)

        console.print("Options:", style="bold")
        if current_page < total_pages:
            console.print(" - [Enter] Next Page", style="red", markup=False)
        console.print(" - [q] Back", style="red", markup=False)
        
        choice = input("Choice: ").strip().lower()
        
        if choice == 'q':
            return
        elif choice == '':
            if offset + limit < total_items:
                offset += limit
            else:
                 offset = 0 # loop back
        else:
            print("Invalid.")

def perform_add_grade_context(email, course_code):
    print(f"\nAdding Grade for {email} in {course_code}")
    
    # Define Assessment Types with Weights
    # Constraint allow list: 'Exam', 'Practical', 'Quiz', 'Assignment', 'Field Exercise', 'Final Exam'
    assessments = {
        '1': {'name': 'Exam', 'weight': 0.4},
        '2': {'name': 'Quiz', 'weight': 0.1},
        '3': {'name': 'Assignment', 'weight': 0.1},
        '4': {'name': 'Practical', 'weight': 0.2},
        '5': {'name': 'Field Exercise', 'weight': 0.3},
        '6': {'name': 'Final Exam', 'weight': 0.5}
    }
    
    options = [f"{k}. {v['name']} (Weight: {v['weight']})" for k, v in assessments.items()]
    render_menu("Select Assessment Type", options)
    choice = get_user_input("Choice (1-6)")
    if choice is None: return
    
    info = assessments.get(choice)
    if not info:
        print("Invalid selection.")
        return
        
    atype = info['name']
    weight = info['weight']
    
    # Confirm or Edit Weight?
    # User requested preset weights. We use them directly.
    # User asked: "should the weights not total 1.0" - usually yes, but for a single entry we just adding one.
    
    score = get_user_input("Score (0-100)", validator=validate_score)
    if score is None: return
    
    remarks = get_user_input("Remarks", required=False)
    
    record_grade(email, course_code, atype, float(score), weight, remarks)
    input("Press Enter to continue...")

def perform_mark_attendance_context(email, course_code):
    print(f"\nMarking Attendance for {email} in {course_code}")
    
    # 1. Date defaults to today
    dt = str(date.today())
    print(f"Date: {dt}")
    
    # 2. Status Menu
    statuses = {
        '1': 'Present',
        '2': 'Absent',
        '3': 'Late',
        '4': 'Excused',
        '5': 'AWOL'
    }
    
    options = [f"{k}. {v}" for k, v in statuses.items()]
    render_menu("Select Status", options)
    choice = get_user_input("Choice (1-5)")
    if choice is None: return
    
    status = statuses.get(choice)
    if not status:
        print("Invalid status selection.")
        return
    
    remarks = get_user_input("Remarks", required=False)
    mark_attendance(email, course_code, dt, status, remarks)
    input("Press Enter to continue...")

def manage_grades_workflow(course_code, course_name):
    """Persistent workflow for recording grades."""
    while True:
        # Pass action name to prompt correctly
        student = select_enrolled_student(course_code, f"Grade in {course_code}")
        if not student:
            break
        perform_add_grade_context(student['email'], course_code)

def manage_attendance_workflow(course_code, course_name):
    """Persistent workflow for marking attendance."""
    while True:
        student = select_enrolled_student(course_code, f"Mark Attendance in {course_code}")
        if not student:
            break
        perform_mark_attendance_context(student['email'], course_code)

def select_student_for_enrollment():
    """Interactive student selection (paginated, descending ID)."""
    offset = 0
    limit = 5
    
    # Get total count first for "Page X of Y"
    res_count = execute_query("SELECT COUNT(*) as cnt FROM students", fetch=True)
    total_items = res_count[0]['cnt'] if res_count else 0
    total_pages = math.ceil(total_items / limit)
    
    while True:
        current_page = (offset // limit) + 1
        print(f"\nScanning for students (Page {current_page} of {max(1, total_pages)})...")
        # Note: Sorting by ID DESC changes the "pages" conceptually but the count is same.
        query = f"SELECT student_id, first_name, last_name, email, rank FROM students ORDER BY student_id DESC LIMIT {limit} OFFSET {offset}"
        students = execute_query(query, fetch=True)
        
        if not students:
             print("No students found.")
             # If offset is 0 and no students, return. Else we might be at end.
             if offset == 0: return None
        else:
            print_results(students)
            
        console.print("Options:", style="bold")
        console.print(" - Enter Student ID to select")
        if current_page < total_pages:
            console.print(" - [Enter] Next Page", style="red", markup=False)
        console.print(" - [q] Back", style="red", markup=False)
        
        choice = input("Choice: ").strip()
        
        if choice.lower() == 'q':
            return None
            
        if choice == "":
            if offset + limit < total_items:
                offset += limit
            elif total_items > 0:
                offset = 0
                print("Restarting list...")
            continue
            
        try:
            sid = int(choice)
            details = get_student_details(sid)
            if details:
                return details
            else:
                print("Student not found.")
        except ValueError:
            print("Invalid input.")

# Duplicate older definition removed — using the updated `perform_manage_course` above.

def menu_course_management():
    """List courses and allow management."""
    offset = 0
    limit = 10
    
    # Get total count
    res_count = execute_query("SELECT COUNT(*) as cnt FROM courses", fetch=True)
    total_items = res_count[0]['cnt'] if res_count else 0
    total_pages = math.ceil(total_items / limit)
    
    while True:
        current_page = (offset // limit) + 1
        query = f"SELECT course_id, course_code, name, credits FROM courses ORDER BY course_id LIMIT {limit} OFFSET {offset}"
        courses = execute_query(query, fetch=True)
        
        console.print(Panel(f"Course Management (Page {current_page} of {max(1, total_pages)})", style="cyan"))
        if courses:
            tbl = Table(show_header=True, header_style="bold magenta")
            tbl.add_column("No.")
            tbl.add_column("Code", style="cyan")
            tbl.add_column("Name", style="green")
            tbl.add_column("Credits", style="yellow")
            for i, c in enumerate(courses, 1):
                tbl.add_row(str(i), c.get('course_code',''), c.get('name',''), str(c.get('credits','')))
            console.print(tbl)
        else:
            if offset == 0:
                console.print("No courses found.")
            else:
                console.print("No more courses.")

        # Show options similar to view students menu
        opts = ["Enter Number to Manage Course"]
        if current_page < total_pages:
            opts.append("[Enter] Next Page")
        opts.append("[a] Add Course")
        opts.append("[q] Back")
        console.print("Options:", style="bold")
        for opt in opts:
            console.print(f" - {opt}", style="red", markup=False)

        choice = input("Select: ").strip().lower()
        
        if choice == 'q':
            return
        elif choice == 'a':
            perform_add_course()
        elif choice == '':
            if offset + limit < total_items:
                offset += limit
            elif total_items > 0:
                 offset = 0 
                 print("Restarting list...")
            else:
                print("End of list.")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(courses):
                    perform_manage_course(courses[idx])
                else:
                    print("Invalid selection.")
            except ValueError:
                pass


def main():
    while True:
        print_header()
        options = [
            "1. Student Management",
            "2. Course Management",
            "3. Generate Reports",
            "4. Stored Procedures",
            "q. Exit",
        ]
        render_menu("Main Menu", options)
        choice = input("Select an option: ").strip().lower()
        
        if choice == '1':
            menu_student_management()
        elif choice == '2':
            menu_course_management()
        elif choice == '3':
            menu_reports()
        elif choice == '4':
            menu_stored_procedures()
        elif choice == 'q':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice, please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
