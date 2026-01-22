import sys
import math
from datetime import date
import os
from src.controllers import (
    add_student, enroll_student, record_grade, mark_attendance, 
    update_student, delete_student, get_student_id_by_email, get_student_details,
    get_students_in_course,
    get_student_enrollments, get_student_grades, get_student_attendance,
    update_grade, delete_grade, update_attendance, delete_attendance,
    get_all_courses, add_course, update_course, delete_course, unenroll_student
)
from src.database import execute_query
from src.reports import generate_roster_report, generate_attendance_report
from src.utils import get_user_input, validate_email, validate_date, validate_score

def print_header():
    print("\n" + "="*40)
    print("   ELITE DEFENSE ACADEMY DBMS")
    print("="*40)

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
        print("\n--- Student Management (CRUD) ---")
        print("1. Add Student (Create)")
        print("2. List Students (Read)")
        print("3. Update Student")
        print("4. Delete Student")
        print("q. Back")
        
        choice = input("\nSelect Option: ").strip().lower()
        
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
                
                print("\nOptions: " + " | ".join(nav_opts))
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
        print("\n--- Generate Reports ---")
        print("1. Student Roster")
        print("2. Attendance Report")
        print("q. Back")
        
        choice = input("\nSelect Report: ").strip().lower()
        
        if choice == 'q': return
        
        print("\nSelect Format:")
        print("1. CSV")
        print("2. PDF")
        
        f_choice = get_user_input("Format (1-2)")
        if f_choice is None: return
        
        if f_choice == '1':
            fmt = 'csv'
        elif f_choice == '2':
            fmt = 'pdf'
        else:
            print("Invalid selection. Defaulting to CSV.")
            fmt = 'csv'

        if choice == '1':
            generate_roster_report(fmt.lower())
        elif choice == '2':
            generate_attendance_report(fmt.lower())
        else:
            print("Invalid selection.")
            continue
        
        input("Press Enter to continue...")

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

    # Get headers
    headers = list(results[0].keys())
    
    # Calculate widths
    widths = {h: len(h) for h in headers}
    for row in results:
        for h in headers:
            val = str(row.get(h, ''))
            widths[h] = max(widths[h], len(val))
    
    # Create format string
    fmt = " | ".join([f"{{:<{widths[h]}}}" for h in headers])
    separator = "-+-".join(["-" * widths[h] for h in headers])
    
    # Print table
    print("\n" + fmt.format(*headers))
    print(separator)
    for row in results:
        values = [str(row.get(h, '')) for h in headers]
        print(fmt.format(*values))
    print(f"\n({len(results)} rows)\n")

def menu_stored_procedures():
    while True:
        print("\n--- Stored Procedures & Views ---")
        print("1. View Students in Course (05)")
        print("2. Course Average Grades (06)")
        print("3. Low Attendance Risk (07)")
        print("4. Top Student Ranking (08)")
        print("5. Enrollment Stats (09)")
        print("q. Back")
        
        choice = input("\nSelect Option: ").strip().lower()
        
        if choice == 'q': return
        
        sql_file = None
        params = None
        
        if choice == '1':
            course_code = get_user_input("Enter Course Code (e.g. TAC-101)")
            if course_code is None: continue
            
            raw_sql = get_sql_content("05_view_course_students.sql")
            if raw_sql:
                # Replace hardcoded value in file with parameter placeholder
                sql_file = raw_sql.replace("'TAC-101'", "%s")
                params = (course_code,)
                
        elif choice == '2':
            sql_file = get_sql_content("06_course_avg_grades.sql")
        elif choice == '3':
            sql_file = get_sql_content("07_low_attendance_risk.sql")
        elif choice == '4':
            sql_file = get_sql_content("08_top_student_ranking.sql")
        elif choice == '5':
            sql_file = get_sql_content("09_enrollment_stats.sql")
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
    print(f"\n{prompt_text}:")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
        
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
                print("Invalid number.")
        except ValueError:
            print("Invalid input.")

DEPARTMENTS = [
    "Tactics", "Intelligence", "Engineering", "Leadership", 
    "Weapons", "Cyber Warfare", "Logistics", "Medical", "General"
]

DIFFICULTIES = ["Basic", "Intermediate", "Advanced"]

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
        print(f"\n--- Managing Course: {ccode} - {course['name']} ---")
        print("1. View Enrolled Students")
        print("2. Enroll Student")
        print("3. Unenroll Student")
        print("4. Record Grade")
        print("5. Mark Attendance")
        print("6. Update Course Details")
        print("7. Delete Course")
        print("q. Back")
        
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
    """
    Interactively select a student enrolled in the course.
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
        
        print(f"\n--- Select Student to {prompt_action} (Page {current_page} of {total_pages}) ---")
        for i, s in enumerate(page_items, 1):
             print(f"{s['student_id']}. {s['first_name']} {s['last_name']} ({s['rank']})")
             
        print("\nOptions:")
        print(" - Enter Student ID to Select")
        if current_page < total_pages:
            print(" - [Enter] Next Page")
        if current_page > 1:
            print(" - [p] Previous Page")
        print(" - [q] Back")
        
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
        
        print(f"\n--- Enrolled Students: {course_code} (Page {current_page} of {total_pages}) ---")
        # Reuse print_results or custom format? Custom is often nicer for specific views
        # print_results(page_items) 
        # Using custom loop for consistency with other lists
        for s in page_items:
             print(f"ID: {s['student_id']} | {s['rank']} {s['first_name']} {s['last_name']} | {s['email']}")
             
        print("\nOptions:")
        if current_page < total_pages:
             print(" - [Enter] Next Page")
        
        print(" - [q] Back")
        
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
    
    print("Select Assessment Type:")
    for k, v in assessments.items():
        w_str = f" (Weight: {v['weight']})" if v['weight'] else ""
        print(f"{k}. {v['name']}{w_str}")
        
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
    
    print("Select Status:")
    for k, v in statuses.items():
        print(f"{k}. {v}")
        
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
            
        print("\nOptions:")
        print(" - Enter Student ID to select")
        if current_page < total_pages:
            print(" - [Enter] Next Page")
        print(" - [q] Back")
        
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

def perform_manage_course(course):
    """Sub-menu for a specific course."""
    cid = course['course_id']
    ccode = course['course_code']
    
    while True:
        print(f"\n--- Managing Course: {ccode} - {course['name']} ---")
        print("1. View Enrolled Students")
        print("2. Enroll Student")
        print("3. Unenroll Student")
        print("4. Record Grade")
        print("5. Mark Attendance")
        print("6. Update Course Details")
        print("7. Delete Course")
        print("q. Back")
        
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
        
        print(f"\n--- Course Management (Page {current_page} of {max(1, total_pages)}) ---")
        if courses:
            for i, c in enumerate(courses, 1):
                print(f"{i}. {c['course_code']} - {c['name']} ({c['credits']} cr)")
        else:
            if offset == 0:
                print("No courses found.")
            else:
                print("No more courses.")
        
        print("\nOptions:")
        print(" - Enter Number to Manage Course")
        if current_page < total_pages:
            print(" - [Enter] Next Page")
        print(" - [a] Add Course")
        print(" - [q] Back")
        
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
        print("1. Student Management")
        print("2. Course Management")
        print("3. Generate Reports")
        print("4. Stored Procedures")
        print("q. Exit")
        
        choice = input("\nSelect an option: ").strip().lower()
        
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
